import json

import pytest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def extract_tool_result(result) -> dict:
    """Extract the JSON payload returned by an MCP tool."""
    text = result.content[0].text
    return json.loads(text)


@pytest.mark.anyio
async def test_mcp_tools():
    server_parameters = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp.server"],
    )

    async with stdio_client(server_parameters) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            tool_names = [
                tool.name
                for tool in tools.tools
            ]

            print("Available tools:", tool_names)

            assert "get_payment_failure_summary" in tool_names
            assert "search_operational_knowledge" in tool_names

            failure_result = await session.call_tool(
                "get_payment_failure_summary",
                {},
            )

            assert failure_result.is_error is False

            failure_data = extract_tool_result(
                failure_result
            )

            print("Failure data:", failure_data)

            assert "total_failed" in failure_data
            assert "failure_reasons" in failure_data
            assert failure_data["total_failed"] == 8

            knowledge_result = await session.call_tool(
                "search_operational_knowledge",
                {
                    "question": "How should TIMEOUT failures be investigated?",
                    "top_k": 2,
                },
            )

            assert knowledge_result.is_error is False

            knowledge_data = extract_tool_result(
                knowledge_result
            )

            print("Knowledge data:", knowledge_data)

            assert knowledge_data["query"] == (
                "How should TIMEOUT failures be investigated?"
            )
            assert "results" in knowledge_data
            assert len(knowledge_data["results"]) > 0
