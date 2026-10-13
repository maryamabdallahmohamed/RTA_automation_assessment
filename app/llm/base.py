
from typing import Protocol
from app.DataModel import Claim


class ClaimExtractor(Protocol):
    def extract_claim( self, system_prompt: str, intake_note: str,) -> Claim:
        ...
