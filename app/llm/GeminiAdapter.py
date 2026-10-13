from google import genai
from app.DataModel import Claim


class GeminiLLM:
    def __init__(self, api_key: str, model: str ):
        if not api_key:
            raise ValueError("Api key is required")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def extract_claim(self, system_prompt: str, intake_note: str) -> Claim:
        interaction = self.client.interactions.create(
            model=self.model,
            input=f"{system_prompt}\n\n<intake_note>{intake_note}</intake_note>",
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": Claim.model_json_schema()
            },
        )
        return Claim.model_validate_json(self._json_payload(interaction.output_text))

    @staticmethod
    def _json_payload(output_text: str) -> str:
        """Accept JSON returned directly or inside a Markdown code fence."""
        payload = output_text.strip()
        if payload.startswith("```") and payload.endswith("```"):
            first_newline = payload.find("\n")
            if first_newline == -1:
                raise ValueError("Gemini returned an empty Markdown code fence")
            payload = payload[first_newline + 1 : -3].strip()
        return payload
