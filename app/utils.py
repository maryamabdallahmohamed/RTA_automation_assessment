from pathlib import Path
import yaml
from app.llm.GeminiAdapter import GeminiLLM
from app.llm.OllamaAdapter import OllamaLLM
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("utils")

def get_all_files(directory: str | Path) -> list[Path]:
    directory_path = Path(directory)
    return sorted(
        path for path in directory_path.iterdir() if path.is_file() and path.suffix == ".txt"
    )


def load_prompt(path: str | Path) -> str:
    prompt_path = Path(path)
    with prompt_path.open(encoding="utf-8") as prompt_file:
        prompt = yaml.safe_load(prompt_file)
    if not isinstance(prompt, dict) or not isinstance(prompt.get("SystemPrompt"), str):
        raise ValueError(f"{prompt_path} must define a SystemPrompt string")
    logger.info(f"Loaded system prompt from {prompt_path}")
    return prompt["SystemPrompt"]


def map_claims(input_dir: str | Path, prompt_path: str | Path, llm : GeminiLLM | OllamaLLM) -> list[dict]:
    system_prompt = load_prompt(prompt_path)
    claims = []
    for file_path in get_all_files(input_dir):
        claim = llm.extract_claim(system_prompt, file_path.read_text(encoding="utf-8"))
        claims.append({"source_file": file_path.name, "claim": claim.model_dump()})
        logger.info(f"Processed claim from {file_path.name}")
    return claims