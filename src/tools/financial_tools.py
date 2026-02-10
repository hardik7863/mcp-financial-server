"""Financial report MCP tools: get_financial_report, compare_companies."""

import logging
from pydantic import ValidationError as PydanticValidationError

from src.db import queries
from src.utils.errors import MCPToolError
from src.utils.formatters import format_financial_report, format_comparison
from src.validators.input_validator import FinancialReportInput, CompareCompaniesInput

logger = logging.getLogger(__name__)


def register_financial_tools(mcp):
    """Register financial tools on the FastMCP instance."""

    @mcp.tool()
    def get_financial_report(
        ticker: str,
        fiscal_year: int | None = None,
        fiscal_quarter: str | None = None,
    ) -> str:
        """Get quarterly/annual financial reports for a company.

        Args:
            ticker: Stock ticker symbol (e.g. AAPL)
            fiscal_year: Fiscal year (e.g. 2024). Omit for all available years.
            fiscal_quarter: Fiscal quarter (Q1, Q2, Q3, Q4). Omit for all quarters.
        """
        try:
            validated = FinancialReportInput(
                ticker=ticker,
                fiscal_year=fiscal_year,
                fiscal_quarter=fiscal_quarter,
            )
            company, reports = queries.get_financial_reports(
                ticker=validated.ticker,
                fiscal_year=validated.fiscal_year,
                fiscal_quarter=validated.fiscal_quarter,
            )
            if not reports:
                return f"No financial reports found for {validated.ticker}."

            lines = [f"Financial Reports for {company['name']} ({company['ticker']})\n"]
            for r in reports:
                lines.append(format_financial_report(r, company["name"]))
                lines.append("")
            return "\n".join(lines)
        except PydanticValidationError as e:
            return f"Validation error: {e.errors()[0]['msg']}"
        except MCPToolError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("Unexpected error in get_financial_report")
            return f"Internal error: {e}"

    @mcp.tool()
    def compare_companies(
        tickers: list[str],
        metrics: list[str] | None = None,
    ) -> str:
        """Compare 2-5 companies side-by-side on key financial metrics.

        Args:
            tickers: List of 2-5 ticker symbols to compare (e.g. ["AAPL", "MSFT", "GOOGL"])
            metrics: List of metrics to compare. Defaults to ["revenue", "net_income", "eps", "gross_margin"]. Valid metrics: revenue, net_income, eps, gross_margin, operating_margin, debt_to_equity, free_cash_flow, market_cap
        """
        try:
            validated = CompareCompaniesInput(tickers=tickers, metrics=metrics)
            results = queries.compare_companies(
                validated.tickers,
                metrics=validated.metrics,
            )
            return format_comparison(results)
        except PydanticValidationError as e:
            return f"Validation error: {e.errors()[0]['msg']}"
        except MCPToolError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("Unexpected error in compare_companies")
            return f"Internal error: {e}"
