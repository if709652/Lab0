
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""


from datetime import datetime
import time
import numpy as np
import pandas as pd
import yfinance as yf
from os import listdir, path
from os.path import isfile, join
import math
import functions as fn
from data import archivos, data_archivos

abspath = path.abspath('Archivos/NAFTRAC_holdings')
i_fechas = fn.f_i_fechas(archivos)
global_tickers=fn.f_tickers(archivos,data_archivos)
data=fn.f_data(global_tickers)
data_close=fn.f_data_close(data,global_tickers)
ic_fechas=fn.f_ic_fechas(data_close,i_fechas)
precios=fn.f_precios(data_close,ic_fechas)

inv_pasiva = {'timestamp': ['30-01-2018'], 'Capital': [k]}
pos_datos=fn.f_pos_datos(remv_activos,k,c,archivos,data_archivos,precios,ic_fechas)


