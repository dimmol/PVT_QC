# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 21:02:01 2020

@author: molok
"""

import scipy.stats as stats
import scipy.special as sps
import pandas as pd
import numpy as np

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
    return x

excel = pd.read_csv(r'.\DATA\gamma_dist.csv', header = 0, index_col = 0)

alpha = 1.20453
ita = 135.576
ave_MC10plus = 227.594


df = gamma_dist(excel, alpha, ita, ave_MC10plus)

df.to_csv(r'.\DATA\out.csv')
