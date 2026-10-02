from langchain_core.tools import tool

from app.database.queries import get_success_rate


@tool
def calculate_success_rate() -> dict:
    """
    Calculate the payment success rate from the operational database.
    """

    return get_success_rate()
