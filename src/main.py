"""
MCP Financial Server — Entry Point

Exposes 8 financial database tools over MCP protocol.
Supports stdio and SSE transports.

Usage:
    python -m src.main                           # stdio (default)
    python -m src.main --transport sse --port 8000
"""

import argparse
import logging
import sys

from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (stdout reserved for JSON-RPC in stdio mode)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Create FastMCP server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Financial Database Server",
    instructions=(
        "MCP server providing financial data tools: company profiles, "
        "financial reports, stock prices, analyst ratings, and sector analysis. "
        "Backed by Supabase PostgreSQL."
    ),
)

# ---------------------------------------------------------------------------
# Register all tools
# ---------------------------------------------------------------------------
from src.tools.company_tools import register_company_tools
from src.tools.financial_tools import register_financial_tools
from src.tools.stock_tools import register_stock_tools
from src.tools.analyst_tools import register_analyst_tools
from src.tools.sector_tools import register_sector_tools

register_company_tools(mcp)
register_financial_tools(mcp)
register_stock_tools(mcp)
register_analyst_tools(mcp)
register_sector_tools(mcp)

# ---------------------------------------------------------------------------
# MCP Resources (schema descriptions for LLM context)
# ---------------------------------------------------------------------------

@mcp.resource("schema://companies")
def companies_schema() -> str:
    """Schema description for the companies table."""
    return (
        "Table: companies\n"
        "Columns: id, ticker (unique), name, sector, industry, market_cap, "
        "description, ceo, headquarters, founded_year, employees, website, created_at\n"
        "Indexes: sector, name\n"
        "Contains 25 companies across 5 sectors: Technology, Healthcare, "
        "Financial Services, Consumer Discretionary, Energy."
    )

@mcp.resource("schema://financial_reports")
def financial_reports_schema() -> str:
    """Schema description for the financial_reports table."""
    return (
        "Table: financial_reports\n"
        "Columns: id, company_id (FK→companies), fiscal_year, fiscal_quarter, "
        "revenue, net_income, eps, operating_margin, debt_to_equity, "
        "free_cash_flow, report_date, created_at\n"
        "Unique constraint: (company_id, fiscal_year, fiscal_quarter)\n"
        "Contains quarterly reports for 2022-2024 (3 years × 4 quarters per company)."
    )

@mcp.resource("schema://stock_prices")
def stock_prices_schema() -> str:
    """Schema description for the stock_prices table."""
    return (
        "Table: stock_prices\n"
        "Columns: id, company_id (FK→companies), price_date, open_price, "
        "close_price, high_price, low_price, volume, created_at\n"
        "Unique constraint: (company_id, price_date)\n"
        "Contains ~65 trading days per company (Q4 2024)."
    )

@mcp.resource("schema://analyst_ratings")
def analyst_ratings_schema() -> str:
    """Schema description for the analyst_ratings table."""
    return (
        "Table: analyst_ratings\n"
        "Columns: id, company_id (FK→companies), analyst_name, firm, "
        "rating (Strong Buy|Buy|Hold|Sell|Strong Sell), price_target, "
        "rating_date, notes, created_at\n"
        "Contains 2-3 ratings per company from major Wall Street firms."
    )


# ---------------------------------------------------------------------------
# MCP Prompt Templates
# ---------------------------------------------------------------------------

@mcp.prompt()
def financial_analysis(ticker: str) -> str:
    """Generate a prompt for comprehensive financial analysis of a company."""
    return (
        f"Please perform a comprehensive financial analysis of {ticker}. "
        f"Follow these steps:\n\n"
        f"1. Use get_company_profile to get basic company information for {ticker}\n"
        f"2. Use get_financial_report to retrieve recent quarterly reports\n"
        f"3. Use get_stock_price_history to check recent price trends\n"
        f"4. Use get_analyst_ratings to see Wall Street consensus\n\n"
        f"Then provide:\n"
        f"- Company overview and market position\n"
        f"- Revenue and profitability trend analysis\n"
        f"- Stock price momentum assessment\n"
        f"- Analyst sentiment summary\n"
        f"- Overall investment thesis (bull and bear case)"
    )


@mcp.prompt()
def sector_comparison(sector: str) -> str:
    """Generate a prompt for sector analysis and company comparison."""
    return (
        f"Please analyze the {sector} sector. Follow these steps:\n\n"
        f"1. Use get_sector_overview to get aggregate sector statistics for '{sector}'\n"
        f"2. Use search_companies with sector='{sector}' to list all companies\n"
        f"3. Use screen_stocks with sector='{sector}' to find top performers\n"
        f"4. Pick the top 3 companies by market cap and use compare_companies\n\n"
        f"Then provide:\n"
        f"- Sector health overview\n"
        f"- Top companies and their competitive positioning\n"
        f"- Key financial metrics comparison\n"
        f"- Investment recommendations within the sector"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="MCP Financial Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=None,
        help="Transport mode (default: from MCP_TRANSPORT env var or stdio)",
    )
    parser.add_argument("--host", default=None, help="SSE host (default: from env or 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="SSE port (default: from env or 8000)")

    args = parser.parse_args()

    # Resolve settings (lazy import to avoid env validation at import time)
    from src.config.env import get_settings
    settings = get_settings()

    transport = args.transport or settings.mcp_transport
    host = args.host or settings.mcp_host
    port = args.port or settings.mcp_port

    logger.info(f"Starting MCP Financial Server (transport={transport})")

    if transport == "sse":
        mcp.settings.host = host
        mcp.settings.port = port
        logger.info(f"SSE endpoint: http://{host}:{port}/sse")
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
