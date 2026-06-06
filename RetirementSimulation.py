#The algorithm that generates the simulated SMP returns#

import numpy as np
import statistics

#Blach Scholes model that generates a random growth pattern#

def  S_T(r,o,t):
    Z = np.random.randn()
    result = np.exp((r-o**2/2)*t+o * np.sqrt(t)*Z)
    return result

#Target is the amount of money the consumer wants, portfolio is the updating money gained#

def Retire_Simulate(simulations, target, starting, monthly):
#Fixed rates from Annual SMP data#
    simulations = 2000
    r = 0.105
    o = 0.175
    t = 1/12

    months = []
    paths = []

    for i in range(simulations):
        m = 0
        portfolio = starting
        path = [portfolio]
        while portfolio < target and m < 720:

#Random growth applied to the portfolio and monthly contribution added#
        
            growth = S_T(r,o,t)
            portfolio = portfolio * growth
            portfolio = portfolio + monthly
            m = m + 1
            path.append(portfolio)
        months.append(m)
        paths.append(path)

# Finding Median and Quartiles

    median = statistics.median(months)
    sort = sorted(months)
    t1 = sort[int(.9*len(months))]
    b1 = sort[int(.1*len(months))]

# Finding Success rate Percentage

    success_rate=(sum(1 for m in months if m < 720)/len(months)) * 100

    simulations = 2000

    average = sum(months)/len(months)

    return {
        "avg_months": average,
        "median_months": median,
        "num_simulations": simulations,
        "success_rate": success_rate,
        "bottom_10_months": b1,
        "top_10_months": t1,
        "all_months": months,
        "all_paths": paths  # frontend uses this for plotting
    }
