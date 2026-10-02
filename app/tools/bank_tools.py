from langchain_core.tools import tool

from app.database.queries import (
    get_bank_failure_summary as query_bank_failure_summary,
)


@tool
def get_bank_failure_summary() -> dict:
    """
    Analyze failed payment transactions by sender and receiver bank.
    """

    return query_bank_failure_summary()
