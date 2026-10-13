
from ollama import Client

from application.DataModel import Claim


class OllamaLLM:
    def __init__(self, model: str, host: str = "http://localhost:11434",):
        self.client = Client(host=host)
        self.model = model

    def extract_claim(self, system_prompt: str, intake_note: str,) -> Claim:
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        "Extract the claim from this intake note:\n"
                        f"<intake_note>{intake_note}</intake_note>"
                    ),
                },
            ],
            format=Claim.model_json_schema(),
            options={"temperature": 0},
        )

        output_text = response.message.content

        return Claim.model_validate_json(output_text)
