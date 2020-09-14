
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
import time

from data import data_archivos


def f_i_fechas(archivos):
    i_fechas = [i.strftime('%Y-%m-%d') for i in sorted([pd.to_datetime(l[8:]).date() for l in archivos])]
    return i_fechas

def f_tickers(archivos,data_archivos):
    tickers = []
    for i in archivos:
        l_tickers = list(data_archivos[i]['Ticker'])
        [tickers.append(i + '.MX') for i in l_tickers]
    global_tickers = np.unique(tickers).tolist()

    # ajustes de nombre de tickers
    global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
    global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
    global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers]

    # eliminar entradas de efectivo: MXN, USD, y tickers con problemas de precios: KOFL, BSMXB
    [global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX', 'KOFUBL.MX', 'BSMXB.MX']]
    return global_tickers

def f_data(global_tickers):
    inicio = time.time()
    data = yf.download(global_tickers, start="2017-08-21", end="2020-09-21", actions=False,
                       group_by="close", interval='1d', auto_adjust=False, prepost=False, threads=True)
    return data

def f_data_close(data,global_tickers):
    data_close = pd.DataFrame({i: data[i]['Close'] for i in global_tickers})
    return data_close

def f_ic_fechas(data_close,i_fechas):
    ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(i_fechas)))
    return ic_fechas

def f_precios(data_close,ic_fechas):
    precios = data_close.iloc[[int(np.where(data_close.index.astype(str) == i)[0]) for i in ic_fechas]]
    precios = precios.reindex(sorted(precios.columns), axis=1)
    return precios

def f_pos_datos(remv_activos,k,c,archivos,data_archivos,precios,ic_fechas):
    k = 1000000
    c = 0.00125
    remv_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']
    pos_datos = data_archivos[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Nombre', 'Peso (%)']]
    i_activos = list(pos_datos[pos_datos['Ticker'].isin(remv_activos)].index)
    pos_datos.drop(i_activos, inplace=True)
    pos_datos.reset_index(inplace=True, drop=True)
    pos_datos['Ticker'] = pos_datos['Ticker'] + '.MX'
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.MX', 'RA.MX')
    pos_datos['Precio'] = (np.array([precios.iloc[0, precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]))
    pos_datos['Capital'] = pos_datos['Peso (%)'] * k - pos_datos['Peso (%)'] * k * c
    pos_datos['Titulos'] = (pos_datos['Capital'] // pos_datos['Precio'])
    pos_datos['Comisiones'] = (pos_datos['Precio'] * c * pos_datos['Titulos'])
    pos_datos['Inversion'] = (pos_datos['Precio'] * pos_datos['Titulos'])
    pos_datos['timestamp'] = (ic_fechas[0])
    return pos_datos





