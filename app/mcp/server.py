import asyncio

from mcp.server import MCPServer

from app.tools.failure_tools import get_failure_summary
from app.tools.knowledge_tools import retrieve_operational_knowledge


mcp = MCPServer(
    "PayOps MCP Server"
)


@mcp.tool()
def get_payment_failure_summary() -> dict:
    """Get a summary of failed UPI-like payment transactions."""
    return get_failure_summary.invoke({})


@mcp.tool()
def search_operational_knowledge(
    question: str,
    top_k: int = 2,
) -> dict:
    """Search operational knowledge for payment failure investigation guidance."""
    return retrieve_operational_knowledge(
        question=question,
        top_k=top_k,
    )


if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())
