
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
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

pd.set_option('display.max_rows', None)                   # sin limite de renglones maximos
pd.set_option('display.max_columns', None)                # sin limite de columnas maximas
pd.set_option('display.width', None)                      # sin limite el ancho del display
pd.set_option('display.expand_frame_repr', False)         # visualizar todas las columnas

# -------------------------------------------------------------------------------------------- PASO 1.1  -- #
# -- Obtener la lista de los archivos a leer

# obtener la ruta absoluta de la carpeta donde estan los archivos
abspath = path.abspath('Archivos/NAFTRAC_holdings')
# obtener una lista de todos los archivos en la carpeta (quitandole la extension de archivo)
# no tener archivos abiertos al mismo tiempo que correr la siguiente linea, error por ".~loc.archivo"
archivos = [f[:-4] for f in listdir(abspath) if isfile(join(abspath, f))]
archivos = sorted(archivos, key=lambda t: datetime.strptime(t[8:], '%d%m%y'))
# --------------------------------------------------------------------------------------------- PASO 1.2 -- #
# -- Leer todos los archivos y guardarlos en un diccionario

# crear un diccionario para almacenar todos los datos
data_archivos = {}

for i in archivos:
    # leer archivos despues de los primeros dos renglones
    data = pd.read_csv('Archivos/NAFTRAC_holdings/' + i + '.csv', skiprows=2, header=None)
    # renombrar las columnas con lo que tiene el 1er renglon
    data.columns = list(data.iloc[0, :])
    # quitar columnas que no sean nan
    data = data.loc[:, pd.notnull(data.columns)]
    # resetear el indice
    data = data.iloc[1:-1].reset_index(drop=True, inplace=False)
    # quitar las comas en la columna de precios
    data['Precio'] = [i.replace(',', '') for i in data['Precio']]
    # quitar el asterisco de columna ticker
    data['Ticker'] = [i.replace('*', '') for i in data['Ticker']]
    # hacer conversiones de tipos de columnas a numerico
    convert_dict = {'Ticker': str, 'Nombre': str, 'Peso (%)': float, 'Precio': float}
    data = data.astype(convert_dict)
    # convertir a decimal la columna de peso (%)
    data['Peso (%)'] = data['Peso (%)']/100
    # guardar en diccionario
    data_archivos[i] = data

# --------------------------------------------------------------------------------------------- PASO 1.3 -- #
# -- Construir el vector de fechas a partir del vector de nombres de archivos

# estas serviran como etiquetas en dataframe y para yfinance
i_fechas = [i.strftime('%Y-%m-%d') for i in sorted([pd.to_datetime(l[8:]).date() for l in archivos])]

# --------------------------------------------------------------------------------------------- PASO 1.4 -- #
# -- Construir el vector de tickers utilizables en yahoo finance

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
[global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX','KOFUBL.MX', 'BSMXB.MX']]

# --------------------------------------------------------------------------------------------- PASO 1.5 -- #
# -- Descargar y acomodar todos los precios historicos

# para contar tiempo que se tarda
inicio = time.time()

# descarga masiva de precios de yahoo finance
data = yf.download(global_tickers, start="2017-08-21", end="2020-09-21", actions=False,
                   group_by="close", interval='1d', auto_adjust=False, prepost=False, threads=True)

# tiempo que se tarda
print('se tardo', round(time.time() - inicio, 2), 'segundos')

#convertir columna de fechas
data_close= pd.DataFrame({i: data[i]['Close'] for i in global_tickers})

# tomar solo las fechas de interes
ic_fechas=sorted(list(set(data_close.index.astype(str).tolist()) & set(i_fechas)))
#Localizar todos los precios
precios=data_close.iloc[[int(np.where(data_close.index.astype(str)==i)[0]) for i in ic_fechas]]
#Ordenar precios Lexicograficamente
precios=precios.reindex(sorted(precios.columns), axis=1)


# capital inicial
k = 1000000
# comisiones por transaccion
c = 0.00125

remv_activos = ['KOFL','KOFUBL', 'BSMXB', 'MXN', 'USD']

inv_pasiva = {'timestamp': ['30-01-2018'], 'Capital': [k]}

pos_datos = data_archivos[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Nombre', 'Peso (%)']]

#Extraer los activos a eliminar
i_activos = list(pos_datos[pos_datos['Ticker'].isin(remv_activos)].index)

#Eliminar los activos del Data
pos_datos.drop(i_activos, inplace=True)

#resetear index
pos_datos.reset_index(inplace=True, drop=True)

#Agregar .MX para empatar precios
pos_datos['Ticker'] = pos_datos['Ticker'] + '.MX'

#Corregir  ticker  en datos
pos_datos['Ticker'] = pos_datos['Ticker'].replace('LIVEPOLC.1.MX','LIVEPOLC-1.MX')
pos_datos['Ticker'] = pos_datos['Ticker'].replace('MEXCHEM.MX','ORBIA.MX')
pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.MX','RA.MX')

# ----------------------------------------------------------
# ----------------------------------- PASO 1.6 -- #
# -- Obtener posiciones historicas
pos_datos['Precio'] = (np.array([precios.iloc[0, precios.columns.to_list().index(i)] for i in pos_datos['Ticker']]))
pos_datos['Capital']=pos_datos['Peso (%)']*k-pos_datos['Peso (%)']*k*c
#Cantidad de titulos por accion
pos_datos['Titulos']=(pos_datos['Capital']//pos_datos['Precio'])
pos_datos['Comisiones']=(pos_datos['Precio']*c*pos_datos['Titulos'])
# Capital es en dinero lo que gastaste en activos sin comision
pos_datos['Inversion']=(pos_datos['Precio']*pos_datos['Titulos'] )
pos_datos['timestamp']=(ic_fechas[0])
#cantidad de dinero que tienes que tienes invertido en $

#Obtencion de lo que me sobro despues de invertir
cash_final=k-pos_datos['Inversion'].sum()-pos_datos['Comisiones'].sum()
cash_final=np.round(cash_final)


#Lo tenemos que hacer para todos los meses pero ahora no hay comisiones
for i in range(len(sorted(list(set(ic_fechas))))):
    pos_datos['Precio'] = np.array([precios.iloc[i, precios.columns.to_list().index(j)] for j in pos_datos['Ticker']])
    pos_datos['Comisiones']=0
    pos_datos['Inversion'] = (pos_datos['Precio'] * pos_datos['Titulos'])
    inv_pasiva['timestamp'].append(ic_fechas[i])
    inv_pasiva['Capital'].append(sum(pos_datos['Inversion'])+cash_final)


inv_pfinal = pd.DataFrame()
inv_pfinal['timestamp']=inv_pasiva['timestamp']
#inv_pfinal['Inversion']=inv_pasiva['Inversion']
inv_pfinal['Capital']=inv_pasiva['Capital']
#Hacemos el dataFrame que contendra los resulados de la inversion pasiva
inv_pfinal['REND']=0
inv_pfinal['REND_ACUM']=0

#Creamos el for que nos rellena inv_pfinal['REND'],inv_pfinal['REND_ACUM']
for i in range(1,len(inv_pfinal)):
    inv_pfinal.loc[i,'REND']= (inv_pfinal.loc[i,'Capital']-inv_pfinal.loc[i-1,'Capital'])/inv_pfinal.loc[i-1,'Capital']
    inv_pfinal.loc[i,'REND_ACUM']=inv_pfinal.loc[i,'REND']+ inv_pfinal.loc[i-1,'REND_ACUM']

#Visualizamos el DataFrame con resultados
print (inv_pfinal)













