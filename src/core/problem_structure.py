from __future__ import annotations
from dataclasses import dataclass

DEFAULT_HEADER = """import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

"""

@dataclass
class Attempt:
    """Represents an attempt to prove a theorem or lemma."""
    success: bool
    raw_output: str
    parsed_proof: str
    message: list
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
        header: str | None = None,
        informal_statement: str | None = None,
    ):
        self._formal_statement = formal_statement
        self._header = header
        self._informal_statement = informal_statement
        self._attempts: list[Attempt] = []
        self._solution: str | None = None

    @property
    def formal_statement(self) -> str:
        return self._formal_statement

    @property
    def header(self) -> str:
        return self._header or DEFAULT_HEADER

    @property
    def informal_statement(self) -> str | None:
        return self._informal_statement

    @property
    def solution(self) -> str | None:
        return self._solution

    def add_attempt(self, attempt: Attempt) -> None:
        self._attempts.append(attempt)
        if attempt.success:
            self._solution = attempt.parsed_proof

    def add_solution(self, solution: str) -> None:
        self._solution = solution

    def has_solution(self) -> bool:
        return self._solution is not None

    def count_attempts(self) -> int:
        return len(self._attempts)

    def to_dict(self) -> dict[str, object]:
        return {
            "formal_statement": self._formal_statement,
            "header": self._header,
            "informal_statement": self._informal_statement,
            "attempts": [attempt.to_dict() for attempt in self._attempts],
            "solution": self._solution,
        }

    @staticmethod
    def from_dict(processor_dict: dict) -> TheoremProcessor:
        processor = TheoremProcessor(
            formal_statement=processor_dict["formal_statement"],
            header=processor_dict.get("header"),
            informal_statement=processor_dict.get("informal_statement"),
        )
        processor._attempts = [
            Attempt.from_dict(att) for att in processor_dict.get("attempts", [])
        ]
        processor._solution = processor_dict.get("solution")
        return processor
