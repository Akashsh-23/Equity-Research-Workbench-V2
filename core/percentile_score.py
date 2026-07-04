"""
Percentile-based Health Score — an alternative to the fixed-threshold
scoring in health_score.py.

Instead of hardcoded cutoffs ("ROE >= 20% is excellent"), this scores a
company relative to every other company in your SQLite history:
"this company's ROE beats 73% of companies you've researched."

Why this matters: fixed thresholds are sector-blind and arbitrary (why
20% and not 18%?). Percentile scoring recalibrates automatically as you
add more companies, and — when there's enough data — can compare within
the same sector instead of the whole market, which is the fairer
comparison (an IT company and an oil company don't have comparable ROE
profiles for structural reasons, not performance reasons).

Limitation (be upfront about this — it's a legitimate one): percentile
ranks are only meaningful with a reasonable sample size. Comparing
against 3 companies tells you almost nothing. We require a minimum
sample before trusting a sector-level comparison, and fall back to the
whole dataset otherwise.
"""

from core.database import get_all_snapshots

MIN_SECTOR_SAMPLE = 5     # below this, fall back to whole-dataset comparison
MIN_TOTAL_SAMPLE  = 8     # below this, percentile scoring isn't meaningful at all

# Metrics used per category, and whether higher is better (False = lower is better)
METRIC_DIRECTIONS = {
    "net_margin":        True,
    "roe":               True,
    "roce":              True,
    "current_ratio":     True,
    "quick_ratio":       True,
    "debt_to_equity":    False,   # lower debt is better
    "interest_coverage": True,
    "revenue_growth":    True,
    "free_cash_flow":    True,
}

CATEGORY_METRICS = {
    "Profitability": ["net_margin", "roe", "roce"],
    "Liquidity":     ["current_ratio", "quick_ratio"],
    "Leverage":      ["debt_to_equity", "interest_coverage"],
    "Growth":        ["revenue_growth"],
    "Cash Flow":     ["free_cash_flow"],
}

CATEGORY_WEIGHTS = {
    "Profitability": 0.30,
    "Liquidity":     0.20,
    "Leverage":      0.20,
    "Growth":        0.15,
    "Cash Flow":     0.15,
}


def _percentile_rank(value, values, higher_is_better=True):
    """
    What percentage of `values` does `value` beat?
    Returns 0-100. Pure Python, no scipy dependency needed.
    """
    values = [v for v in values if v is not None]
    if not values:
        return 50.0  # no comparison data — neutral score

    count_below = sum(1 for v in values if v < value)
    count_equal = sum(1 for v in values if v == value)
    # standard percentile-rank formula, counting ties as half-credit
    rank = (count_below + 0.5 * count_equal) / len(values) * 100

    return rank if higher_is_better else (100 - rank)


def calculate_percentile_score(ticker, snapshot_row):
    """
    Compute a percentile-based health score for one company.

    Args:
        ticker: the company's ticker, e.g. "TCS.NS"
        snapshot_row: dict with that company's ratio values
                      (same shape as a row from get_all_snapshots())

    Returns:
        dict — same shape as calculate_health_score() output, plus a
        "sample_info" key describing what it was compared against.
    """
    all_snapshots = get_all_snapshots()
    sector = snapshot_row.get("sector")

    # Use sector peers if there are enough of them, else whole dataset
    sector_peers = [s for s in all_snapshots if s.get("sector") == sector] if sector else []
    use_sector = len(sector_peers) >= MIN_SECTOR_SAMPLE
    comparison_pool = sector_peers if use_sector else all_snapshots

    sample_size = len(comparison_pool)
    sample_info = {
        "compared_against": "sector" if use_sector else "whole dataset",
        "sample_size": sample_size,
        "sector": sector if use_sector else None,
        "reliable": sample_size >= MIN_TOTAL_SAMPLE,
    }

    category_scores = {}
    for category, metrics in CATEGORY_METRICS.items():
        metric_percentiles = []
        for metric in metrics:
            value = snapshot_row.get(metric)
            if value is None:
                continue
            peer_values = [s.get(metric) for s in comparison_pool]
            higher_is_better = METRIC_DIRECTIONS[metric]
            pct = _percentile_rank(value, peer_values, higher_is_better)
            metric_percentiles.append(pct)

        category_scores[category] = (
            round(sum(metric_percentiles) / len(metric_percentiles), 1)
            if metric_percentiles else 50.0
        )

    overall = sum(
        category_scores[cat] * weight
        for cat, weight in CATEGORY_WEIGHTS.items()
    )
    overall = round(overall, 1)

    if   overall >= 80: grade = "A — Top performer in comparison group"
    elif overall >= 65: grade = "B — Above average"
    elif overall >= 50: grade = "C — Average"
    elif overall >= 35: grade = "D — Below average"
    else:               grade = "E — Bottom performer in comparison group"

    return {
        "overall_score": overall,
        "grade": grade,
        "category_scores": category_scores,
        "weights": {k: f"{int(v*100)}%" for k, v in CATEGORY_WEIGHTS.items()},
        "sample_info": sample_info,
    }
