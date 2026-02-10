"""Sector overview MCP tools: get_sector_overview."""

import logging
from pydantic import ValidationError as PydanticValidationError

from src.db import queries
from src.utils.errors import MCPToolError
from src.utils.formatters import format_sector_overview
from src.validators.input_validator import SectorOverviewInput

logger = logging.getLogger(__name__)


def register_sector_tools(mcp):
    """Register sector tools on the FastMCP instance."""

    @mcp.tool()
    def get_sector_overview(sector: str) -> str:
        """Get aggregated sector-level stats including avg market cap, avg margin, company count, and analyst sentiment.

        Args:
            sector: Sector name (e.g. Technology, Healthcare, Financial Services, Consumer Discretionary, Energy)
        """
        try:
            validated = SectorOverviewInput(sector=sector)
            stats = queries.get_sector_stats(sector=validated.sector)
            if not stats:
                return f"No data found for sector '{validated.sector}'."

            return f"Sector Overview — {validated.sector}\n" + format_sector_overview(stats)
        except PydanticValidationError as e:
            return f"Validation error: {e.errors()[0]['msg']}"
        except MCPToolError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("Unexpected error in get_sector_overview")
            return f"Internal error: {e}"
