from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.investigation_agent import investigate_payment_failures
from app.agents.sql_agent import run_data_agent
from app.analytics.evidence import build_failure_evidence
from app.analytics.guardrails import validate_investigation_response
from app.tools.approval_tools import request_human_approval
from app.tools.incident_tools import create_incident
from app.tools.knowledge_tools import retrieve_operational_knowledge
from app.tools.report_tools import generate_incident_report


class InvestigationState(TypedDict):
    question: str
    evidence: dict
    operational_knowledge: dict
    investigation: str
    validation: dict
    retry_count: int
    report: dict
    approval_status: str
    approval: dict
    incident: dict


def data_node(state: InvestigationState) -> InvestigationState:
    data_result = run_data_agent(state["question"])

    return {
        "question": state["question"],
        "evidence": data_result["evidence"],
        "operational_knowledge": state["operational_knowledge"],
        "investigation": "",
        "validation": {},
        "retry_count": state["retry_count"],
        "report": {},
        "approval_status": state["approval_status"],
        "approval": {},
        "incident": {},
    }


def knowledge_node(state: InvestigationState) -> InvestigationState:
    failure_reasons = state["evidence"].get(
        "failure_reasons",
        {},
    )

    observed_failure_codes = ", ".join(
        failure_reasons.keys()
    )

    knowledge_query = (
        "Provide operational definitions and investigation guidance "
        f"for these observed payment failure codes: "
        f"{observed_failure_codes}"
    )

    knowledge_result = retrieve_operational_knowledge(
        knowledge_query,
        top_k=4,
    )

    return {
        "question": state["question"],
        "evidence": state["evidence"],
        "operational_knowledge": knowledge_result,
        "investigation": "",
        "validation": {},
        "retry_count": state["retry_count"],
        "report": {},
        "approval_status": state["approval_status"],
        "approval": state["approval"],
        "incident": state["incident"],
    }


def investigation_node(state: InvestigationState) -> InvestigationState:
    verified_evidence = build_failure_evidence(
        state["evidence"]
    )

    result = investigate_payment_failures(
        verified_evidence,
        operational_knowledge=state["operational_knowledge"],
        validation_errors=state["validation"].get("errors"),
    )

    return {
        "question": state["question"],
        "evidence": verified_evidence,
        "operational_knowledge": state["operational_knowledge"],
        "investigation": result,
        "validation": state["validation"],
        "retry_count": state["retry_count"],
        "report": {},
        "approval_status": state["approval_status"],
        "approval": state["approval"],
        "incident": state["incident"],
    }


def validation_node(state: InvestigationState) -> InvestigationState:
    validation = validate_investigation_response(
        state["investigation"],
        state["evidence"],
    )

    return {
        "question": state["question"],
        "evidence": state["evidence"],
        "operational_knowledge": state["operational_knowledge"],
        "investigation": state["investigation"],
        "validation": validation,
        "retry_count": state["retry_count"],
        "report": {},
        "approval_status": state["approval_status"],
        "approval": state["approval"],
        "incident": state["incident"],
    }


def retry_node(state: InvestigationState) -> InvestigationState:
    return {
        "question": state["question"],
        "evidence": state["evidence"],
        "operational_knowledge": state["operational_knowledge"],
        "investigation": state["investigation"],
        "validation": state["validation"],
        "retry_count": state["retry_count"] + 1,
        "report": {},
        "approval_status": state["approval_status"],
        "approval": state["approval"],
        "incident": state["incident"],
    }


def report_node(state: InvestigationState) -> InvestigationState:
    report = generate_incident_report(
        question=state["question"],
        investigation=state["investigation"],
        evidence=state["evidence"],
    )

    return {
        "question": state["question"],
        "evidence": state["evidence"],
        "operational_knowledge": state["operational_knowledge"],
        "investigation": state["investigation"],
        "validation": state["validation"],
        "retry_count": state["retry_count"],
        "report": report,
        "approval_status": state["approval_status"],
        "approval": {},
        "incident": {},
    }


def approval_node(state: InvestigationState) -> InvestigationState:
    approval = request_human_approval(
        report=state["report"],
        decision=state["approval_status"],
    )

    return {
        "question": state["question"],
        "evidence": state["evidence"],
        "operational_knowledge": state["operational_knowledge"],
        "investigation": state["investigation"],
        "validation": state["validation"],
        "retry_count": state["retry_count"],
        "report": state["report"],
        "approval_status": state["approval_status"],
        "approval": approval,
        "incident": {},
    }


def incident_node(state: InvestigationState) -> InvestigationState:
    incident = create_incident(
        report=state["report"],
        approval=state["approval"],
    )

    return {
        "question": state["question"],
        "evidence": state["evidence"],
        "operational_knowledge": state["operational_knowledge"],
        "investigation": state["investigation"],
        "validation": state["validation"],
        "retry_count": state["retry_count"],
        "report": state["report"],
        "approval_status": state["approval_status"],
        "approval": state["approval"],
        "incident": incident,
    }


def route_after_validation(state: InvestigationState) -> str:
    if state["validation"].get("valid") is True:
        return "report"

    if state["retry_count"] < 1:
        return "retry"

    return "end"


builder = StateGraph(InvestigationState)

builder.add_node("data", data_node)
builder.add_node("knowledge", knowledge_node)
builder.add_node("investigation", investigation_node)
builder.add_node("validation", validation_node)
builder.add_node("retry", retry_node)
builder.add_node("report", report_node)
builder.add_node("approval", approval_node)
builder.add_node("incident", incident_node)

builder.add_edge(START, "data")
builder.add_edge("data", "knowledge")
builder.add_edge("knowledge", "investigation")
builder.add_edge("investigation", "validation")

builder.add_conditional_edges(
    "validation",
    route_after_validation,
    {
        "retry": "retry",
        "report": "report",
        "end": END,
    },
)

builder.add_edge("retry", "investigation")
builder.add_edge("report", "approval")
builder.add_edge("approval", "incident")
builder.add_edge("incident", END)

graph = builder.compile()
