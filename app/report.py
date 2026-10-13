from html import escape


def render_report_html(claims: list[dict]) -> str:
    """Render extracted claims and review issues as a simple human-review draft."""
    field_labels = {
        key: key.replace("_", " ").title()
        for key in (
            "claimant_full_name",
            "date_of_birth",
            "address",
            "email",
            "accident_date",
            "accident_time",
            "accident_location",
            "claimant_role",
            "claimant_vehicle_registration",
            "other_vehicle_registration",
            "injury_description",
            "other_insurer_name",
        )
    }
    claim_sections = []

    for item in claims:
        rows = []
        issues = []
        for field_name, field in item["claim"].items():
            value = field.get("value")
            reported_versions = field.get("reported_versions") or []
            if reported_versions:
                issues.append(f"{field_labels[field_name]} has conflicting reported values.")
            elif value is None:
                issues.append(f"{field_labels[field_name]} is missing or unresolved.")

            evidence = field.get("evidence") or "None recorded"
            note = field.get("note") or ""
            if field_name == "other_insurer_name" and value is None:
                insurer_note = (
                    "Unknown insurer details do not establish that the vehicle was uninsured."
                )
                note = f"{note} {insurer_note}".strip()

            evidence_markup = escape(evidence)
            if reported_versions:
                versions_markup = "".join(
                    "<li>"
                    f"<strong>{escape(str(version.get('value')))}</strong>: "
                    f"{escape(version.get('evidence') or 'None recorded')}"
                    "</li>"
                    for version in reported_versions
                )
                evidence_markup += (
                    "<br><strong>Reported versions:</strong>"
                    f"<ul>{versions_markup}</ul>"
                )
            rows.append(
                "<tr>"
                f"<th scope=\"row\">{escape(field_labels[field_name])}</th>"
                f"<td>{escape(str(value)) if value is not None else '<em>Not resolved</em>'}</td>"
                f"<td>{evidence_markup}</td>"
                f"<td>{escape(note)}</td>"
                "</tr>"
            )

        issue_markup = (
            "<ul>" + "".join(f"<li>{escape(issue)}</li>" for issue in issues) + "</ul>"
            if issues
            else "<p class=\"clear\">No missing or conflicting fields detected.</p>"
        )
        claim_sections.append(
            f"""
            <section class="claim">
              <h2>Source: {escape(item["source_file"])}</h2>
              <h3>Outstanding issues</h3>
              {issue_markup}
              <table>
                <thead><tr><th>Field</th><th>Extracted value</th><th>Evidence</th><th>Note</th></tr></thead>
                <tbody>{''.join(rows)}</tbody>
              </table>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Claim extraction review draft</title>
  <style>
    body {{ font: 16px/1.45 system-ui, sans-serif; color: #222; margin: 2rem auto; max-width: 1100px; padding: 0 1rem; }}
    .warning {{ background: #fff3cd; border: 3px solid #b45309; color: #7c2d12; padding: 1rem; font-weight: 700; }}
    .claim {{ margin-top: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #bbb; padding: .5rem; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .claim h3 {{ color: #991b1b; }}
    .clear {{ color: #166534; }}
  </style>
</head>
<body>
  <h1>Claim extraction review draft</h1>
  <p class="warning">DRAFT — HUMAN REVIEW REQUIRED — NOT FOR SUBMISSION.
  A human must verify every value against the source note and resolve all outstanding issues
  before use.</p>
  {''.join(claim_sections)}
</body>
</html>
"""
