from typing import Literal

from langchain_ollama import ChatOllama

from app.config.settings import LLM_MODEL, LLM_TEMPERATURE


Intent = Literal[
    "SUCCESS_RATE",
    "FAILURE_ANALYSIS",
    "BANK_ANALYSIS",
    "INVESTIGATION",
    "OUT_OF_SCOPE",
]


llm = ChatOllama(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
)


def _rule_based_intent(question: str) -> Intent | None:
    """
    Detect obvious operational intents using deterministic rules.

    Returns None when the request is not clearly identifiable
    from deterministic rules and should be evaluated by the LLM.
    """

    text = question.lower()

    bank_keywords = [
        "bank",
        "sender bank",
        "receiver bank",
        "which bank",
        "banks",
    ]

    success_keywords = [
        "success rate",
        "successful transactions",
        "how many succeeded",
        "success percentage",
    ]

    failure_keywords = [
        "why are payments failing",
        "payment failures",
        "failed payments",
        "failure reason",
        "failure reasons",
        "why did payments fail",
        "timeouts",
        "bank errors",
    ]

    investigation_keywords = [
        "investigate",
        "investigation",
        "root cause",
        "root-cause",
        "what should we investigate",
        "analyze why",
        "perform an investigation",
    ]

    if any(keyword in text for keyword in bank_keywords):
        return "BANK_ANALYSIS"

    if any(keyword in text for keyword in success_keywords):
        return "SUCCESS_RATE"

    if any(keyword in text for keyword in investigation_keywords):
        return "INVESTIGATION"

    if any(keyword in text for keyword in failure_keywords):
        return "FAILURE_ANALYSIS"

    return None


def plan_request(question: str) -> Intent:
    """
    Classify the user's request.

    Supported operational intents:
    - SUCCESS_RATE
    - FAILURE_ANALYSIS
    - BANK_ANALYSIS
    - INVESTIGATION
    - OUT_OF_SCOPE

    Deterministic rules handle obvious operational cases first.
    The local LLM handles ambiguous or natural-language requests.
    """

    rule_intent = _rule_based_intent(question)

    if rule_intent is not None:
        return rule_intent

    prompt = f"""
You are a payment operations request planner.

Your system is designed specifically to analyze
UPI-like payment transaction operations.

Classify the user's question into exactly ONE of these intents:

SUCCESS_RATE
Use this when the user asks about payment success,
successful transaction counts, success percentages,
or overall payment success performance.

FAILURE_ANALYSIS
Use this when the user asks about payment failures,
failure reasons, failed transaction counts,
or why transactions are failing.

BANK_ANALYSIS
Use this when the user asks about payment failures
or transaction performance broken down by sender bank,
receiver bank, or bank.

INVESTIGATION
Use this when the user explicitly asks to investigate,
perform an investigation, analyze the issue,
identify what should be investigated, or perform
a root-cause investigation.

OUT_OF_SCOPE
Use this when the request is unrelated to payment
operations, transaction analysis, payment failures,
bank analysis, success analysis, or investigation.

Examples:

"What is the payment success rate?"
SUCCESS_RATE

"Why are payments failing?"
FAILURE_ANALYSIS

"Which bank has the most failures?"
BANK_ANALYSIS

"Investigate why payments are failing."
INVESTIGATION

"What is the weather today?"
OUT_OF_SCOPE

"Write me a Python game."
OUT_OF_SCOPE

"Tell me a joke."
OUT_OF_SCOPE

"Who is the CEO of Google?"
OUT_OF_SCOPE

User question:
{question}

Return ONLY one intent name.
"""

    response = llm.invoke(prompt)

    intent = response.content.strip().upper()

    allowed_intents = {
        "SUCCESS_RATE",
        "FAILURE_ANALYSIS",
        "BANK_ANALYSIS",
        "INVESTIGATION",
        "OUT_OF_SCOPE",
    }

    if intent not in allowed_intents:
        return "OUT_OF_SCOPE"

    return intent
