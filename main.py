import matplotlib as mpl
import pandas as pd
import numpy as np
import scipy.stats


frame = pd.read_csv("csv/SI_D_ROPC.txt", sep="|", header=None, skiprows=1,
                    parse_dates=[3], 
                    names=["?", "stock", "stock type", "exercise date", "??", "???",
                           "series", "????", "strike price", "?????", "covered",
                           "uncovered", "total", "owner", "releaser", "??????",
                           "option type"])

# frame[frame["stock"]=="PETR"].sort_values(by=["exercise date", "series"])
