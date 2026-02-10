"""Database query functions using Supabase PostgREST client.

All queries use the PostgREST builder which parameterises values
automatically, preventing SQL injection.
"""

import logging

from src.db.client import get_supabase_client
from src.utils.errors import CompanyNotFoundError, DatabaseError

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------
# Company queries
# -----------------------------------------------------------------------

def get_company_by_ticker(ticker: str) -> dict:
    """Fetch a single company by ticker symbol."""
    client = get_supabase_client()
    result = (
        client.table("companies")
        .select("*")
        .eq("ticker", ticker.upper())
        .execute()
    )
    if not result.data:
        raise CompanyNotFoundError(ticker)
    return result.data[0]


def get_company_by_identifier(identifier: str) -> dict:
    """Fetch a company by ticker or partial name match."""
    client = get_supabase_client()

    # First try exact ticker match
    clean = identifier.strip().upper()
    result = (
        client.table("companies")
        .select("*")
        .eq("ticker", clean)
        .execute()
    )
    if result.data:
        return result.data[0]

    # Fall back to partial name match (case-insensitive)
    result = (
        client.table("companies")
        .select("*")
        .ilike("name", f"%{identifier.strip()}%")
        .limit(1)
        .execute()
    )
    if not result.data:
        raise CompanyNotFoundError(identifier)
    return result.data[0]


def search_companies(
    sector: str | None = None,
    industry: str | None = None,
    min_market_cap: int | None = None,
    max_market_cap: int | None = None,
    country: str | None = None,
) -> list[dict]:
    """Search companies by sector, industry, market cap range, or country."""
    client = get_supabase_client()
    builder = client.table("companies").select("*")

    if sector:
        builder = builder.eq("sector", sector)
    if industry:
        builder = builder.ilike("industry", f"%{industry}%")
    if min_market_cap is not None:
        builder = builder.gte("market_cap", min_market_cap)
    if max_market_cap is not None:
        builder = builder.lte("market_cap", max_market_cap)
    if country:
        builder = builder.eq("country", country)

    result = builder.execute()
    return result.data


def get_company_id_by_ticker(ticker: str) -> str:
    """Resolve ticker to company ID. Raises CompanyNotFoundError."""
    company = get_company_by_ticker(ticker)
    return company["id"]


# -----------------------------------------------------------------------
# Financial report queries
# -----------------------------------------------------------------------

def get_financial_reports(
    ticker: str,
    fiscal_year: int | None = None,
    fiscal_quarter: str | None = None,
    limit: int = 12,
) -> tuple[dict, list[dict]]:
    """Fetch financial reports for a company. Returns (company, reports)."""
    company = get_company_by_ticker(ticker)
    client = get_supabase_client()

    builder = (
        client.table("financial_reports")
        .select("*")
        .eq("company_id", company["id"])
    )

    if fiscal_year:
        builder = builder.eq("fiscal_year", fiscal_year)
    if fiscal_quarter:
        builder = builder.eq("fiscal_quarter", fiscal_quarter)

    result = (
        builder
        .order("fiscal_year", desc=True)
        .order("fiscal_quarter", desc=True)
        .limit(limit)
        .execute()
    )
    return company, result.data


def get_latest_financials(company_id: str) -> dict | None:
    """Get most recent quarter's financials for a company."""
    client = get_supabase_client()
    result = (
        client.table("financial_reports")
        .select("*")
        .eq("company_id", company_id)
        .order("fiscal_year", desc=True)
        .order("fiscal_quarter", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


# -----------------------------------------------------------------------
# Stock price queries
# -----------------------------------------------------------------------

def get_stock_prices(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 30,
) -> tuple[dict, list[dict]]:
    """Fetch stock prices for a company. Returns (company, prices)."""
    company = get_company_by_ticker(ticker)
    client = get_supabase_client()

    builder = (
        client.table("stock_prices")
        .select("*")
        .eq("company_id", company["id"])
    )

    if start_date:
        builder = builder.gte("date", start_date)
    if end_date:
        builder = builder.lte("date", end_date)

    result = (
        builder
        .order("date", desc=True)
        .limit(limit)
        .execute()
    )
    return company, result.data


def screen_stocks(
    min_revenue: float | None = None,
    min_eps: float | None = None,
    min_gross_margin: float | None = None,
    max_debt_to_equity: float | None = None,
    sector: str | None = None,
) -> list[dict]:
    """Screen stocks based on financial criteria. Returns companies with latest financials."""
    client = get_supabase_client()
    builder = client.table("companies").select("*")

    if sector:
        builder = builder.eq("sector", sector)

    result = builder.execute()
    companies = result.data

    # Enrich with latest financials and filter
    enriched = []
    for comp in companies:
        latest = get_latest_financials(comp["id"])
        if latest is None:
            continue

        # Apply financial filters
        if min_revenue is not None:
            rev = float(latest.get("revenue") or 0)
            if rev < min_revenue:
                continue
        if min_eps is not None:
            eps = float(latest.get("eps") or 0)
            if eps < min_eps:
                continue
        if min_gross_margin is not None:
            gm = float(latest.get("gross_margin") or 0)
            if gm < min_gross_margin:
                continue
        if max_debt_to_equity is not None:
            dte = float(latest.get("debt_to_equity") or 999)
            if dte > max_debt_to_equity:
                continue

        enriched.append({**comp, "latest_financials": latest})

    return enriched


# -----------------------------------------------------------------------
# Analyst rating queries
# -----------------------------------------------------------------------

def get_analyst_ratings(
    ticker: str,
    firm: str | None = None,
    limit: int = 20,
) -> tuple[dict, list[dict]]:
    """Fetch analyst ratings for a company. Returns (company, ratings)."""
    company = get_company_by_ticker(ticker)
    client = get_supabase_client()

    builder = (
        client.table("analyst_ratings")
        .select("*")
        .eq("company_id", company["id"])
    )

    if firm:
        builder = builder.ilike("analyst_firm", f"%{firm}%")

    result = (
        builder
        .order("rating_date", desc=True)
        .limit(limit)
        .execute()
    )
    return company, result.data


# -----------------------------------------------------------------------
# Sector queries (using RPC)
# -----------------------------------------------------------------------

def get_sector_stats(sector: str) -> list[dict]:
    """Call the get_sector_stats RPC function for a specific sector."""
    client = get_supabase_client()
    result = client.rpc("get_sector_stats", {"target_sector": sector}).execute()
    return result.data


# -----------------------------------------------------------------------
# Compare companies
# -----------------------------------------------------------------------

def compare_companies(tickers: list[str], metrics: list[str] | None = None) -> list[dict]:
    """Fetch profile + latest financials for multiple companies for comparison."""
    if metrics is None:
        metrics = ["revenue", "net_income", "eps", "gross_margin"]

    results = []
    for ticker in tickers:
        company = get_company_by_ticker(ticker)
        latest = get_latest_financials(company["id"])
        results.append({**company, "latest_financials": latest, "requested_metrics": metrics})
    return results
