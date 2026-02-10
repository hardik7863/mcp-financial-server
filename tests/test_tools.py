"""Unit tests for MCP Financial Server tools.

Tests mock the Supabase client to avoid requiring a live database.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.validators.input_validator import (
    TickerInput,
    CompanyIdentifierInput,
    SearchCompaniesInput,
    FinancialReportInput,
    CompareCompaniesInput,
    StockPriceInput,
    ScreenStocksInput,
    AnalystRatingsInput,
    SectorOverviewInput,
)
from src.utils.formatters import (
    format_currency,
    format_percentage,
    format_number,
    format_company_profile,
    format_stock_table,
    format_analyst_ratings,
    format_sector_overview,
    format_comparison,
)
from src.utils.errors import (
    CompanyNotFoundError,
    ValidationError,
    RateLimitExceededError,
)
from src.utils.rate_limiter import RateLimiter


# -----------------------------------------------------------------------
# Validator tests
# -----------------------------------------------------------------------


class TestTickerValidator:
    def test_valid_ticker(self):
        result = TickerInput(ticker="AAPL")
        assert result.ticker == "AAPL"

    def test_lowercase_ticker(self):
        result = TickerInput(ticker="aapl")
        assert result.ticker == "AAPL"

    def test_ticker_with_whitespace(self):
        result = TickerInput(ticker="  msft  ")
        assert result.ticker == "MSFT"

    def test_invalid_ticker_numbers(self):
        with pytest.raises(Exception):
            TickerInput(ticker="123")

    def test_invalid_ticker_too_long(self):
        with pytest.raises(Exception):
            TickerInput(ticker="TOOLONGTICKER")

    def test_invalid_ticker_special_chars(self):
        with pytest.raises(Exception):
            TickerInput(ticker="AA$PL")


class TestCompanyIdentifierInput:
    def test_valid_ticker_identifier(self):
        result = CompanyIdentifierInput(identifier="AAPL")
        assert result.identifier == "AAPL"

    def test_valid_name_identifier(self):
        result = CompanyIdentifierInput(identifier="Apple Inc.")
        assert result.identifier == "Apple Inc."

    def test_empty_identifier(self):
        with pytest.raises(Exception):
            CompanyIdentifierInput(identifier="")

    def test_whitespace_only(self):
        with pytest.raises(Exception):
            CompanyIdentifierInput(identifier="   ")


class TestSearchCompaniesInput:
    def test_valid_search(self):
        result = SearchCompaniesInput(sector="Technology", industry="Software")
        assert result.sector == "Technology"
        assert result.industry == "Software"

    def test_market_cap_range(self):
        result = SearchCompaniesInput(
            min_market_cap=100_000_000_000,
            max_market_cap=1_000_000_000_000,
        )
        assert result.min_market_cap == 100_000_000_000

    def test_country_filter(self):
        result = SearchCompaniesInput(country="US")
        assert result.country == "US"


class TestFinancialReportInput:
    def test_valid_report_input(self):
        result = FinancialReportInput(ticker="AAPL", fiscal_year=2024, fiscal_quarter="Q3")
        assert result.ticker == "AAPL"
        assert result.fiscal_year == 2024
        assert result.fiscal_quarter == "Q3"

    def test_quarter_validation(self):
        result = FinancialReportInput(ticker="AAPL", fiscal_quarter="q1")
        assert result.fiscal_quarter == "Q1"

    def test_invalid_quarter(self):
        with pytest.raises(Exception):
            FinancialReportInput(ticker="AAPL", fiscal_quarter="Q5")


class TestStockPriceInput:
    def test_valid_date_format(self):
        result = StockPriceInput(ticker="AAPL", start_date="2024-01-01", end_date="2024-12-31")
        assert result.start_date == "2024-01-01"

    def test_invalid_date_format(self):
        with pytest.raises(Exception):
            StockPriceInput(ticker="AAPL", start_date="01-01-2024")

    def test_default_limit(self):
        result = StockPriceInput(ticker="AAPL")
        assert result.limit == 30


class TestCompareCompaniesInput:
    def test_valid_compare(self):
        result = CompareCompaniesInput(tickers=["AAPL", "msft", "googl"])
        assert result.tickers == ["AAPL", "MSFT", "GOOGL"]

    def test_too_few_tickers(self):
        with pytest.raises(Exception):
            CompareCompaniesInput(tickers=["AAPL"])

    def test_too_many_tickers(self):
        with pytest.raises(Exception):
            CompareCompaniesInput(tickers=["A", "B", "C", "D", "E", "F"])

    def test_valid_metrics(self):
        result = CompareCompaniesInput(
            tickers=["AAPL", "MSFT"],
            metrics=["revenue", "eps", "gross_margin"],
        )
        assert result.metrics == ["revenue", "eps", "gross_margin"]

    def test_invalid_metric(self):
        with pytest.raises(Exception):
            CompareCompaniesInput(
                tickers=["AAPL", "MSFT"],
                metrics=["invalid_metric"],
            )


class TestScreenStocksInput:
    def test_valid_screen(self):
        result = ScreenStocksInput(
            min_revenue=10000,
            min_eps=2.0,
            min_gross_margin=30,
            max_debt_to_equity=2.0,
            sector="Technology",
        )
        assert result.min_revenue == 10000
        assert result.sector == "Technology"


class TestAnalystRatingsInput:
    def test_valid_with_firm(self):
        result = AnalystRatingsInput(ticker="AAPL", firm="Goldman Sachs")
        assert result.ticker == "AAPL"
        assert result.firm == "Goldman Sachs"

    def test_valid_without_firm(self):
        result = AnalystRatingsInput(ticker="AAPL")
        assert result.firm is None


class TestSectorOverviewInput:
    def test_valid_sector(self):
        result = SectorOverviewInput(sector="Technology")
        assert result.sector == "Technology"

    def test_sector_required(self):
        with pytest.raises(Exception):
            SectorOverviewInput()


# -----------------------------------------------------------------------
# Formatter tests
# -----------------------------------------------------------------------


class TestFormatters:
    def test_format_currency_trillions(self):
        assert format_currency(3_400_000_000_000) == "$3.40T"

    def test_format_currency_billions(self):
        assert format_currency(150_000_000_000) == "$150.00B"

    def test_format_currency_millions(self):
        assert format_currency(5_500_000) == "$5.50M"

    def test_format_currency_small(self):
        assert format_currency(1234.56) == "$1,234.56"

    def test_format_currency_none(self):
        assert format_currency(None) == "N/A"

    def test_format_percentage_decimal(self):
        assert format_percentage(0.234) == "23.40%"

    def test_format_percentage_whole(self):
        assert format_percentage(45.50) == "45.50%"

    def test_format_percentage_none(self):
        assert format_percentage(None) == "N/A"

    def test_format_number(self):
        assert format_number(164000) == "164,000"

    def test_format_number_none(self):
        assert format_number(None) == "N/A"

    def test_format_company_profile(self):
        company = {
            "name": "Apple Inc.",
            "ticker": "AAPL",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": 3_400_000_000_000,
            "country": "US",
            "ceo": "Tim Cook",
            "founded_year": 1976,
            "employees": 164000,
            "description": "Makes iPhones.",
        }
        result = format_company_profile(company)
        assert "Apple Inc." in result
        assert "AAPL" in result
        assert "$3.40T" in result
        assert "US" in result

    def test_format_stock_table_empty(self):
        assert format_stock_table([]) == "No stock price data available."

    def test_format_stock_table(self):
        prices = [{
            "date": "2024-12-31",
            "open": 250.00,
            "high": 253.00,
            "low": 249.00,
            "close": 252.50,
            "volume": 45000000,
        }]
        result = format_stock_table(prices)
        assert "2024-12-31" in result
        assert "45,000,000" in result

    def test_format_analyst_ratings_empty(self):
        assert format_analyst_ratings([]) == "No analyst ratings available."

    def test_format_analyst_ratings(self):
        ratings = [{
            "analyst_firm": "Goldman Sachs",
            "rating": "Buy",
            "target_price": 250.0,
            "previous_rating": "Hold",
            "rating_date": "2024-12-01",
        }]
        result = format_analyst_ratings(ratings)
        assert "Goldman Sachs" in result
        assert "Buy" in result
        assert "(prev: Hold)" in result

    def test_format_sector_overview_empty(self):
        assert format_sector_overview([]) == "No sector data available."

    def test_format_comparison(self):
        results = [{
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "market_cap": 3_400_000_000_000,
            "latest_financials": {
                "revenue": 94000.0,
                "net_income": 23000.0,
                "eps": 1.52,
                "gross_margin": 45.5,
            },
            "requested_metrics": ["revenue", "eps", "gross_margin"],
        }]
        result = format_comparison(results)
        assert "AAPL" in result
        assert "Apple" in result


# -----------------------------------------------------------------------
# Error tests
# -----------------------------------------------------------------------


class TestErrors:
    def test_company_not_found(self):
        err = CompanyNotFoundError("XYZ")
        assert "XYZ" in str(err)
        assert err.ticker == "XYZ"

    def test_rate_limit_exceeded(self):
        err = RateLimitExceededError()
        assert "Rate limit" in str(err)


# -----------------------------------------------------------------------
# Rate limiter tests
# -----------------------------------------------------------------------


class TestRateLimiter:
    def test_allows_under_limit(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            limiter.check("test_client")

    def test_blocks_over_limit(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.check("test_client")
        with pytest.raises(RateLimitExceededError):
            limiter.check("test_client")

    def test_separate_clients(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("client_a")
        limiter.check("client_a")
        # client_b should still work
        limiter.check("client_b")

    def test_reset(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.check("test_client")
        with pytest.raises(RateLimitExceededError):
            limiter.check("test_client")
        limiter.reset("test_client")
        limiter.check("test_client")  # should work after reset


# -----------------------------------------------------------------------
# Tool integration tests (mocked DB)
# -----------------------------------------------------------------------


MOCK_COMPANY = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "market_cap": 3_400_000_000_000,
    "country": "US",
    "ceo": "Tim Cook",
    "founded_year": 1976,
    "employees": 164000,
    "description": "Makes great products.",
}

MOCK_REPORT = {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "company_id": "550e8400-e29b-41d4-a716-446655440000",
    "fiscal_year": 2024,
    "fiscal_quarter": "Q4",
    "revenue": 94000.00,
    "net_income": 23000.00,
    "eps": 1.5200,
    "gross_margin": 45.50,
    "operating_margin": 31.20,
    "debt_to_equity": 1.872,
    "free_cash_flow": 28000.00,
    "report_date": "2024-12-31",
}


def _mock_supabase():
    """Create a mock Supabase client with chained query builder methods."""
    client = MagicMock()

    def make_chain(data):
        chain = MagicMock()
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.ilike.return_value = chain
        chain.or_.return_value = chain
        chain.gte.return_value = chain
        chain.lte.return_value = chain
        chain.order.return_value = chain
        chain.limit.return_value = chain
        chain.execute.return_value = MagicMock(data=data)
        return chain

    return client, make_chain


class TestCompanyTools:
    @patch("src.db.queries.get_supabase_client")
    def test_get_company_by_ticker(self, mock_get_client):
        client, make_chain = _mock_supabase()
        client.table.return_value = make_chain([MOCK_COMPANY])
        mock_get_client.return_value = client

        from src.db.queries import get_company_by_ticker
        result = get_company_by_ticker("AAPL")
        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple Inc."

    @patch("src.db.queries.get_supabase_client")
    def test_get_company_by_identifier_ticker(self, mock_get_client):
        client, make_chain = _mock_supabase()
        client.table.return_value = make_chain([MOCK_COMPANY])
        mock_get_client.return_value = client

        from src.db.queries import get_company_by_identifier
        result = get_company_by_identifier("AAPL")
        assert result["ticker"] == "AAPL"

    @patch("src.db.queries.get_supabase_client")
    def test_company_not_found(self, mock_get_client):
        client, make_chain = _mock_supabase()
        client.table.return_value = make_chain([])
        mock_get_client.return_value = client

        from src.db.queries import get_company_by_ticker
        with pytest.raises(CompanyNotFoundError):
            get_company_by_ticker("ZZZZ")

    @patch("src.db.queries.get_supabase_client")
    def test_search_companies(self, mock_get_client):
        client, make_chain = _mock_supabase()
        client.table.return_value = make_chain([MOCK_COMPANY])
        mock_get_client.return_value = client

        from src.db.queries import search_companies
        results = search_companies(sector="Technology")
        assert len(results) == 1
        assert results[0]["ticker"] == "AAPL"


class TestFinancialTools:
    @patch("src.db.queries.get_supabase_client")
    def test_get_financial_reports(self, mock_get_client):
        client, make_chain = _mock_supabase()

        company_chain = make_chain([MOCK_COMPANY])
        report_chain = make_chain([MOCK_REPORT])
        client.table.side_effect = [company_chain, report_chain]
        mock_get_client.return_value = client

        from src.db.queries import get_financial_reports
        company, reports = get_financial_reports("AAPL")
        assert company["ticker"] == "AAPL"
        assert len(reports) == 1
        assert reports[0]["revenue"] == 94000.00
        assert reports[0]["fiscal_quarter"] == "Q4"
        assert reports[0]["gross_margin"] == 45.50


class TestAnalystTools:
    @patch("src.db.queries.get_supabase_client")
    def test_get_analyst_ratings(self, mock_get_client):
        client, make_chain = _mock_supabase()
        mock_rating = {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "company_id": "550e8400-e29b-41d4-a716-446655440000",
            "analyst_firm": "Goldman Sachs",
            "rating": "Buy",
            "target_price": 250.0,
            "previous_rating": "Hold",
            "rating_date": "2024-12-01",
        }
        company_chain = make_chain([MOCK_COMPANY])
        ratings_chain = make_chain([mock_rating])
        client.table.side_effect = [company_chain, ratings_chain]
        mock_get_client.return_value = client

        from src.db.queries import get_analyst_ratings
        company, ratings = get_analyst_ratings("AAPL")
        assert company["ticker"] == "AAPL"
        assert ratings[0]["rating"] == "Buy"
        assert ratings[0]["analyst_firm"] == "Goldman Sachs"
        assert ratings[0]["previous_rating"] == "Hold"


class TestSectorTools:
    @patch("src.db.queries.get_supabase_client")
    def test_get_sector_stats(self, mock_get_client):
        client = MagicMock()
        mock_rpc_result = MagicMock(
            data=[{
                "sector": "Technology",
                "company_count": 5,
                "avg_market_cap": 2_580_000_000_000,
                "total_revenue": 400_000_000_000,
                "avg_margin": 0.25,
                "avg_rating_score": 3.8,
            }]
        )
        client.rpc.return_value = MagicMock(execute=MagicMock(return_value=mock_rpc_result))
        mock_get_client.return_value = client

        from src.db.queries import get_sector_stats
        stats = get_sector_stats("Technology")
        assert len(stats) == 1
        assert stats[0]["sector"] == "Technology"
