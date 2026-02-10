"""Company-related MCP tools: get_company_profile, search_companies."""

import logging
from pydantic import ValidationError as PydanticValidationError

from src.db import queries
from src.utils.errors import MCPToolError
from src.utils.formatters import format_company_profile, format_currency
from src.validators.input_validator import CompanyIdentifierInput, SearchCompaniesInput

logger = logging.getLogger(__name__)


def register_company_tools(mcp):
    """Register company tools on the FastMCP instance."""

    @mcp.tool()
    def get_company_profile(identifier: str) -> str:
        """Fetch full company profile by ticker symbol or partial company name.

        Args:
            identifier: Stock ticker symbol (e.g. AAPL) or partial company name (e.g. Apple)
        """
        try:
            validated = CompanyIdentifierInput(identifier=identifier)
            company = queries.get_company_by_identifier(validated.identifier)
            return format_company_profile(company)
        except PydanticValidationError as e:
            return f"Validation error: {e.errors()[0]['msg']}"
        except MCPToolError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("Unexpected error in get_company_profile")
            return f"Internal error: {e}"

    @mcp.tool()
    def search_companies(
        sector: str | None = None,
        industry: str | None = None,
        min_market_cap: int | None = None,
        max_market_cap: int | None = None,
        country: str | None = None,
    ) -> str:
        """Search companies by sector, industry, market cap range, or country.

        Args:
            sector: Filter by sector (e.g. Technology, Healthcare, Energy)
            industry: Filter by industry (e.g. Software, Pharma)
            min_market_cap: Minimum market capitalization in USD
            max_market_cap: Maximum market capitalization in USD
            country: Filter by country (e.g. US)
        """
        try:
            validated = SearchCompaniesInput(
                sector=sector,
                industry=industry,
                min_market_cap=min_market_cap,
                max_market_cap=max_market_cap,
                country=country,
            )
            companies = queries.search_companies(
                sector=validated.sector,
                industry=validated.industry,
                min_market_cap=validated.min_market_cap,
                max_market_cap=validated.max_market_cap,
                country=validated.country,
            )
            if not companies:
                return "No companies found matching your criteria."

            lines = [f"Found {len(companies)} company(ies):\n"]
            for c in companies:
                cap = c.get("market_cap", 0)
                cap_str = format_currency(cap) if cap else "N/A"
                lines.append(
                    f"  {c['ticker']:<8} {c['name']:<35} "
                    f"Sector: {c['sector']:<25} MCap: {cap_str}"
                )
            return "\n".join(lines)
        except PydanticValidationError as e:
            return f"Validation error: {e.errors()[0]['msg']}"
        except MCPToolError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("Unexpected error in search_companies")
            return f"Internal error: {e}"
