
import yfinance as yf
import pandas as pd
import sqlite3
import numpy as np
from set_calibration_data import set_option_data


def get_calibration_data():
    """
    this functions accesses the sql data base to load the repsective option chain
    :return: dataframe of option chain (for heston model) (df_db) and data of data base with option with max volume (for bs calibration)
    """
    data_option = set_option_data("AAPL", "2023-12-12")
    data_option_bs_calibration = data_option[4]  # only used for black scholes calibration

    dbconn = sqlite3.connect("/home/leo/Documents/OptionPricing/optionpricing.db")
    curs = dbconn.cursor()
    results = []
    colnames = []
    for row in dbconn.execute("SELECT * FROM optionpricing ORDER BY oid DESC LIMIT 1"):
        results.append(row)
    results = np.array(results[0])
    for col in dbconn.execute("PRAGMA table_info(optionpricing)"):
        colnames.append(col)
    dbconn.commit()
    dbconn.close()
    colnames = np.array(colnames)

    colnames = colnames[:, 1]
    data_db = dict(zip(colnames, results))

    df_db = pd.DataFrame(data_db, index=[0])
    df_db = df_db.astype(
        {
            "numsims": "int",
            "bid": "float",
            "ask": "float",
            "RiskFreeRate": "float",
            "Deltat": "float",
            "S0": "float",
            "Strike": "float",
            "contractSymbol": "string",
        }
    )

    return [data_option_bs_calibration, df_db]
