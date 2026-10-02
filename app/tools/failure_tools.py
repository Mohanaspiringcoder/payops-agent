from langchain_core.tools import tool

from app.database.queries import get_failure_summary as query_failure_summary


@tool
def get_failure_summary() -> dict:
    """
    Analyze failed payment transactions and summarize their failure reasons.
    """

    return query_failure_summary()
