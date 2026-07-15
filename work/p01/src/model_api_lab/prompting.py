from __future__ import annotations

from model_api_lab.models import Incident

SYSTEM_INSTRUCTIONS = """You write short internal incident-digest summaries for on-call
engineers and leadership. For the incident report you are given:

1. Identify the affected system or workflow.
2. State the confirmed impact and scope.
3. State the confirmed cause and mitigation, but only if the report states
   them.
4. Do not add a cause, impact, or resolution that the report does not state.
5. Clearly mark anything uncertain or unconfirmed as uncertain. Do not
   state a guess as a settled fact.
6. Keep the summary to 2-3 sentences."""


def user_prompt(incident: Incident) -> str:
    return f"Summarize this incident report:\n\n{incident.report}"
