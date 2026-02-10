"""Analyst rating MCP tools: get_analyst_ratings."""

import logging
from pydantic import ValidationError as PydanticValidationError

from src.db import queries
from src.utils.errors import MCPToolError
from src.utils.formatters import format_analyst_ratings
from src.validators.input_validator import AnalystRatingsInput

logger = logging.getLogger(__name__)


def register_analyst_tools(mcp):
    """Register analyst tools on the FastMCP instance."""

    @mcp.tool()
    def get_analyst_ratings(
        ticker: str,
        firm: str | None = None,
    ) -> str:
        """Get latest analyst ratings and consensus for a company.

        Args:
            ticker: Stock ticker symbol (e.g. AAPL)
            firm: Filter by analyst firm name (e.g. Goldman Sachs, Morgan Stanley)
        """
        try:
            validated = AnalystRatingsInput(ticker=ticker, firm=firm)
            company, ratings = queries.get_analyst_ratings(
                ticker=validated.ticker,
                firm=validated.firm,
            )
            if not ratings:
                msg = f"No analyst ratings found for {validated.ticker}"
                if validated.firm:
                    msg += f" from {validated.firm}"
                return msg + "."

            header = f"Analyst Ratings — {company['name']} ({company['ticker']})\n"
            return header + format_analyst_ratings(ratings)
        except PydanticValidationError as e:
            return f"Validation error: {e.errors()[0]['msg']}"
        except MCPToolError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("Unexpected error in get_analyst_ratings")
            return f"Internal error: {e}"
