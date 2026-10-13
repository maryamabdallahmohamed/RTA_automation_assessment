"""Gradio interface for the fictional CNF claim-intake assessment."""
import json
import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import gradio as gr
from dotenv import load_dotenv

from application.llm.GeminiAdapter import GeminiLLM
from application.report import render_report_html
from application.utils import map_claims


load_dotenv()

LOGGER = logging.getLogger("gradio.app")
PROJECT_ROOT = Path(__file__).resolve().parent
PROMPT_PATH = PROJECT_ROOT / "application" / "prompt.yaml"
SAFETY_LABEL = "DRAFT — HUMAN REVIEW REQUIRED — NOT FOR SUBMISSION"


def _sample_cases() -> list[tuple[str, str]]:
    """Return available fictional notes without reading user input as a path."""
    data_dir = PROJECT_ROOT / "data"
    if not data_dir.is_dir():
        return []
    return [
        (path.name, path.read_text(encoding="utf-8"))
        for path in sorted(data_dir.glob("*.txt"))
    ]


def _format_issues(result: list[dict]) -> str:
    """Summarize unresolved fields while retaining all reported conflict evidence."""
    lines = ["### Missing, conflicting, and validation issues"]
    issue_count = 0
    for item in result:
        lines.append(f"\n**Source: `{item['source_file']}`**")
        for field_name, field in item["claim"].items():
            versions = field.get("reported_versions") or []
            if versions:
                issue_count += 1
                lines.append(f"- **{field_name} — conflicting values:**")
                for version in versions:
                    lines.append(
                        f"  - `{version.get('value')}` — evidence: "
                        f"{version.get('evidence') or 'None recorded'}"
                    )
            elif field.get("value") is None:
                issue_count += 1
                evidence = field.get("evidence") or "None recorded"
                lines.append(f"- **{field_name} — missing or unresolved:** evidence: {evidence}")

    if issue_count == 0:
        lines.append("\nNo missing or conflicting fields were detected. Human review is still required.")
    return "\n".join(lines)


def _error_outputs(message: str) -> tuple[str, str, str, str]:
    return (
        "",
        "",
        "### Processing error\n\n" + message,
        f"**{SAFETY_LABEL}**\n\nThe note was not processed.",
    )


def process_note(note: str) -> tuple[str, str, str, str]:
    """Process one note through the existing extraction and reporting pipeline."""
    if not note or not note.strip():
        return _error_outputs("Enter a fictional intake note before submitting.")

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")
    if not api_key:
        return _error_outputs(
            "GEMINI_API_KEY is not configured. Add it as an environment variable "
            "or Hugging Face Space Secret."
        )
    if not model:
        return _error_outputs(
            "GEMINI_MODEL is not configured. Add it as an environment variable "
            "or Hugging Face Space Secret."
        )

    try:
        with TemporaryDirectory(prefix="cnf-claim-") as temporary_directory:
            input_path = Path(temporary_directory) / "intake_note.txt"
            input_path.write_text(note, encoding="utf-8")
            result = map_claims(input_path.parent, PROMPT_PATH, GeminiLLM(api_key, model))
    except Exception:
        LOGGER.exception("Claim-intake processing failed")
        return _error_outputs(
            "The assessment could not be completed. Check the model configuration "
            "and try again. No claim was submitted."
        )

    payload = json.dumps(result, indent=2, ensure_ascii=False)
    return payload, render_report_html(result), _format_issues(result), f"**{SAFETY_LABEL}**"


def _load_sample(selected_case: str | None) -> str:
    if not selected_case:
        return ""
    for filename, note in _sample_cases():
        if filename == selected_case:
            return note
    return ""


def build_demo() -> gr.Blocks:
    sample_names = [filename for filename, _ in _sample_cases()]
    with gr.Blocks(title="CNF Claim Intake Assessment") as demo:
        gr.Markdown(
            f"# CNF Claim Intake Assessment\n\n"
            f"**{SAFETY_LABEL}**\n\n"
            "Use fictional assessment data only. Verify every extracted value against "
            "the source note; this tool does not assess liability or submit claims."
        )
        with gr.Row():
            with gr.Column():
                sample_case = gr.Dropdown(
                    choices=sample_names,
                    label="Sample case",
                    info="Optional: choose a .txt fixture from data/.",
                    interactive=bool(sample_names),
                )
                intake_note = gr.Textbox(
                    label="Intake note",
                    placeholder="Paste a fictional claimant intake note here.",
                    lines=14,
                )
                submit = gr.Button("Assess note", variant="primary")
            with gr.Column():
                status = gr.Markdown(f"**{SAFETY_LABEL}**")
                issues = gr.Markdown(label="Review issues")

        with gr.Tab("Structured JSON"):
            structured_json = gr.Code(label="Extracted claim", language="json")
        with gr.Tab("Human-readable draft report"):
            report = gr.HTML()

        sample_case.change(_load_sample, inputs=sample_case, outputs=intake_note)
        submit.click(
            process_note,
            inputs=intake_note,
            outputs=[structured_json, report, issues, status],
        )
    return demo




if __name__ == "__main__":
    demo = build_demo()
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),                 
        share=True)
    