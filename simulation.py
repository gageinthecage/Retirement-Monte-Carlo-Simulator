import numpy as np

SP500_ANNUAL_RETURN = 0.105      # 10.5% historical nominal average
SP500_ANNUAL_VOLATILITY = 0.175  # 17.5% historical standard deviation


def S_T(S, r, o, t):
    """Single geometric Brownian motion step."""
    Z = np.random.randn()
    return S * np.exp((r - o ** 2 / 2) * t + o * np.sqrt(t) * Z)


def Retire_Simulate(starting_amount, monthly_contribution, retirement_target,
                    r=SP500_ANNUAL_RETURN, o=SP500_ANNUAL_VOLATILITY,
                    n_simulations=1000, max_years=40):
    """
    Vectorized Monte Carlo retirement simulation using GBM.

    Simulates n_simulations independent portfolio paths, each stepping
    month-by-month and adding monthly_contribution each period.
    Returns percentile bands, a retirement-year histogram, and summary stats.
    """
    if starting_amount >= retirement_target:
        return _already_retired(starting_amount, n_simulations, r, o)

    dt = 1 / 12
    max_months = max_years * 12

    # All random shocks at once: (n_simulations, max_months)
    Z = np.random.randn(n_simulations, max_months)
    monthly_returns = np.exp((r - o ** 2 / 2) * dt + o * np.sqrt(dt) * Z)

    # Build portfolio paths: (n_simulations, max_months + 1)
    portfolios = np.zeros((n_simulations, max_months + 1))
    portfolios[:, 0] = starting_amount
    for month in range(1, max_months + 1):
        portfolios[:, month] = (
            portfolios[:, month - 1] * monthly_returns[:, month - 1]
            + monthly_contribution
        )

    # First month each simulation crosses the target
    exceeded = portfolios >= retirement_target
    retirement_months = []
    for i in range(n_simulations):
        idx = int(np.argmax(exceeded[i]))
        retirement_months.append(idx if exceeded[i, idx] else None)

    # Percentile bands sampled every 3 months to limit payload size
    step = 3
    sample_idx = np.arange(0, max_months + 1, step)
    sampled = portfolios[:, sample_idx]
    bands = {
        f"p{p}": np.percentile(sampled, p, axis=0).tolist()
        for p in [10, 25, 50, 75, 90]
    }
    months_axis = sample_idx.tolist()

    # Y-axis cap: 97th percentile of final values to suppress extreme outliers
    y_max = float(np.percentile(portfolios[:, -1], 97))

    # Individual paths for visualization (quarterly sampling)
    n_display = min(120, n_simulations)
    q_step = 3
    q_idx = np.arange(0, max_months + 1, q_step)
    sampled_display = portfolios[:n_display, q_idx]

    retirement_months_arr = np.array(
        [m if m is not None else (max_months + 1) for m in retirement_months]
    )

    individual_paths = []
    for i in range(n_display):
        fm = retirement_months[i]
        if fm is not None:
            slower_count = int(np.sum(retirement_months_arr > fm))
            prank = round(slower_count / n_simulations * 100, 1)
            # Truncate path at the quarterly sample just after retirement
            n_quarters = min((fm // q_step) + 2, len(q_idx))
            values = sampled_display[i, :n_quarters].tolist()
            years = [round(q_idx[j] / 12, 3) for j in range(n_quarters)]
        else:
            prank = 0.0
            values = sampled_display[i].tolist()
            years = [round(q_idx[j] / 12, 3) for j in range(len(q_idx))]
        individual_paths.append({
            "values": values,
            "years": years,
            "final_year": round(fm / 12, 2) if fm is not None else None,
            "percentile_rank": prank,
        })

    # Retirement statistics
    successful = [m for m in retirement_months if m is not None]
    success_rate = len(successful) / n_simulations * 100

    if successful:
        years = [m / 12 for m in successful]
        bins = np.arange(0, max_years + 2, 1)
        hist, _ = np.histogram(years, bins=bins)
        histogram = {"counts": hist.tolist(), "years": list(range(max_years + 1))}
        stats = {
            "median_years": float(np.median(years)),
            "p10_years":    float(np.percentile(years, 10)),
            "p25_years":    float(np.percentile(years, 25)),
            "p75_years":    float(np.percentile(years, 75)),
            "p90_years":    float(np.percentile(years, 90)),
        }
    else:
        histogram = {"counts": [0] * (max_years + 1), "years": list(range(max_years + 1))}
        stats = {}

    return {
        "success_rate":     success_rate,
        "bands":            bands,
        "months_axis":      months_axis,
        "individual_paths": individual_paths,
        "histogram":        histogram,
        "stats":            stats,
        "y_max":            y_max,
        "n_simulations":    n_simulations,
        "parameters": {
            "annual_return_pct":     round(r * 100, 1),
            "annual_volatility_pct": round(o * 100, 1),
        },
    }


def _already_retired(starting_amount, n_simulations, r, o):
    return {
        "success_rate":  100.0,
        "bands":         {f"p{p}": [starting_amount, starting_amount] for p in [10, 25, 50, 75, 90]},
        "months_axis":   [0, 1],
        "histogram":     {"counts": [n_simulations], "years": [0]},
        "stats":         {k: 0.0 for k in ["median_years", "p10_years", "p25_years", "p75_years", "p90_years"]},
        "y_max":         starting_amount * 1.5,
        "n_simulations": n_simulations,
        "parameters":    {"annual_return_pct": round(r * 100, 1), "annual_volatility_pct": round(o * 100, 1)},
    }
