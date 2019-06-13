import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import re
from scipy.stats import norm
from bs4 import BeautifulSoup
from datetime import datetime
from mpl_toolkits.mplot3d import Axes3D

def implied_volatility(v, call, s, k, t, r):
    limit = 100
    max_error = 1.0e-5
    sigma = 0.5
    t = (frame["exercise date"][0] - datetime.today()).days

    for i in range(0, limit):
        price = bs(call, s, k, t, r, sigma)
        veg = vega(s, k, t, r, sigma)

        diff = v - price

        if (abs(diff) < max_error):
            return sigma
        sigma = sigma + diff/veg

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

frame = pd.read_csv("csv/SI_D_ROPC.txt", sep="|", header=None, skiprows=1,
                    parse_dates=[3], 
                    names=["?", "stock", "stock type", "exercise date", "??", "???",
                           "series", "????", "strike price", "?????", "covered",
                           "uncovered", "total", "owner", "releaser", "??????",
                           "option type"])

frame[frame["stock"]=="PETR"].sort_values(by=["exercise date", "series"])
frame = frame.filter(["stock", "exercise date", "series", "strike price"])
frame["call"] = frame["series"].str.get(4) < "L"

with open("html/Opções de compra | Valor Econômico.html") as f:
    html_string = f.read()
soup = BeautifulSoup(html_string, 'lxml')
table = soup.find_all('table')[0]
rows = table.find_all('tr', {'class': 'row'})[2:] # skip first 2 rows

# regexp = r"^([A-Z]{5}\d+)([A-Z]{4})\s+[O|P|N]{2,4}([a-z]{3}/\d{2})(\d+.\d+)-*(\d+.\d+)"
regexp = r"([A-Z]+\d+)([A-Z]{4}).*([a-z]{3}\/\d{2})(\d{1,2}\,\d{2})[\d]+\,[\d]{2}[\d]+\,[\d]{2}[\d]+\,[\d]{2}([\d]+\,[\d]{2})"

quotes = []
for i in rows:
    try:
        x = re.search(regexp, i.get_text())
        quotes.append(x.groups())
    except AttributeError:
        continue
        
frame["option price"] = 0.0
for q in quotes:
    frame.loc[frame["series"]==q[0], "option price"] = float(q[4].replace(",", "."))

frame['implied volatility'] = frame.apply(lambda x: implied_volatility(x['option price'],
                                                                       x['call'],
                                                                       29.85,
                                                                       x['strike price'],
                                                                       x['exercise date'],
                                                                       0.065), axis=1)

frame[(frame["stock"]=="PETR") & (frame["exercise date"]=='2019-06-17')].plot(x="strike price", y="implied volatility", kind="scatter")

frame[(frame["stock"]=="PETR") & (frame["exercise date"]=='2019-08-19')].plot(x="strike price", y="implied volatility", kind="scatter")

frame[(frame["stock"]=="PETR") & (frame["exercise date"]=='2020-01-20')].plot(x="strike price", y="implied volatility", kind="scatter")

fig = plt.figure().gca(projection='3d')
fig.scatter(frame[(frame["stock"]=="PETR")]["strike price"],
            [(x - datetime.today()).days for x in frame[(frame["stock"]=="PETR")]["exercise date"]],
            frame[(frame["stock"]=="PETR")]["implied volatility"])
fig.set_xlabel('strike price')
fig.set_ylabel('time left until exercise')
fig.set_zlabel('implied volatility')
plt.show()
