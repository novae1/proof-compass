from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class Attempt:
    """Represents an attempt to prove a theorem or lemma."""
    success: bool
    raw_output: str
    parsed_proof: str
    message: Any
    generation_time: float
    verification_time: float

    def to_dict(self) -> dict[str, object]:
        """Convert the Attempt to a dictionary."""
        return {
            "success": self.success,
            "raw_output": self.raw_output,
            "parsed_proof": self.parsed_proof,
            "message": self.message,
            "generation_time": self.generation_time,
            "verification_time": self.verification_time,
        }

    @staticmethod
    def from_dict(attempt_dict: dict) -> Attempt:
        """Create an Attempt from a dictionary."""
        return Attempt(
            success=attempt_dict["success"],
            raw_output=attempt_dict["raw_output"],
            parsed_proof=attempt_dict["parsed_proof"],
            message=attempt_dict["message"],
            generation_time=attempt_dict["generation_time"],
            verification_time=attempt_dict["verification_time"],
        )


class TheoremProcessor:
    def __init__(
        self,
        formal_statement: str,
        header: str,
        informal_statement: str | None = None,
        nl_proof: str | None = None,
    ):
        self._formal_statement = formal_statement
        if not header or not header.strip():
            raise ValueError("TheoremProcessor.header must be a non-empty string.")
        self._header = header
        self._informal_statement = informal_statement
        self._nl_proof = nl_proof
        self._attempts: list[Attempt] = []

    @property
    def formal_statement(self) -> str:
        return self._formal_statement

    @property
    def header(self) -> str:
        return self._header

    @property
    def informal_statement(self) -> str | None:
        return self._informal_statement

    @property
    def nl_proof(self) -> str | None:
        return self._nl_proof

    def get_solution(self) -> str | None:
        for attempt in self._attempts:
            if attempt.success:
                return attempt.parsed_proof
        return None

    def add_attempt(self, attempt: Attempt) -> None:
        self._attempts.append(attempt)

    def has_solution(self) -> bool:
        return self.get_solution() is not None

    def count_attempts(self) -> int:
        return len(self._attempts)

    def to_dict(self) -> dict[str, object]:
        return {
            "formal_statement": self._formal_statement,
            "header": self._header,
            "informal_statement": self._informal_statement,
            "nl_proof": self._nl_proof,
            "attempts": [attempt.to_dict() for attempt in self._attempts],
        }

    @staticmethod
    def from_dict(processor_dict: dict) -> TheoremProcessor:
        processor = TheoremProcessor(
            formal_statement=processor_dict["formal_statement"],
            header=processor_dict["header"],
            informal_statement=processor_dict.get("informal_statement"),
            nl_proof=processor_dict.get("nl_proof"),
        )
        processor._attempts = [
            Attempt.from_dict(att) for att in processor_dict.get("attempts", [])
        ]
        return processor
