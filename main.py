
from fastapi import FastAPI
from RetirementSimulation import Retire_Simulate


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Retirement Simulator API is running"}

@app.post("/simulate")
def simulate(target:float, starting:float, monthly:float):
    result = Retire_Simulate(10000, target, starting, monthly)
    return {"average years": result}
