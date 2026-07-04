"""SQLite persistence layer for company ratio snapshots."""

import sqlite3
import os
from datetime import datetime

DB_PATH = "data/workbench.db"


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the snapshots table if it doesn't exist yet. Safe to call every app start."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker          TEXT NOT NULL,
            name            TEXT,
            sector          TEXT,
            industry        TEXT,
            snapshot_date   TEXT NOT NULL,

            gross_margin    REAL,
            operating_margin REAL,
            net_margin      REAL,
            roe             REAL,
            roce            REAL,
            current_ratio   REAL,
            quick_ratio     REAL,
            debt_to_equity  REAL,
            interest_coverage REAL,
            asset_turnover  REAL,
            free_cash_flow  REAL,
            revenue_growth  REAL,
            updated_at      TEXT,
            UNIQUE(ticker, snapshot_date)
        )
    """)

    conn.commit()
    conn.close()


def save_snapshot(ticker, info, ratios):
    """Insert or refresh today's snapshot for this ticker."""
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT OR REPLACE INTO snapshots (
            id, ticker, name, sector, industry, snapshot_date,
            gross_margin, operating_margin, net_margin, roe, roce,
            current_ratio, quick_ratio, debt_to_equity, interest_coverage,
            asset_turnover, free_cash_flow, revenue_growth, updated_at
        ) VALUES (
            (SELECT id FROM snapshots WHERE ticker = ? AND snapshot_date = ?),
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        ticker, today,
        ticker, info.get("name"), info.get("sector"), info.get("industry"), today,
        ratios.get("Gross Margin %"), ratios.get("Operating Margin %"),
        ratios.get("Net Margin %"), ratios.get("ROE %"), ratios.get("ROCE %"),
        ratios.get("Current Ratio"), ratios.get("Quick Ratio"),
        ratios.get("Debt to Equity"), ratios.get("Interest Coverage"),
        ratios.get("Asset Turnover"), ratios.get("Free Cash Flow (Cr)"),
        ratios.get("Revenue Growth %"), now,
    ))

    conn.commit()
    conn.close()


def get_latest_snapshot(ticker):
    """Most recent snapshot row for one ticker, or None if never searched before."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM snapshots WHERE ticker = ? ORDER BY snapshot_date DESC, id DESC LIMIT 1",
        (ticker,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_snapshots():
    """Every snapshot row (all tickers, all dates). Used as the percentile comparison pool."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM snapshots ORDER BY snapshot_date DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_snapshot_per_ticker():
    """One row per ticker — the most recent snapshot. Used by Compare/Leaderboard."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.* FROM snapshots s
        WHERE s.id = (
            SELECT id FROM snapshots s2
            WHERE s2.ticker = s.ticker
            ORDER BY s2.snapshot_date DESC, s2.id DESC
            LIMIT 1
        )
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_snapshot_history(ticker):
    """All historical snapshots for one ticker, oldest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM snapshots WHERE ticker = ? ORDER BY snapshot_date ASC",
        (ticker,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
