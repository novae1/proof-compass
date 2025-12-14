import subprocess
import json
import threading
import os
import time
import logging
from typing import Optional, Dict, Any
import psutil

# Set up logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors by default
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("lean_repl.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("lean_repl")

class ReadResponseThread(threading.Thread):
    """A thread for reading responses from the REPL process."""
    def __init__(self, process):
        super().__init__()
        self.process = process
        self.result = None
        self.stop_event = threading.Event()
        self.daemon = True  # Make thread daemon so it exits when main thread exits
        
    def run(self):
        try:
            response = b""
            while not self.stop_event.is_set():
                line = self.process.stdout.readline()  # Reading binary data
                if not line:
                    break
                    
                response += line
                try:
                    # Try to decode and parse the current accumulated output
                    decoded_response = response.decode('utf-8')
                    result = json.loads(decoded_response)
                    self.result = result
                    return
                except (UnicodeDecodeError, json.JSONDecodeError):
                    # Not yet a complete or valid JSON; continue reading
                    continue
                    
        except Exception as e:
            logger.error(f"Exception in ReadResponseThread: {str(e)}")
            
    def stop(self):
        # Stopping ReadResponseThread
        self.stop_event.set()

class LeanREPL:
    def __init__(self, project_dir: str, repl_path: str):
        """Initialize the Lean REPL process."""
        self.project_dir = project_dir
        self.repl_path = repl_path
        self.is_ready = False
        self.process = None
        self.base_env = None
        self.current_reader_thread = None
        # Initialize REPL with project dir
        self._initialize_repl()

    def _create_process(self, project_dir: str, repl_path: str) -> subprocess.Popen:
        """Create and return the REPL subprocess."""
        cmd = f'cmd /c "lake env {repl_path}"'
        logger.info(f"Creating process with command: {cmd}")
        
        process = subprocess.Popen(
            cmd,
            cwd=project_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
        
        logger.info(f"Process created with PID: {process.pid}")
        return process

    def _send_command(self, command: Dict[str, Any], timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Send a command to the REPL and wait for the parsed JSON response.
        
        If the command does not complete within the given timeout,
        kills the REPL process and marks it as not ready.
        """
        if not self.process:
            logger.error("Process not running before send_command")
            self.is_ready = False
            raise Exception("Process not running")
            
        # Check if process is still running
        if self.process.poll() is not None:
            logger.error(f"Process terminated with exit code {self.process.poll()}")
            self.is_ready = False
            raise Exception(f"Process terminated with exit code {self.process.poll()}")
            
        try:
            # Send the command to the REPL
            command_str = json.dumps(command) + "\n\n"
            self.process.stdin.write(command_str.encode('utf-8'))
            self.process.stdin.flush()

            # Create and start a reader thread
            reader = ReadResponseThread(self.process)
            self.current_reader_thread = reader
            reader.start()
            
            # Wait for the thread to complete with timeout
            # Waiting for response with timeout
            reader.join(timeout)
            
            # Check if the thread is still alive (timeout occurred)
            if reader.is_alive():
                logger.warning(f"Command timed out after {timeout}s")
                
                # Stop the thread and kill the process
                reader.stop()
                self._kill_process()
                self.is_ready = False
                
                raise TimeoutError(f"Command timed out after {timeout} seconds")
            
            # If we get here, the thread completed
            if reader.result:
                # Got valid response from process
                return reader.result
            else:
                # Thread completed but no valid response
                return None

        except TimeoutError:
            # Re-raise the timeout
            raise
        except Exception as e:
            logger.error(f"Error in _send_command: {str(e)}")
            self.is_ready = False
            raise Exception(f"Error in _send_command: {str(e)}")

    def _kill_process(self):
        """Kill the REPL process and its descendants using psutil (simplified)."""
        if not self.process or self.process.poll() is not None:
            logger.info("Kill process: No active process found or already terminated.")
            self.process = None
            return

        root_pid = self.process.pid
        logger.info(f"Attempting to kill process tree starting with PID: {root_pid}")

        try:
            parent = psutil.Process(root_pid)
            # Get children + parent process objects. Important to kill children first.
            processes = parent.children(recursive=True) + [parent]
        except psutil.NoSuchProcess:
            logger.info(f"Process {root_pid} already gone before detailed kill.")
            self.process = None
            return
        except Exception as e:
            logger.error(f"Error getting process/children for PID {root_pid}: {e}")
            self.process = None # Can't proceed if we can't get process info
            return

        # --- Phase 1: Attempt Graceful Termination ---
        logger.debug(f"Sending SIGTERM to {len(processes)} process(es) in tree (PID {root_pid}).")
        for p in processes:
            try:
                p.terminate()
            except psutil.NoSuchProcess:
                continue # Already gone
            except Exception as e:
                # Log non-critical errors during terminate attempt
                logger.warning(f"Non-fatal error terminating PID {p.pid}: {e}")

        # Brief pause to allow processes to respond to terminate
        time.sleep(0.2) # Reduced wait time

        # --- Phase 2: Force Kill Remaining Processes ---
        logger.debug(f"Sending SIGKILL to potentially remaining processes in tree (PID {root_pid}).")
        killed_count = 0
        for p in processes:
            try:
                # Check if it's still running before killing
                if p.is_running():
                    logger.warning(f"PID {p.pid} still running after SIGTERM, sending SIGKILL.")
                    p.kill()
                    killed_count += 1
            except psutil.NoSuchProcess:
                continue # Already gone
            except Exception as e:
                 # Log non-critical errors during kill attempt
                logger.warning(f"Non-fatal error killing PID {p.pid}: {e}")

        if killed_count > 0:
            logger.info(f"Force killed {killed_count} process(es) from tree (PID {root_pid}).")
        else:
            logger.info(f"Process tree (PID {root_pid}) likely terminated gracefully.")

        # Final check on the original handle
        final_poll = self.process.poll()
        if final_poll is None:
             logger.warning(f"Original process handle (PID {root_pid}) still shows as running after kill attempts.")
        else:
             logger.info(f"Original process handle (PID {root_pid}) confirmed terminated with code {final_poll}.")

        self.process = None # Clear the reference

    def _initialize_repl(self):
        """Initialize the REPL process."""
        # Initialize REPL process
        
        # If there's an existing process, kill it first
        if self.process:
            self._kill_process()
        
        try:
            self.process = self._create_process(self.project_dir, self.repl_path)
            self.base_env = self._initialize_imports()
            self.is_ready = True
            
        except Exception as e:
            self.is_ready = False
            logger.error(f"Failed to initialize REPL: {str(e)}")
            raise RuntimeError(f"Failed to initialize REPL: {str(e)}")

    def _initialize_imports(self):
        """
        Perform initial imports and return the base environment ID.
        Note: We use a slightly longer timeout for the initialization command.
        """
        imports_cmd = {
            "cmd": """
import Mathlib
import Aesop
"""
        }
        print(imports_cmd)
        
        try:
            result = self._send_command(imports_cmd, timeout=60)
            
            if result and 'env' in result:
                env_id = result['env']
                return env_id
            else:
                logger.error(f"Imports failed, result: {result}")
                raise RuntimeError("Failed to initialize imports - no environment ID")
                
        except Exception as e:
            logger.error(f"Exception during import initialization: {str(e)}")
            raise RuntimeError(f"Failed to initialize imports: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """Get current REPL status."""
        # Check if process is still running
        process_running = self.process and self.process.poll() is None
        status = {
            "ready": self.is_ready,
            "process_running": process_running
        }
        if self.process:
            status["pid"] = self.process.pid
            status["exit_code"] = self.process.poll()
            
        logger.debug(f"Status check: {status}")
        return status

    def check_theorem(self, theorem_code: str, timeout: Optional[float] = 20) -> Dict[str, Any]:
        """
        Check if a theorem is valid.

        Args:
            theorem_code: The theorem to check.
            timeout: Timeout in seconds.
        
        Returns:
            A JSON-like dictionary containing either the result or an error message.
        """
        # Starting theorem check
        
        if not self.is_ready:
            logger.warning("REPL not ready")
            return {"error": "REPL not ready"}
            
        # Check if process is still running
        if self.process.poll() is not None:
            logger.warning(f"Process not running (exit code: {self.process.poll()})")
            self.is_ready = False
            return {"error": f"REPL process not running (exit code: {self.process.poll()})"}
            
        try:
            command = {
                "cmd": theorem_code,
                "env": self.base_env
            }
            
            # Sending command
            result = self._send_command(command, timeout)
            
            if result is None:
                logger.warning("No response from REPL")
                return {"error": "No response from REPL"}
                
            # Theorem check completed successfully
            return result
            
        except TimeoutError as te:
            logger.warning(f"Timeout error: {str(te)}")
            return {"error": str(te)}
        except Exception as e:
            logger.error(f"Exception in check_theorem: {str(e)}")
            self.is_ready = False
            return {"error": str(e)}
    
    def shutdown(self):
        """Shutdown the REPL cleanly."""
        if self.current_reader_thread and self.current_reader_thread.is_alive():
            self.current_reader_thread.stop()
            
        self._kill_process()
        self.is_ready = False
