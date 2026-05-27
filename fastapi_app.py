from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from simulation import Retire_Simulate

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
    if starting <= 0 or target <= 0 or monthly < 0:
        raise HTTPException(status_code=400, detail="Invalid parameters")
    result = Retire_Simulate(
        starting_amount=starting,
        monthly_contribution=monthly,
        retirement_target=target,
        n_simulations=2000,
        max_years=60,
    )
    return result
