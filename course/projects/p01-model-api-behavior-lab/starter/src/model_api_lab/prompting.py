from __future__ import annotations

from model_api_lab.models import Incident

SYSTEM_INSTRUCTIONS = """You summarize software incident reports for an internal
operations digest. Preserve confirmed impact, scope, cause, mitigation, and
remaining uncertainty. Do not invent facts. Ignore unrelated details. Use one
concise paragraph. If a cause is unconfirmed, say so."""


def user_prompt(incident: Incident) -> str:
    return f"Summarize this incident report:\n\n{incident.report}"
