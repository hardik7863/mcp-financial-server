"""
Live integration test — connects to the MCP server via stdio
and calls all 8 tools against the real Supabase database.
"""

import asyncio
import sys
import json

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


SERVER_COMMAND = [sys.executable, "-m", "src.main", "--transport", "stdio"]

TOOL_CALLS = [
    {
        "name": "get_company_profile",
        "args": {"ticker": "AAPL"},
        "expect_contains": "Apple Inc.",
    },
    {
        "name": "search_companies",
        "args": {"sector": "Technology", "limit": 5},
        "expect_contains": "AAPL",
    },
    {
        "name": "get_financial_report",
        "args": {"ticker": "MSFT", "year": 2024, "quarter": 4},
        "expect_contains": "Microsoft",
    },
    {
        "name": "compare_companies",
        "args": {"tickers": ["AAPL", "MSFT", "GOOGL"]},
        "expect_contains": "Company Comparison",
    },
    {
        "name": "get_stock_price_history",
        "args": {"ticker": "NVDA", "start_date": "2024-10-01", "end_date": "2024-12-31"},
        "expect_contains": "NVIDIA",
    },
    {
        "name": "screen_stocks",
        "args": {"sector": "Healthcare", "min_market_cap": 200000000000},
        "expect_contains": "Stock Screener",
    },
    {
        "name": "get_analyst_ratings",
        "args": {"ticker": "TSLA"},
        "expect_contains": "Tesla",
    },
    {
        "name": "get_sector_overview",
        "args": {"sector": "Energy"},
        "expect_contains": "Energy",
    },
]


async def main():
    server_params = StdioServerParameters(
        command=SERVER_COMMAND[0],
        args=SERVER_COMMAND[1:],
    )

    print("=" * 60)
    print("  MCP Financial Server — Live Integration Test")
    print("=" * 60)

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            print(f"\nRegistered tools ({len(tool_names)}): {', '.join(tool_names)}\n")

            passed = 0
            failed = 0

            for tc in TOOL_CALLS:
                name = tc["name"]
                args = tc["args"]
                expect = tc["expect_contains"]

                print(f"--- Tool: {name} ---")
                print(f"  Args: {json.dumps(args)}")

                try:
                    result = await session.call_tool(name, args)
                    text = result.content[0].text if result.content else ""

                    if expect in text:
                        print(f"  ✓ PASS (contains '{expect}')")
                        # Print first 3 lines of output
                        lines = text.strip().split("\n")
                        for line in lines[:3]:
                            print(f"    | {line}")
                        if len(lines) > 3:
                            print(f"    | ... ({len(lines) - 3} more lines)")
                        passed += 1
                    else:
                        print(f"  ✗ FAIL — expected '{expect}' in output")
                        print(f"    Got: {text[:200]}")
                        failed += 1
                except Exception as e:
                    print(f"  ✗ ERROR — {e}")
                    failed += 1

                print()

            print("=" * 60)
            print(f"  Results: {passed} passed, {failed} failed out of {len(TOOL_CALLS)}")
            print("=" * 60)

            return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
