# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#die funktion muss ich auch nochmal umschreiben, damit das mit gui gestreamlined ist!

import yfinance as yf 
import pandas as pd
import sqlite3
import numpy as np
from set_calibration_data import set_option_data
def get_calibration_data():
    ''''
    :return: dataframe of option chain (for heston model) and data of data base with option with max volume (for bs calibration)
    '''
    data_option=set_option_data("AAPL","2023-12-12")
    
    dbconn=sqlite3.connect('/home/leo/Documents/OptionPricing/optionpricing.db')
    curs = dbconn.cursor()
    results=[]
    colnames=[]
    for row in dbconn.execute("SELECT * FROM optionpricing ORDER BY oid DESC LIMIT 1"):  # ORDER BY oid DESC LIMIT 1")#get item entered last
        results.append(row)
    results=np.array(results[0])
    for col in dbconn.execute("PRAGMA table_info(optionpricing)"):
        colnames.append(col)
    dbconn.commit()
    dbconn.close()
    colnames=np.array(colnames)

    colnames=colnames[:,1]
    data_db=dict(zip(colnames,results))

    df_db=pd.DataFrame(data_db,index=[0])
    df_db = df_db.astype({'numsims':'int','bid':'float','ask':'float','RiskFreeRate':'float','Deltat':'float','S0':'float','Strike':'float','contractSymbol':'string'})
    
    return [data_option[4],df_db]#hier noch einen named array raus machen

