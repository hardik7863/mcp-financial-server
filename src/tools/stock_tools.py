"""Stock price MCP tools: get_stock_price_history, screen_stocks."""

import logging
from pydantic import ValidationError as PydanticValidationError

from src.db import queries
from src.utils.errors import MCPToolError
from src.utils.formatters import format_stock_table, format_currency, format_percentage
from src.validators.input_validator import StockPriceInput, ScreenStocksInput

logger = logging.getLogger(__name__)


def register_stock_tools(mcp):
    """Register stock tools on the FastMCP instance."""

    @mcp.tool()
    def get_stock_price_history(
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 30,
    ) -> str:
        """Get historical stock price data for a company.

        Args:
            ticker: Stock ticker symbol (e.g. AAPL)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Max number of price rows (1-365, default 30)
        """
        try:
            validated = StockPriceInput(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )
            company, prices = queries.get_stock_prices(
                ticker=validated.ticker,
                start_date=validated.start_date,
                end_date=validated.end_date,
                limit=validated.limit,
            )
            if not prices:
                return f"No stock price data found for {validated.ticker}."

            header = f"Stock Price History — {company['name']} ({company['ticker']})\n"
            return header + format_stock_table(prices)
        except PydanticValidationError as e:
            return f"Validation error: {e.errors()[0]['msg']}"
        except MCPToolError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("Unexpected error in get_stock_price_history")
            return f"Internal error: {e}"

    @mcp.tool()
    def screen_stocks(
        min_revenue: float | None = None,
        min_eps: float | None = None,
        min_gross_margin: float | None = None,
        max_debt_to_equity: float | None = None,
        sector: str | None = None,
    ) -> str:
        """Screen stocks based on multiple financial criteria.

        Args:
            min_revenue: Minimum revenue in millions USD
            min_eps: Minimum earnings per share
            min_gross_margin: Minimum gross margin percentage (e.g. 30 for 30%)
            max_debt_to_equity: Maximum debt-to-equity ratio
            sector: Filter by sector (e.g. Technology, Healthcare)
        """
        try:
            validated = ScreenStocksInput(
                min_revenue=min_revenue,
                min_eps=min_eps,
                min_gross_margin=min_gross_margin,
                max_debt_to_equity=max_debt_to_equity,
                sector=sector,
            )
            results = queries.screen_stocks(
                min_revenue=validated.min_revenue,
                min_eps=validated.min_eps,
                min_gross_margin=validated.min_gross_margin,
                max_debt_to_equity=validated.max_debt_to_equity,
                sector=validated.sector,
            )
            if not results:
                return "No stocks match your screening criteria."

            lines = [f"Stock Screener Results ({len(results)} matches)\n"]
            header = f"{'Ticker':<8} {'Name':<30} {'Sector':<22} {'Revenue':>14} {'EPS':>8} {'Gross Margin':>14} {'D/E':>8}"
            lines.append(header)
            lines.append("-" * len(header))

            for comp in results:
                fin = comp.get("latest_financials") or {}
                gm = fin.get("gross_margin")
                lines.append(
                    f"{comp['ticker']:<8} "
                    f"{comp['name'][:28]:<30} "
                    f"{comp['sector'][:20]:<22} "
                    f"{format_currency(float(fin['revenue']) if fin.get('revenue') else None):>14} "
                    f"{'$' + str(fin.get('eps', 'N/A')):>8} "
                    f"{format_percentage(float(gm) if gm is not None else None):>14} "
                    f"{fin.get('debt_to_equity', 'N/A'):>8}"
                )
            return "\n".join(lines)
        except PydanticValidationError as e:
            return f"Validation error: {e.errors()[0]['msg']}"
        except MCPToolError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("Unexpected error in screen_stocks")
            return f"Internal error: {e}"
