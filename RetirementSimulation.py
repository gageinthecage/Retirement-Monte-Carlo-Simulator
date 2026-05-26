import numpy as np

#16.76 = annulized volatility & 8.5% returns

def  S_T(r,o,t):
    Z = np.random.randn()
    result = np.exp((r-o**2/2)*t+o * np.sqrt(t)*Z)
    return result

#Target is the amount of money the consumer wants, portfolio is the updating money gained#

def Retire_Simulate(simulations, target, starting, monthly):
    r = .085
    o = .167
    t = 1/12
    months = []
    for i in range(simulations):
        m = 0
        portfolio = starting
        months.append(m)
        while portfolio < target and m < 9600:
            growth = S_T(r,o,t)
            portfolio = portfolio * growth
            portfolio = portfolio + monthly
            m = m + 1
    return sum(months) / len(months)




