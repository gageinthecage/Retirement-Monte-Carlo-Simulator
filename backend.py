import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from RetirementSimulation import Retire_Simulate

app = FastAPI(title="Retirement Simulator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Retirement Simulator API is running"}


@app.post("/simulate")
def simulate(starting: float, monthly: float, target: float):
    if starting < 0 or monthly < 0 or target <= 0:
        raise HTTPException(status_code=400, detail="Invalid parameters")

    raw = Retire_Simulate(2000, target, starting, monthly)

    all_months = raw["all_months"]
    all_paths  = raw["all_paths"]
    n_sims     = raw["num_simulations"]
    months_arr = np.array(all_months)

    # ── Individual paths for the chart (120 paths, quarterly sampling) ──────
    n_display = min(120, len(all_paths))
    individual_paths = []

    for i in range(n_display):
        fm   = all_months[i]
        path = all_paths[i]

        # Sample every 3rd month (quarterly) to keep payload small
        indices = list(range(0, len(path), 3))
        values  = [path[j] for j in indices]
        years   = [round(j / 12, 3) for j in indices]

        # percentile_rank: % of ALL simulations that took longer (higher = faster)
        slower = int(np.sum(months_arr > fm))
        prank  = round(slower / n_sims * 100, 1)

        individual_paths.append({
            "values":       values,
            "years":        years,
            "final_year":   round(fm / 12, 2) if fm < 720 else None,
            "percentile_rank": prank,
        })

    # ── Histogram of retirement years ────────────────────────────────────────
    max_year = 60
    counts   = [0] * (max_year + 1)
    for m in all_months:
        yr = int(m / 12)
        if yr <= max_year:
            counts[yr] += 1

    # ── Summary stats ────────────────────────────────────────────────────────
    successful = [m for m in all_months if m < 720]
    yrs = np.array(successful) / 12 if successful else np.array([0.0])

    stats = {
        "median_years": float(np.median(yrs)),
        "p10_years":    float(np.percentile(yrs, 10)),
        "p25_years":    float(np.percentile(yrs, 25)),
        "p75_years":    float(np.percentile(yrs, 75)),
        "p90_years":    float(np.percentile(yrs, 90)),
    }

    return {
        "success_rate":     raw["success_rate"],
        "individual_paths": individual_paths,
        "bands":            None,
        "months_axis":      None,
        "histogram":        {"counts": counts, "years": list(range(max_year + 1))},
        "stats":            stats,
        "y_max":            None,
        "n_simulations":    n_sims,
        "parameters":       {"annual_return_pct": 10.5, "annual_volatility_pct": 17.5},
    }
