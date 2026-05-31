from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from RetirementSimulation import Retire_Simulate

app = FastAPI()

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
def simulate(target:float, starting:float, monthly:float):
    result = Retire_Simulate(10000, target, starting, monthly)
    return {"average years": result}
