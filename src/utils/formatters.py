"""Response formatting helpers for MCP tool outputs."""


def format_currency(value: int | float | None) -> str:
    """Format a number as USD currency string."""
    if value is None:
        return "N/A"
    value = float(value)
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.2f}"


def format_percentage(value: float | None) -> str:
    """Format a percentage value. If value > 1, assume it's already a percentage."""
    if value is None:
        return "N/A"
    value = float(value)
    if abs(value) <= 1.0:
        return f"{value * 100:.2f}%"
    return f"{value:.2f}%"


def format_number(value: int | float | None) -> str:
    """Format a number with comma separators."""
    if value is None:
        return "N/A"
    return f"{value:,}"


def format_company_profile(company: dict) -> str:
    """Format a company dict into a readable text profile."""
    lines = [
        f"{'=' * 50}",
        f"  {company.get('name', 'Unknown')} ({company.get('ticker', '?')})",
        f"{'=' * 50}",
        f"  Sector:        {company.get('sector', 'N/A')}",
        f"  Industry:      {company.get('industry', 'N/A')}",
        f"  Market Cap:    {format_currency(company.get('market_cap'))}",
        f"  Country:       {company.get('country', 'N/A')}",
        f"  CEO:           {company.get('ceo', 'N/A')}",
        f"  Founded:       {company.get('founded_year', 'N/A')}",
        f"  Employees:     {format_number(company.get('employees'))}",
        f"",
        f"  Description:",
        f"  {company.get('description', 'No description available.')}",
        f"{'=' * 50}",
    ]
    return "\n".join(lines)


def format_financial_report(report: dict, company_name: str = "") -> str:
    """Format a financial report dict into readable text."""
    header = company_name or f"Company #{report.get('company_id', '?')}"
    lines = [
        f"--- {header} | FY{report.get('fiscal_year', '?')} {report.get('fiscal_quarter', '?')} ---",
        f"  Revenue:          {format_currency(report.get('revenue'))}",
        f"  Net Income:       {format_currency(report.get('net_income'))}",
        f"  EPS:              ${report.get('eps', 'N/A')}",
        f"  Gross Margin:     {format_percentage(report.get('gross_margin'))}",
        f"  Operating Margin: {format_percentage(report.get('operating_margin'))}",
        f"  Debt-to-Equity:   {report.get('debt_to_equity', 'N/A')}",
        f"  Free Cash Flow:   {format_currency(report.get('free_cash_flow'))}",
        f"  Report Date:      {report.get('report_date', 'N/A')}",
    ]
    return "\n".join(lines)


def format_stock_table(prices: list[dict]) -> str:
    """Format stock price rows as a text table."""
    if not prices:
        return "No stock price data available."

    header = f"{'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>14}"
    separator = "-" * len(header)
    rows = [header, separator]

    for p in prices:
        rows.append(
            f"{p.get('date', 'N/A'):<12} "
            f"${float(p.get('open', 0)):>9.2f} "
            f"${float(p.get('high', 0)):>9.2f} "
            f"${float(p.get('low', 0)):>9.2f} "
            f"${float(p.get('close', 0)):>9.2f} "
            f"{p.get('volume', 0):>14,}"
        )
    return "\n".join(rows)


def format_analyst_ratings(ratings: list[dict]) -> str:
    """Format analyst rating rows as text."""
    if not ratings:
        return "No analyst ratings available."

    lines = []
    for r in ratings:
        prev = r.get("previous_rating")
        prev_str = f" (prev: {prev})" if prev else ""
        lines.append(
            f"  [{r.get('rating', 'N/A')}] {r.get('analyst_firm', 'Unknown')}{prev_str} — "
            f"Target: ${r.get('target_price', 'N/A')} | "
            f"Date: {r.get('rating_date', 'N/A')}"
        )
    return "\n".join(lines)


def format_sector_overview(sector_stats: list[dict]) -> str:
    """Format sector aggregation results."""
    if not sector_stats:
        return "No sector data available."

    lines = []
    for s in sector_stats:
        lines.extend([
            f"\n{'=' * 40}",
            f"  Sector: {s.get('sector', 'Unknown')}",
            f"{'=' * 40}",
            f"  Companies:        {s.get('company_count', 0)}",
            f"  Avg Market Cap:   {format_currency(s.get('avg_market_cap'))}",
            f"  Total Revenue:    {format_currency(s.get('total_revenue'))}",
            f"  Avg Margin:       {format_percentage(s.get('avg_margin'))}",
            f"  Avg Rating Score: {s.get('avg_rating_score', 'N/A')} / 5.0",
        ])
    return "\n".join(lines)


def format_comparison(results: list[dict]) -> str:
    """Format company comparison results with requested metrics."""
    if not results:
        return "No companies to compare."

    metrics = results[0].get("requested_metrics", ["revenue", "net_income", "eps", "gross_margin"])

    # Build header
    metric_labels = {
        "revenue": "Revenue",
        "net_income": "Net Income",
        "eps": "EPS",
        "gross_margin": "Gross Margin",
        "operating_margin": "Op. Margin",
        "debt_to_equity": "D/E Ratio",
        "free_cash_flow": "FCF",
        "market_cap": "Market Cap",
    }

    header_parts = [f"{'Ticker':<8} {'Name':<30}"]
    for m in metrics:
        header_parts.append(f"{metric_labels.get(m, m):>14}")
    header = " ".join(header_parts)

    lines = [f"Company Comparison ({len(results)} companies)\n", header, "-" * len(header)]

    for comp in results:
        fin = comp.get("latest_financials") or {}
        parts = [f"{comp['ticker']:<8} {comp['name'][:28]:<30}"]
        for m in metrics:
            if m == "market_cap":
                val = comp.get("market_cap")
                parts.append(f"{format_currency(val):>14}")
            elif m in ("gross_margin", "operating_margin"):
                val = fin.get(m)
                parts.append(f"{format_percentage(float(val) if val is not None else None):>14}")
            elif m in ("revenue", "net_income", "free_cash_flow"):
                val = fin.get(m)
                parts.append(f"{format_currency(float(val) if val is not None else None):>14}")
            elif m == "eps":
                val = fin.get("eps", "N/A")
                parts.append(f"{'$' + str(val):>14}")
            elif m == "debt_to_equity":
                val = fin.get("debt_to_equity", "N/A")
                parts.append(f"{str(val):>14}")
            else:
                parts.append(f"{'N/A':>14}")
        lines.append(" ".join(parts))

    return "\n".join(lines)
