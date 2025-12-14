from __future__ import annotations

from .http_client import LeanHTTPClient

def check_repl_status(server_client: LeanHTTPClient) -> tuple[bool, str]:
	if server_client is None:
		return False, "Server client is None"
	
	success, status = server_client.get_status()
	if not success:
		return False, "Failed to get server status"
	elif not status['ready']:
		print("REPL not ready, reinitializing...")
		success, status = server_client.reinitialize_repl()
		if not success:
			return False, "Failed to reinitialize REPL"
	return True, "REPL is ready"


def check_proof(proof, server_client: LeanHTTPClient, timeout=20, ignore_sorries=False, header="") -> tuple[bool, str]:
	# basic checking before actually checking the proof
	if server_client is None:
		return False, "Server client is None"
	
	if not proof:
		return False, "Proof provided was an empty string (probably a generation error)"

	success, message = check_repl_status(server_client)
	if not success:
		return False, message
		
	# actual checking of the proof
	if not header:
		header = "\nset_option maxHeartbeats 0\n\nopen BigOperators Real Nat Topology Rat\n"
	else:
		# Remove "import Mathlib" from header
		header = header[14:] # I should improve the logic here
	proof_with_header = header + '\n' + proof
	success, response = server_client.check_theorem(proof_with_header, timeout)

	# evaluating the response
	if not success:
		return False, response
		
	if not ignore_sorries:
		if 'sorries' in response:
			return False, "Proof contains sorries"

	correct = True
	if 'messages' in response:
		for msg in response['messages']:
			if msg['severity'] == 'error':
				correct = False
				return False, response['messages']
	if correct:
		return True, "Proof verified successfully"
