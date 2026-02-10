"""Pydantic models for validating MCP tool inputs."""

import re
from pydantic import BaseModel, Field, field_validator


class TickerInput(BaseModel):
    """Validates a single stock ticker."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g. AAPL, MSFT)")

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^[A-Z]{1,10}$", v):
            raise ValueError(f"Invalid ticker format: '{v}'. Must be 1-10 uppercase letters.")
        return v


class CompanyIdentifierInput(BaseModel):
    """Validates get_company_profile tool input — ticker or partial name."""
    identifier: str = Field(..., description="Stock ticker symbol or partial company name")

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1:
            raise ValueError("Identifier must not be empty.")
        if len(v) > 255:
            raise ValueError("Identifier too long (max 255 characters).")
        return v


class SearchCompaniesInput(BaseModel):
    """Validates search_companies tool input."""
    sector: str | None = Field(None, description="Filter by sector name")
    industry: str | None = Field(None, description="Filter by industry")
    min_market_cap: int | None = Field(None, ge=0, description="Minimum market cap in USD")
    max_market_cap: int | None = Field(None, ge=0, description="Maximum market cap in USD")
    country: str | None = Field(None, description="Filter by country")


class FinancialReportInput(BaseModel):
    """Validates get_financial_report tool input."""
    ticker: str = Field(..., description="Stock ticker symbol")
    fiscal_year: int | None = Field(None, ge=2000, le=2030, description="Fiscal year")
    fiscal_quarter: str | None = Field(None, description="Fiscal quarter (Q1, Q2, Q3, Q4)")

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        return TickerInput(ticker=v).ticker

    @field_validator("fiscal_quarter")
    @classmethod
    def validate_quarter(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip().upper()
            if v not in ("Q1", "Q2", "Q3", "Q4"):
                raise ValueError(f"Invalid quarter: '{v}'. Must be Q1, Q2, Q3, or Q4.")
        return v


class CompareCompaniesInput(BaseModel):
    """Validates compare_companies tool input."""
    tickers: list[str] = Field(..., min_length=2, max_length=5, description="List of 2-5 ticker symbols to compare")
    metrics: list[str] | None = Field(None, description="Metrics to compare (defaults to revenue, net_income, eps, gross_margin)")

    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, v: list[str]) -> list[str]:
        return [TickerInput(ticker=t).ticker for t in v]

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, v: list[str] | None) -> list[str] | None:
        valid_metrics = {"revenue", "net_income", "eps", "gross_margin", "operating_margin", "debt_to_equity", "free_cash_flow", "market_cap"}
        if v is not None:
            v = [m.strip().lower() for m in v]
            for m in v:
                if m not in valid_metrics:
                    raise ValueError(f"Invalid metric: '{m}'. Valid metrics: {', '.join(sorted(valid_metrics))}")
        return v


class StockPriceInput(BaseModel):
    """Validates get_stock_price_history tool input."""
    ticker: str = Field(..., description="Stock ticker symbol")
    start_date: str | None = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: str | None = Field(None, description="End date (YYYY-MM-DD)")
    limit: int = Field(30, ge=1, le=365, description="Max number of rows (default 30)")

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        return TickerInput(ticker=v).ticker

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
                raise ValueError(f"Invalid date format: '{v}'. Use YYYY-MM-DD.")
        return v


class ScreenStocksInput(BaseModel):
    """Validates screen_stocks tool input."""
    min_revenue: float | None = Field(None, ge=0, description="Minimum revenue in millions USD")
    min_eps: float | None = Field(None, description="Minimum earnings per share")
    min_gross_margin: float | None = Field(None, ge=0, le=100, description="Minimum gross margin percentage")
    max_debt_to_equity: float | None = Field(None, ge=0, description="Maximum debt-to-equity ratio")
    sector: str | None = Field(None, description="Filter by sector")


class AnalystRatingsInput(BaseModel):
    """Validates get_analyst_ratings tool input."""
    ticker: str = Field(..., description="Stock ticker symbol")
    firm: str | None = Field(None, description="Filter by analyst firm name")

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        return TickerInput(ticker=v).ticker


class SectorOverviewInput(BaseModel):
    """Validates get_sector_overview tool input."""
    sector: str = Field(..., description="Sector name (e.g. Technology, Healthcare, Energy)")
