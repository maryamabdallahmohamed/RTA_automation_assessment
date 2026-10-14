from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from application.llm.base import ClaimExtractor
from application.DataModel import Claim  

load_dotenv()


class OllamaLLM(ClaimExtractor):
    def __init__(self,api_key: str = None, model: str = None):
        api_key = api_key
        base_url = 'https://api.ollama.com'
        model= model

        self.llm = ChatOllama(
            model=model,
            temperature=0.0,
            base_url=base_url,
            client_kwargs={
                "headers": (
                    {"Authorization": f"Bearer {api_key}"}
                )
            },
        )

    def extract_claim(self, system_prompt: str, intake_note: str,) -> Claim:
        response = self.llm.invoke(
            f"{system_prompt}\n\n"
            f"<intake_note>\n{intake_note}\n</intake_note>"
        )

        content = response.content

        if not isinstance(content, str):
            raise ValueError("Ollama returned non-text content.")

        return Claim.model_validate_json(content)