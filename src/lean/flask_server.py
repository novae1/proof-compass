from flask import Flask, request, jsonify
import os
import logging
import json

from .sync_lean_repl import LeanREPL

# Set up logging
logging.basicConfig(
	level=logging.WARNING,  # Only show warnings and errors by default
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	handlers=[
		logging.FileHandler("lean_server.log"),
		logging.StreamHandler()
	]
)
logger = logging.getLogger("lean_server")

app = Flask(__name__)
repl = None

def initialize_repl():
	"""Initialize the Lean REPL process."""
	global repl
	try:
		if repl is not None:
			# Ensure old process is killed before initializing a new one
			try:
				repl.shutdown()
			except Exception as e:
				logger.error(f"Error shutting down existing REPL: {str(e)}")

		project_dir = r"C:\Users\novae\Documents\lean_test"
		repl_path = r"C:\Users\novae\Documents\repl\.lake\build\bin\repl"
		
		repl = LeanREPL(project_dir, repl_path)
		
		return {"status": "success", "message": "REPL initialized successfully"}
	except Exception as e:
		logger.error(f"Failed to initialize REPL: {str(e)}")
		return {"status": "error", "message": f"Failed to initialize REPL: {str(e)}"}

@app.route('/status', methods=['GET'])
def get_status():
	"""Endpoint to check REPL status."""
	if not repl:
		return jsonify({"status": "not_initialized", "ready": False}), 200
		
	try:
		status = repl.get_status()
		return jsonify(status), 200
	except Exception as e:
		logger.error(f"Error getting REPL status: {str(e)}")
		return jsonify({"status": "error", "message": str(e), "ready": False}), 500

@app.route('/verify', methods=['POST'])
def verify_theorem():
	"""Endpoint to verify theorems."""
	if not repl:
		return jsonify({"status": "error", "message": "REPL not initialized"}), 503
		
	if not repl.is_ready:
		return jsonify({"status": "error", "message": "REPL not ready"}), 503
		
	try:
		data = request.json
		theorem = data.get('theorem')
		timeout = data.get('timeout', 20)  # Default 20 second timeout
		
		if not theorem:
			return jsonify({"status": "error", "message": "No theorem provided"}), 400
		
		# Verify theorem with timeout
		result = repl.check_theorem(theorem, timeout)
		
		# If the check_theorem method indicates the REPL is not ready anymore,
		# include that in the response for the client to act on
		if "error" in result and not repl.is_ready:
			result["status"] = "error"
			result["repl_ready"] = False
			return jsonify(result), 200
		
		return jsonify(result), 200
		
	except Exception as e:
		logger.error(f"Error in verify_theorem: {str(e)}")
		return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/reinitialize', methods=['POST'])
def reinitialize_repl():
	"""Endpoint to explicitly reinitialize the REPL."""
	# Reinitialize REPL
	result = initialize_repl()
		
	if result["status"] == "success":
		return jsonify(result), 200
	else:
		return jsonify(result), 500

@app.route('/save_file', methods=['POST'])
def save_file():
    """
    Endpoint to save a file's content.
    If a file with the same name exists, it appends a number like (1), (2), etc.
    This endpoint is completely independent of the Lean REPL.
    """
    try:
        data = request.json
        filename = data.get('filename')
        content_obj = data.get('content') 

        if not filename or content_obj is None:
            return jsonify({"status": "error", "message": "Filename and content are required"}), 400

        # --- SECURITY: Sanitize the filename ---
        from werkzeug.utils import secure_filename
        safe_filename = secure_filename(filename)
        if not safe_filename:
                return jsonify({"status": "error", "message": "Invalid filename"}), 400

        # --- Define the save directory ---
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        os.makedirs(save_dir, exist_ok=True)
        
        # --- NEW: Check for filename conflicts and find a unique name ---
        destination_path = os.path.join(save_dir, safe_filename)
        
        # If the file already exists, start looking for a new name
        if os.path.exists(destination_path):
            # Split the filename into its name and extension (e.g., 'file', '.txt')
            name, ext = os.path.splitext(safe_filename)
            count = 1
            # Loop until we find a name that is not taken
            while True:
                new_filename = f"{name}({count}){ext}"
                new_path = os.path.join(save_dir, new_filename)
                if not os.path.exists(new_path):
                    destination_path = new_path  # We found a free name
                    break
                count += 1
        # --- END of new logic ---

        # --- Write the file using the final, unique destination_path ---
        with open(destination_path, 'w', encoding='utf-8') as f:
            json.dump(content_obj, f, indent=4)

        # Return the final filename used, so the client knows what it was saved as
        final_filename = os.path.basename(destination_path)
        return jsonify({
            "status": "success", 
            "message": f"File saved as {final_filename}"
        }), 200

    except Exception as e:
        logger.error(f"Error in save_file: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
	
def start_server():
	port = input("\nEnter the desired port number (default 1347): ")
	port = int(port) if port else 1347
	"""Initialize the REPL and start the Flask server."""
	initialize_repl()
	app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
	start_server()
