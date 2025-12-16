from __future__ import annotations

from .http_client import LeanHTTPClient

def check_repl_status(server_client: LeanHTTPClient) -> tuple[bool, str]:
    if server_client is None:
        return False, "Server client is None"

    success, status = server_client.get_status()
    if not success:
        return False, "Failed to get server status"
    if not status["ready"]:
        print("REPL not ready, reinitializing...")
        success, status = server_client.reinitialize_repl()
        if not success:
            return False, "Failed to reinitialize REPL"
    return True, "REPL is ready"


def _looks_like_full_lean_file(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("import ") or stripped.startswith("set_option ")


def check_proof(
    proof,
    server_client: LeanHTTPClient,
    timeout=20,
    ignore_sorries=False,
    header="",
) -> tuple[bool, object]:
    # basic checking before actually checking the proof
    if server_client is None:
        return False, "Server client is None"

    if not proof or not str(proof).strip():
        return False, "Proof provided was an empty string (probably a generation error)"

    if not header or not str(header).strip():
        return False, "A non-empty header is required for proof checking."

    success, message = check_repl_status(server_client)
    if not success:
        return False, message

    proof_text = str(proof).strip()
    header_text = str(header).rstrip()

    proof_with_header = proof_text if _looks_like_full_lean_file(proof_text) else f"{header_text}\n\n{proof_text}"
    success, response = server_client.check_theorem(proof_with_header, timeout)

    # evaluating the response
    if not success:
        return False, response

    if not ignore_sorries and "sorries" in response:
        return False, "Proof contains sorries"

    if "messages" in response:
        for msg in response["messages"]:
            if msg["severity"] == "error":
                return False, response["messages"]
    return True, "Proof verified successfully"
