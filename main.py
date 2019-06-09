import matplotlib as mpl
import pandas as pd
import numpy as np
from scipy.stats import norm
import math


frame = pd.read_csv("csv/SI_D_ROPC.txt", sep="|", header=None, skiprows=1,
                    parse_dates=[3], 
                    names=["?", "stock", "stock type", "exercise date", "??", "???",
                           "series", "????", "strike price", "?????", "covered",
                           "uncovered", "total", "owner", "releaser", "??????",
                           "option type"])

frame[frame["stock"]=="PETR"].sort_values(by=["exercise date", "series"])
frame.filter(["stock", "exercise date", "series", "strike price"])
frame["call"] = frame["series"].str.get(4) < "L"



def implied_volatility(target_value, call, s, k, t, r):
    limit = 100
    max_error = 1.0e-5
    sigma = 0.5

    for i in range(0, limit):
        price = bs(call, s, k, t, r, sigma)
        vega = vega(call, s, k, t, r, sigma)

        diff = target_value - price

        if (abs(diff) < max_error):
            return sigma
        sigma = sigma + diff/vega

    return sigma

def bs(call, s, k, t, r, v, q=0.0) -> float:
    d1 = (math.log(s / k) + (r + 0.5 * v**2) * t) / (v * math.sqrt(t))
    d2 = d1 - v * math.sqrt(t)
    if call:
        price = s * math.exp(-q * t) * norm.cdf(d1) \
                - k * math.exp(-r * t) * norm.cdf(d2)
    else:
        price = k * math.exp(-r * t) * norm.cdf(-d2) \
                - s * math.exp(-q * t) * norm.cdf(-d1)
    return price

def vega(s, k, t, r, v) -> float:
    d1 = (math.log(s / k) + (r + 0.5 * v**2) * t) / (v * math.sqrt(t))
    return s * math.sqrt(t) * norm.pdf(d1)
