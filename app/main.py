import json
import os
from pathlib import Path
from dotenv import load_dotenv
from app.utils import *

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")
# api_key = os.getenv("OLLAMA_API_KEY")
# model = os.getenv("OLLAMA_MODEL")



def main() -> None:
    input_dir=Path("data")
    prompt=Path("app/prompt.yaml")
    result = map_claims(input_dir, prompt, GeminiLLM(api_key=api_key, model=model))
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    
    print(payload)



if __name__ == "__main__":
    main()