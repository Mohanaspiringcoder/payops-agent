from typing import Any

from langchain_ollama import ChatOllama

from app.config.settings import LLM_MODEL, LLM_TEMPERATURE

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
)

def investigate_payment_failures(
    evidence: dict,
    operational_knowledge: dict[str, Any] | None = None,
    validation_errors: list[str] | None = None,
) -> str:
    feedback = ""

    if validation_errors:
        feedback = f"""
PREVIOUS RESPONSE VALIDATION FEEDBACK:
{validation_errors}

The previous response failed validation.

You MUST correct every listed issue.
Do not repeat the unsupported claim.
Do not introduce a new numerical relationship.
Do not introduce a new cause.
"""

    operational_knowledge = operational_knowledge or {}

    prompt = f"""
You are a payment operations investigation assistant.

Your job is to produce a SHORT, GROUNDED investigation
from VERIFIED TRANSACTION EVIDENCE.

You are NOT a free-form analyst.
You must not invent relationships, causes, calculations,
trends, or additional transaction facts.

==================================================
VERIFIED TRANSACTION EVIDENCE
==================================================

{evidence}

==================================================
OPERATIONAL KNOWLEDGE
==================================================

{operational_knowledge}

Operational knowledge provides definitions and general
investigation guidance.

It is NOT evidence about what happened in these transactions.

==================================================
SOURCE PRIORITY
==================================================

1. VERIFIED TRANSACTION EVIDENCE
   - The only source for transaction facts and numbers.

2. OPERATIONAL KNOWLEDGE
   - Only use this to explain the meaning of a failure code
     or suggest what additional evidence could be examined.

Never treat operational knowledge as proof of an actual cause.

==================================================
CRITICAL RULES
==================================================

RULE 1:
Only state numbers that already appear in VERIFIED TRANSACTION
EVIDENCE.

RULE 2:
Do NOT calculate new numbers.

RULE 3:
Do NOT create mathematical relationships.

Do NOT say things such as:
- "3 times more"
- "twice as frequent"
- "50% higher"
- "more than"
- "less than"
- "higher than"
- "lower than"
unless that exact relationship is explicitly present in the
verified evidence.

RULE 4:
Do NOT claim a cause.

For example, do NOT say:
- caused by network issues
- caused by server overload
- caused by bank problems
- due to infrastructure issues
- due to latency
unless the verified evidence explicitly proves that cause.

RULE 5:
If the cause is unknown, say exactly:

"The available evidence does not establish the underlying cause."

RULE 6:
Do not invent timestamps, durations, averages, trends,
historical comparisons, infrastructure details, or system behavior.

RULE 7:
NEXT INVESTIGATION may only suggest additional evidence
to collect. It must NOT claim what that evidence will prove.

For example:

GOOD:
"Examine transaction-level timestamps for the failed transactions."

BAD:
"Examine timestamps to determine whether the failures were caused
by network issues."

==================================================
RESPONSE FORMAT
==================================================

Return exactly these four sections:

OBSERVED EVIDENCE:
State only directly observed facts from the verified evidence.

INTERPRETATION:
Explain what the observed failure code means using operational
knowledge if useful.

Do not create new calculations or causal explanations.

LIMITATIONS:
State what cannot be established from the available evidence.

NEXT INVESTIGATION:
Suggest up to two additional pieces of evidence that should be
examined next.

Keep the response concise.

{feedback}

Return ONLY the four sections.
"""

    response = llm.invoke(prompt)

    return response.content
