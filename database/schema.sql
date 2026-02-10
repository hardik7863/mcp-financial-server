-- ============================================================
-- MCP Financial Server — Database Schema
-- Run this in the Supabase SQL Editor to create all tables
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Companies
CREATE TABLE IF NOT EXISTS companies (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker        VARCHAR(10)  NOT NULL UNIQUE,
    name          VARCHAR(255) NOT NULL,
    sector        VARCHAR(100) NOT NULL,
    industry      VARCHAR(100),
    market_cap    BIGINT,
    country       VARCHAR(50),
    founded_year  INT,
    ceo           VARCHAR(255),
    employees     INT,
    description   TEXT,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies (ticker);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies (sector);
CREATE INDEX IF NOT EXISTS idx_companies_name   ON companies (name);

-- 2. Financial Reports (quarterly & annual)
CREATE TABLE IF NOT EXISTS financial_reports (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id      UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    fiscal_year     INT          NOT NULL,
    fiscal_quarter  VARCHAR(5)   NOT NULL CHECK (fiscal_quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    revenue         NUMERIC(15,2),
    net_income      NUMERIC(15,2),
    eps             NUMERIC(8,4),
    gross_margin    NUMERIC(5,2),
    operating_margin NUMERIC(5,2),
    debt_to_equity  NUMERIC(6,3),
    free_cash_flow  NUMERIC(15,2),
    report_date     DATE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (company_id, fiscal_year, fiscal_quarter)
);

CREATE INDEX IF NOT EXISTS idx_financial_reports_company ON financial_reports (company_id);
CREATE INDEX IF NOT EXISTS idx_financial_reports_year    ON financial_reports (fiscal_year);

-- 3. Stock Prices (daily)
CREATE TABLE IF NOT EXISTS stock_prices (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id  UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    date        DATE         NOT NULL,
    open        NUMERIC(10,2),
    high        NUMERIC(10,2),
    low         NUMERIC(10,2),
    close       NUMERIC(10,2),
    volume      BIGINT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (company_id, date)
);

CREATE INDEX IF NOT EXISTS idx_stock_prices_company_date ON stock_prices (company_id, date DESC);

-- 4. Analyst Ratings
CREATE TABLE IF NOT EXISTS analyst_ratings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id      UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    analyst_firm    VARCHAR(255) NOT NULL,
    rating          VARCHAR(20)  NOT NULL CHECK (rating IN (
                        'Buy', 'Hold', 'Sell', 'Overweight', 'Underweight'
                    )),
    target_price    NUMERIC(10,2),
    previous_rating VARCHAR(20),
    rating_date     DATE         NOT NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyst_ratings_company ON analyst_ratings (company_id);

-- ============================================================
-- RPC Function: get_sector_stats
-- Returns aggregated stats per sector for get_sector_overview
-- ============================================================
CREATE OR REPLACE FUNCTION get_sector_stats(target_sector TEXT DEFAULT NULL)
RETURNS TABLE (
    sector          TEXT,
    company_count   BIGINT,
    avg_market_cap  NUMERIC,
    total_revenue   NUMERIC,
    avg_margin      NUMERIC,
    avg_rating_score NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.sector::TEXT,
        COUNT(DISTINCT c.id)                                     AS company_count,
        ROUND(AVG(c.market_cap), 0)                              AS avg_market_cap,
        COALESCE(SUM(fr.revenue), 0)                             AS total_revenue,
        ROUND(AVG(fr.operating_margin), 2)                       AS avg_margin,
        ROUND(AVG(
            CASE ar.rating
                WHEN 'Buy'         THEN 5
                WHEN 'Overweight'  THEN 4
                WHEN 'Hold'        THEN 3
                WHEN 'Underweight' THEN 2
                WHEN 'Sell'        THEN 1
            END
        ), 2)                                                    AS avg_rating_score
    FROM companies c
    LEFT JOIN LATERAL (
        SELECT fr2.revenue, fr2.operating_margin
        FROM financial_reports fr2
        WHERE fr2.company_id = c.id
        ORDER BY fr2.fiscal_year DESC, fr2.fiscal_quarter DESC
        LIMIT 1
    ) fr ON TRUE
    LEFT JOIN analyst_ratings ar ON ar.company_id = c.id
    WHERE (target_sector IS NULL OR c.sector = target_sector)
    GROUP BY c.sector;
END;
$$;
