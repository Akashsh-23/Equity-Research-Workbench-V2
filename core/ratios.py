def calculate_all_ratios(income_statement, balance_sheet, cash_flow):
    """
    Calculate all financial ratios from the 3 financial statements.
    Every formula is written explicitly so you can explain each one.
    """

    # Helper to safely extract a value from a DataFrame row
    def get(df, row_name, col_index=0):
        try:
            return float(df.loc[row_name].iloc[col_index])
        except:
            return 0.0

    # --- Pull raw numbers from statements ---
    revenue          = get(income_statement, "Total Revenue")
    gross_profit     = get(income_statement, "Gross Profit")
    operating_income = get(income_statement, "Operating Income")
    net_income       = get(income_statement, "Net Income")
    interest_expense = get(income_statement, "Interest Expense")

    total_assets     = get(balance_sheet, "Total Assets")
    total_equity     = get(balance_sheet, "Stockholders Equity")
    total_debt       = get(balance_sheet, "Total Debt")
    current_assets   = get(balance_sheet, "Current Assets")
    current_liab     = get(balance_sheet, "Current Liabilities")
    inventory        = get(balance_sheet, "Inventory")

    operating_cf     = get(cash_flow, "Operating Cash Flow")
    capex            = get(cash_flow, "Capital Expenditure")

    # --- Profitability Ratios ---
    gross_margin     = (gross_profit / revenue * 100)     if revenue     else 0
    operating_margin = (operating_income / revenue * 100) if revenue     else 0
    net_margin       = (net_income / revenue * 100)       if revenue     else 0
    roe              = (net_income / total_equity * 100)  if total_equity else 0
    roce             = (operating_income / (total_assets - current_liab) * 100) if (total_assets - current_liab) else 0

    # --- Liquidity Ratios ---
    current_ratio    = (current_assets / current_liab)              if current_liab else 0
    quick_ratio      = ((current_assets - inventory) / current_liab) if current_liab else 0

    # --- Leverage Ratios ---
    debt_to_equity   = (total_debt / total_equity)         if total_equity    else 0
    interest_coverage= (operating_income / abs(interest_expense)) if interest_expense else 0

    # --- Efficiency ---
    asset_turnover   = (revenue / total_assets)            if total_assets    else 0

    # --- Cash Flow ---
    free_cash_flow   = operating_cf + capex    # capex is negative in statements

    # --- Revenue growth (compare this year vs last year) ---
    revenue_prev     = get(income_statement, "Total Revenue", col_index=1)
    revenue_growth   = ((revenue - revenue_prev) / abs(revenue_prev) * 100) if revenue_prev else 0

    return {
        "Gross Margin %":       round(gross_margin, 2),
        "Operating Margin %":   round(operating_margin, 2),
        "Net Margin %":         round(net_margin, 2),
        "ROE %":                round(roe, 2),
        "ROCE %":               round(roce, 2),
        "Current Ratio":        round(current_ratio, 2),
        "Quick Ratio":          round(quick_ratio, 2),
        "Debt to Equity":       round(debt_to_equity, 2),
        "Interest Coverage":    round(interest_coverage, 2),
        "Asset Turnover":       round(asset_turnover, 2),
        "Free Cash Flow (Cr)":  round(free_cash_flow / 1e7, 2),  # Convert to Crores
        "Revenue Growth %":     round(revenue_growth, 2),
    }