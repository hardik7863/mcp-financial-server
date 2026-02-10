"""
Seed script — populates Supabase with realistic financial data.

Usage:
    python -m database.seed_script          (from project root)
    python database/seed_script.py          (direct)

Requires SUPABASE_URL and SUPABASE_KEY in .env or environment.
"""

import os
import random
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------------------------
# Company definitions (25 companies, 5 sectors)
# ---------------------------------------------------------------------------
COMPANIES = [
    # Technology
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "market_cap": 3_400_000_000_000, "country": "US", "ceo": "Tim Cook", "founded_year": 1976, "employees": 164000, "description": "Designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories."},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software", "market_cap": 3_100_000_000_000, "country": "US", "ceo": "Satya Nadella", "founded_year": 1975, "employees": 228000, "description": "Develops and licenses software, services, devices, and solutions worldwide."},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Services", "market_cap": 2_100_000_000_000, "country": "US", "ceo": "Sundar Pichai", "founded_year": 1998, "employees": 182000, "description": "Provides online advertising services, search, cloud computing, and technology products."},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors", "market_cap": 2_800_000_000_000, "country": "US", "ceo": "Jensen Huang", "founded_year": 1993, "employees": 29600, "description": "Designs and sells graphics processing units and system-on-chip units."},
    {"ticker": "META", "name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Internet Services", "market_cap": 1_500_000_000_000, "country": "US", "ceo": "Mark Zuckerberg", "founded_year": 2004, "employees": 67317, "description": "Builds technologies that help people connect, find communities, and grow businesses."},

    # Healthcare
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharma", "market_cap": 380_000_000_000, "country": "US", "ceo": "Joaquin Duato", "founded_year": 1886, "employees": 131900, "description": "Researches, develops, manufactures, and sells healthcare products worldwide."},
    {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "Healthcare", "industry": "Healthcare Plans", "market_cap": 480_000_000_000, "country": "US", "ceo": "Andrew Witty", "founded_year": 1977, "employees": 400000, "description": "Operates as a diversified healthcare company offering health benefits and services."},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare", "industry": "Pharma", "market_cap": 160_000_000_000, "country": "US", "ceo": "Albert Bourla", "founded_year": 1849, "employees": 88000, "description": "Discovers, develops, and manufactures healthcare products worldwide."},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare", "industry": "Pharma", "market_cap": 310_000_000_000, "country": "US", "ceo": "Robert Michael", "founded_year": 2013, "employees": 50000, "description": "Discovers, develops, and commercializes pharmaceuticals worldwide."},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific", "sector": "Healthcare", "industry": "Diagnostics & Research", "market_cap": 200_000_000_000, "country": "US", "ceo": "Marc Casper", "founded_year": 2006, "employees": 130000, "description": "Provides life sciences solutions, analytical instruments, and laboratory products."},

    # Financial Services
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "industry": "Banks", "market_cap": 590_000_000_000, "country": "US", "ceo": "Jamie Dimon", "founded_year": 2000, "employees": 309926, "description": "Provides global financial services including investment banking, treasury, and securities."},
    {"ticker": "V", "name": "Visa Inc.", "sector": "Financial Services", "industry": "Credit Services", "market_cap": 560_000_000_000, "country": "US", "ceo": "Ryan McInerney", "founded_year": 1958, "employees": 30800, "description": "Operates as a payments technology company worldwide."},
    {"ticker": "MA", "name": "Mastercard Inc.", "sector": "Financial Services", "industry": "Credit Services", "market_cap": 430_000_000_000, "country": "US", "ceo": "Michael Miebach", "founded_year": 1966, "employees": 33400, "description": "Provides payment processing and technology-based payment solutions."},
    {"ticker": "BAC", "name": "Bank of America Corp.", "sector": "Financial Services", "industry": "Banks", "market_cap": 330_000_000_000, "country": "US", "ceo": "Brian Moynihan", "founded_year": 1998, "employees": 213000, "description": "Provides banking and financial products and services for individual consumers and businesses."},
    {"ticker": "GS", "name": "Goldman Sachs Group", "sector": "Financial Services", "industry": "Capital Markets", "market_cap": 160_000_000_000, "country": "US", "ceo": "David Solomon", "founded_year": 1869, "employees": 45300, "description": "Provides investment banking, securities, and investment management services."},

    # Consumer Discretionary
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "industry": "Internet Retail", "market_cap": 1_900_000_000_000, "country": "US", "ceo": "Andy Jassy", "founded_year": 1994, "employees": 1541000, "description": "Engages in the retail sale of consumer products and subscriptions through online and physical stores."},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary", "industry": "Auto Manufacturers", "market_cap": 780_000_000_000, "country": "US", "ceo": "Elon Musk", "founded_year": 2003, "employees": 140473, "description": "Designs, develops, manufactures, and sells electric vehicles and energy solutions."},
    {"ticker": "NKE", "name": "Nike Inc.", "sector": "Consumer Discretionary", "industry": "Footwear & Accessories", "market_cap": 120_000_000_000, "country": "US", "ceo": "John Donahoe", "founded_year": 1964, "employees": 79400, "description": "Designs, develops, markets, and sells athletic footwear, apparel, equipment, and accessories."},
    {"ticker": "SBUX", "name": "Starbucks Corporation", "sector": "Consumer Discretionary", "industry": "Restaurants", "market_cap": 105_000_000_000, "country": "US", "ceo": "Laxman Narasimhan", "founded_year": 1971, "employees": 381000, "description": "Operates as a roaster, marketer, and retailer of specialty coffee worldwide."},
    {"ticker": "HD", "name": "The Home Depot Inc.", "sector": "Consumer Discretionary", "industry": "Home Improvement Retail", "market_cap": 350_000_000_000, "country": "US", "ceo": "Ted Decker", "founded_year": 1978, "employees": 465000, "description": "Operates as a home improvement retailer selling building materials, home improvement products, and lawn and garden products."},

    # Energy
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated", "market_cap": 460_000_000_000, "country": "US", "ceo": "Darren Woods", "founded_year": 1999, "employees": 62000, "description": "Explores, produces, transports, and sells crude oil, natural gas, and petroleum products."},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated", "market_cap": 290_000_000_000, "country": "US", "ceo": "Mike Wirth", "founded_year": 1879, "employees": 43846, "description": "Engages in integrated energy and chemicals operations worldwide."},
    {"ticker": "COP", "name": "ConocoPhillips", "sector": "Energy", "industry": "Oil & Gas E&P", "market_cap": 130_000_000_000, "country": "US", "ceo": "Ryan Lance", "founded_year": 2002, "employees": 10100, "description": "Explores for, produces, transports, and markets crude oil, natural gas, and related products."},
    {"ticker": "NEE", "name": "NextEra Energy Inc.", "sector": "Energy", "industry": "Utilities", "market_cap": 150_000_000_000, "country": "US", "ceo": "John Ketchum", "founded_year": 1925, "employees": 16800, "description": "Generates, transmits, distributes, and sells electric power in North America."},
    {"ticker": "SLB", "name": "Schlumberger Limited", "sector": "Energy", "industry": "Oil & Gas Equipment & Services", "market_cap": 65_000_000_000, "country": "US", "ceo": "Olivier Le Peuch", "founded_year": 1926, "employees": 99000, "description": "Provides technology and services for the energy industry worldwide."},
]

# Revenue ranges by market-cap tier (per quarter, in millions USD)
def _revenue_range(market_cap: int) -> tuple[float, float]:
    if market_cap > 1_000_000_000_000:
        return (40000.0, 120000.0)
    if market_cap > 300_000_000_000:
        return (15000.0, 50000.0)
    if market_cap > 100_000_000_000:
        return (5000.0, 20000.0)
    return (2000.0, 8000.0)

def _stock_base_price(market_cap: int) -> float:
    if market_cap > 2_000_000_000_000:
        return random.uniform(150, 500)
    if market_cap > 500_000_000_000:
        return random.uniform(100, 350)
    if market_cap > 100_000_000_000:
        return random.uniform(50, 200)
    return random.uniform(20, 100)


def seed():
    random.seed(42)

    # ------------------------------------------------------------------
    # 1. Insert companies
    # ------------------------------------------------------------------
    print("Inserting 25 companies...")
    result = supabase.table("companies").upsert(
        COMPANIES, on_conflict="ticker"
    ).execute()
    company_rows = result.data
    ticker_to_id = {c["ticker"]: c["id"] for c in company_rows}
    print(f"  -> {len(company_rows)} companies upserted")

    # ------------------------------------------------------------------
    # 2. Financial reports: 3 years x 4 quarters per company (300 total)
    # ------------------------------------------------------------------
    print("Generating financial reports...")
    reports = []
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    quarter_end_dates = {"Q1": "03-31", "Q2": "06-30", "Q3": "09-30", "Q4": "12-31"}

    for comp in COMPANIES:
        cid = ticker_to_id[comp["ticker"]]
        lo, hi = _revenue_range(comp["market_cap"])
        for year in [2022, 2023, 2024]:
            for q in quarters:
                revenue = round(random.uniform(lo, hi), 2)
                gross_margin = round(random.uniform(30, 75), 2)
                operating_margin = round(random.uniform(10, 45), 2)
                net_margin = random.uniform(0.08, 0.35)
                reports.append({
                    "company_id": cid,
                    "fiscal_year": year,
                    "fiscal_quarter": q,
                    "revenue": revenue,
                    "net_income": round(revenue * net_margin, 2),
                    "eps": round(random.uniform(0.5, 15.0), 4),
                    "gross_margin": gross_margin,
                    "operating_margin": operating_margin,
                    "debt_to_equity": round(random.uniform(0.1, 3.0), 3),
                    "free_cash_flow": round(revenue * random.uniform(0.05, 0.25), 2),
                    "report_date": f"{year}-{quarter_end_dates[q]}",
                })

    # Insert in batches of 100
    for i in range(0, len(reports), 100):
        supabase.table("financial_reports").upsert(
            reports[i : i + 100],
            on_conflict="company_id,fiscal_year,fiscal_quarter",
        ).execute()
    print(f"  -> {len(reports)} financial reports upserted")

    # ------------------------------------------------------------------
    # 3. Stock prices: ~65 trading days per company (Q4 2024)
    # ------------------------------------------------------------------
    print("Generating stock prices...")
    prices = []
    start_date = date(2024, 10, 1)
    for comp in COMPANIES:
        cid = ticker_to_id[comp["ticker"]]
        base = _stock_base_price(comp["market_cap"])
        current = base
        d = start_date
        while d <= date(2024, 12, 31):
            if d.weekday() < 5:  # skip weekends
                change_pct = random.gauss(0.0005, 0.018)
                current = max(1.0, current * (1 + change_pct))
                day_high = current * random.uniform(1.0, 1.03)
                day_low = current * random.uniform(0.97, 1.0)
                prices.append({
                    "company_id": cid,
                    "date": d.isoformat(),
                    "open": round(current * random.uniform(0.99, 1.01), 2),
                    "high": round(day_high, 2),
                    "low": round(day_low, 2),
                    "close": round(current, 2),
                    "volume": random.randint(5_000_000, 80_000_000),
                })
            d += timedelta(days=1)

    for i in range(0, len(prices), 200):
        supabase.table("stock_prices").upsert(
            prices[i : i + 200],
            on_conflict="company_id,date",
        ).execute()
    print(f"  -> {len(prices)} stock prices upserted")

    # ------------------------------------------------------------------
    # 4. Analyst ratings: 2-3 per company (~60 total)
    # ------------------------------------------------------------------
    print("Generating analyst ratings...")
    firms = [
        "Morgan Stanley", "Goldman Sachs", "JPMorgan",
        "Bank of America", "Barclays", "Citigroup",
        "Deutsche Bank", "UBS", "Wells Fargo", "RBC Capital",
    ]
    ratings_list = ["Buy", "Hold", "Sell", "Overweight", "Underweight"]
    ratings_weight = [0.30, 0.30, 0.10, 0.20, 0.10]
    analyst_rows = []
    for comp in COMPANIES:
        cid = ticker_to_id[comp["ticker"]]
        n_ratings = random.randint(2, 3)
        chosen_firms = random.sample(firms, n_ratings)
        for firm in chosen_firms:
            rating = random.choices(ratings_list, weights=ratings_weight, k=1)[0]
            # Pick a random previous_rating different from current
            prev_options = [r for r in ratings_list if r != rating]
            previous_rating = random.choice(prev_options)
            base_price = _stock_base_price(comp["market_cap"])
            target_mult = {"Buy": 1.25, "Overweight": 1.15, "Hold": 1.0, "Underweight": 0.85, "Sell": 0.75}
            analyst_rows.append({
                "company_id": cid,
                "analyst_firm": firm,
                "rating": rating,
                "target_price": round(base_price * target_mult[rating] * random.uniform(0.9, 1.1), 2),
                "previous_rating": previous_rating,
                "rating_date": date(2024, random.randint(9, 12), random.randint(1, 28)).isoformat(),
            })

    supabase.table("analyst_ratings").insert(analyst_rows).execute()
    print(f"  -> {len(analyst_rows)} analyst ratings inserted")

    # ------------------------------------------------------------------
    # Also dump seed.sql for fallback
    # ------------------------------------------------------------------
    _generate_seed_sql(ticker_to_id, reports, prices, analyst_rows)

    print("\nSeeding complete!")


def _generate_seed_sql(ticker_to_id, reports, prices, analyst_rows):
    """Generate a seed.sql file as a fallback for users who prefer raw SQL."""
    sql_path = Path(__file__).resolve().parent / "seed.sql"
    lines = [
        "-- ============================================================",
        "-- MCP Financial Server — Seed Data (auto-generated)",
        "-- Run AFTER schema.sql in Supabase SQL Editor",
        "-- ============================================================",
        "",
    ]

    # Companies
    lines.append("-- Companies")
    for c in COMPANIES:
        desc = c["description"].replace("'", "''") if c["description"] else ""
        name = c["name"].replace("'", "''")
        lines.append(
            f"INSERT INTO companies (ticker, name, sector, industry, market_cap, country, ceo, founded_year, employees, description) "
            f"VALUES ('{c['ticker']}', '{name}', '{c['sector']}', "
            f"'{c.get('industry', '')}', {c['market_cap']}, '{c.get('country', 'US')}', "
            f"'{c.get('ceo', '')}', {c.get('founded_year', 'NULL')}, "
            f"{c.get('employees', 'NULL')}, '{desc}') "
            f"ON CONFLICT (ticker) DO NOTHING;"
        )

    lines.append("")
    lines.append("-- Financial Reports (sample: first 10)")
    for r in reports[:10]:
        lines.append(
            f"INSERT INTO financial_reports (company_id, fiscal_year, fiscal_quarter, revenue, net_income, eps, gross_margin, operating_margin, debt_to_equity, free_cash_flow, report_date) "
            f"VALUES ('{r['company_id']}', {r['fiscal_year']}, '{r['fiscal_quarter']}', {r['revenue']}, "
            f"{r['net_income']}, {r['eps']}, {r['gross_margin']}, {r['operating_margin']}, {r['debt_to_equity']}, "
            f"{r['free_cash_flow']}, '{r['report_date']}') "
            f"ON CONFLICT (company_id, fiscal_year, fiscal_quarter) DO NOTHING;"
        )

    lines.append("")
    lines.append("-- Stock Prices (sample: first 10)")
    for p in prices[:10]:
        lines.append(
            f"INSERT INTO stock_prices (company_id, date, open, high, low, close, volume) "
            f"VALUES ('{p['company_id']}', '{p['date']}', {p['open']}, "
            f"{p['high']}, {p['low']}, {p['close']}, {p['volume']}) "
            f"ON CONFLICT (company_id, date) DO NOTHING;"
        )

    lines.append("")
    lines.append("-- Analyst Ratings (sample: first 10)")
    for a in analyst_rows[:10]:
        lines.append(
            f"INSERT INTO analyst_ratings (company_id, analyst_firm, rating, target_price, previous_rating, rating_date) "
            f"VALUES ('{a['company_id']}', '{a['analyst_firm']}', '{a['rating']}', "
            f"{a['target_price']}, '{a['previous_rating']}', '{a['rating_date']}');"
        )

    lines.append("")
    lines.append("-- NOTE: This file contains only sample rows. For full data, run seed_script.py")
    lines.append("")

    sql_path.write_text("\n".join(lines))
    print(f"  -> seed.sql written to {sql_path}")


if __name__ == "__main__":
    seed()
