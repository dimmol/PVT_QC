# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 11:55:47 2020

@author: molok
"""

import scipy.stats as stats
import scipy.special as sps
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

# alpha = 1.205
# ita = 135.576
# ave_MC10plus = 227.594

def gamma_dist(x, alpha, ita, ave_MC10plus):
    
    betha = (ave_MC10plus-ita)/alpha
    x.at[9,'ubound'] = ita
    x['y'] = (x['ubound']-ita)/betha
    x['Q'] = np.exp(-x['y'])*(x['y']**alpha)/sps.gamma(alpha)
    x['P0'] = stats.gamma.cdf((x['ubound']-ita), a=alpha, scale=betha)
    x['P1'] = x['P0']-(x['Q']/alpha)
    x['Mi'] = ita+alpha*betha*((x['P1']-x['P1'].shift())/(x['P0']-x['P0'].shift()))
    x['Wi'] = x['Mi'] * (x['P0']-x['P0'].shift())
    x['Wni'] = x['Wi']/x['Wi'].sum(skipna = True)
    return x.iloc[1:,-1]

excel = pd.read_csv(r'.\DATA\gamma_dist.csv', header = 0, index_col = 0)
x_inp = excel.iloc[:-1, [0]]
y_inp = excel.iloc[1:-1, -1]


alpha = 1.0
ita = 110*(1-(1/(1+(4.043/(alpha**0.723)))))
ave_MC10plus = 200

best_vals, covar = curve_fit(gamma_dist, x_inp, y_inp, p0=[alpha, ita, ave_MC10plus], maxfev=100000)

print('best_vals: {}'.format(best_vals))

df = gamma_dist(x_inp, best_vals[0], best_vals[1], best_vals[2])

print(pd.DataFrame(dict(Lab = y_inp, Fit = df)).reset_index())
