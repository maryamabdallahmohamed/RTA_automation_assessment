# Claim Review Handover

## Run

Run `uv sync`, set `GEMINI_API_KEY` and `GEMINI_MODEL` in the environment (or `.env`), then run:

```bash
uv run python -m app.main
```

This reads `.txt` files from `data/`, prints claim JSON, and writes `claim_review_draft.html`.

## Assumptions

The model returns the twelve fields in `app/DataModel.py`; missing or conflicting values remain unresolved. The HTML is a review draft, not a submit-ready form.

Since the data given are examples,they were posted in the repo. Future data or claims should not be availble publically.

## AI assistance

AI assistance was used for:

    1- Prompt refinement for structured claim extraction.

    2- Development and debugging of the HTML rendering logic.

    3- Troubleshooting Hugging Face deployment issues encountered during demo preparation.

    4- Developing and debugging the LLM adapter to support Gemini and local-model inference.

The implementation, integration, and final design decisions were reviewed against the actual codebase before handover and Hugging Face Deployment.
## Time and next improvement

Actual time spent: approximately 2 hours. The work involved more than selecting an extraction prompt. It also required considering inference-platform trade-offs, model suitability, integration requirements, and the availability of a local inference option for privacy-sensitive claimant information.

Next improvment would be adding guardrails for the module this is technically important as well as model monitering.

I would evolve this prototype into a persistent review application where claims, extracted fields, unresolved issues, and reviewer corrections are stored and managed throughout the claim process. Reviewers would be able to resume reviews, resolve missing or conflicting information,  generate updated claim drafts based on verified corrections , and automate filling claim/legal templates. All automated using Human in the loop to ensure reliability and automating the process.

