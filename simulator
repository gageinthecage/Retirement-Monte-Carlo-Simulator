#The algorithm that generates the simulated SMP returns#

import numpy as np

#Blach Scholes model that generates a random growth pattern#

def  S_T(r,o,t):
    Z = np.random.randn()
    result = np.exp((r-o**2/2)*t+o * np.sqrt(t)*Z)
    return result

#Target is the amount of money the consumer wants, portfolio is the updating money gained#

def Retire_Simulate(simulations, target, starting, monthly):
    portfolio = starting

#Fixed rates from Annual SMP data#
    
    r = 0.105
    o = 0.175
    t = 1/12

    months = []


    for i in range(simulations):
        m = 0
        portfolio = starting
        months.append(m)
        while portfolio < target and m < 9600:

#Random growth applied to the portfolio and monthly contribution added#
        
            growth = S_T(r,o,t)
            portfolio = portfolio * growth
            portfolio = portfolio + monthly
            m = m + 1
            
    return sum(months) / len(months)

    
