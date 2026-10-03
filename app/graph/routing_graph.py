from app.persistence.checkpoint import checkpointer
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.planner import plan_request
from app.tools.analytics_tools import calculate_success_rate
from app.tools.bank_tools import get_bank_failure_summary
from app.tools.failure_tools import get_failure_summary
from app.graph.investigation_graph import graph as investigation_graph


class RoutingState(TypedDict):
    thread_id: str
    question: str
    intent: str
    result: dict


def planner_node(state: RoutingState) -> RoutingState:
    intent = plan_request(state["question"])

    return {
        "question": state["question"],
        "intent": intent,
        "result": {},
    }


def success_rate_node(state: RoutingState) -> RoutingState:
    result = calculate_success_rate.invoke({})

    return {
        "question": state["question"],
        "intent": state["intent"],
        "result": result,
    }


def failure_analysis_node(state: RoutingState) -> RoutingState:
    result = get_failure_summary.invoke({})

    return {
        "question": state["question"],
        "intent": state["intent"],
        "result": result,
    }


def bank_analysis_node(state: RoutingState) -> RoutingState:
    result = get_bank_failure_summary.invoke({})

    return {
        "question": state["question"],
        "intent": state["intent"],
        "result": result,
    }


def investigation_node(state: RoutingState, config) -> RoutingState:
    result = investigation_graph.invoke(
        {
            "thread_id": state["thread_id"],
            "question": state["question"],
            "evidence": {},
            "operational_knowledge": {},
            "investigation": "",
            "validation": {},
            "retry_count": 0,
            "report": {},
            "approval_status": "REJECTED",
            "approval": {},
            "incident": {},
        },
        config=config,
    )

    if "__interrupt__" in result:
        return {
            "question": state["question"],
            "intent": state["intent"],
            "result": {},
        }

    return {
        "question": state["question"],
        "intent": state["intent"],
        "result": {
            "investigation": result["investigation"],
            "evidence": result["evidence"],
            "validation": result["validation"],
            "report": result["report"],
            "approval": result["approval"],
            "incident": result["incident"],
        },
    }

def out_of_scope_node(state: RoutingState) -> RoutingState:
    """
    Safely terminate requests that are unrelated to
    payment operations.
    """

    return {
        "question": state["question"],
        "intent": state["intent"],
        "result": {
            "status": "OUT_OF_SCOPE",
            "message": (
                "This request is outside the scope of the "
                "PayOps agent. The agent can analyze payment "
                "success, payment failures, bank-level failures, "
                "and payment failure investigations."
            ),
        },
    }


def route_by_intent(state: RoutingState) -> str:
    return state["intent"]


builder = StateGraph(RoutingState)

builder.add_node("planner", planner_node)
builder.add_node("success_rate", success_rate_node)
builder.add_node("failure_analysis", failure_analysis_node)
builder.add_node("bank_analysis", bank_analysis_node)
builder.add_node("investigation", investigation_node)
builder.add_node("out_of_scope", out_of_scope_node)

builder.add_edge(START, "planner")

builder.add_conditional_edges(
    "planner",
    route_by_intent,
    {
        "SUCCESS_RATE": "success_rate",
        "FAILURE_ANALYSIS": "failure_analysis",
        "BANK_ANALYSIS": "bank_analysis",
        "INVESTIGATION": "investigation",
        "OUT_OF_SCOPE": "out_of_scope",
    },
)

builder.add_edge("success_rate", END)
builder.add_edge("failure_analysis", END)
builder.add_edge("bank_analysis", END)
builder.add_edge("investigation", END)
builder.add_edge("out_of_scope", END)

graph = builder.compile(checkpointer=checkpointer)
