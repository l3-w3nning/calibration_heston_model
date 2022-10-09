import yfinance as yf 
import pandas as pd
import numpy as np

def set_option_data(input_stock_ticker,base_date):

    '''

    :param input_stock_ticker: Ticker for stock to analyze 
    :base_date: expiry date of option
    :return: array with [0]:df of option with highest volume, used to calibrate bs imp vol, [1]price of option(used for calibration) [2]expiry date[3]time to expiry from today [4]option chain (for calibration of Heston modell -> later i also want to calibrate bs vola with multiple options maybe (average is then imp vola market consenus))
    '''

    
    stock=yf.Ticker(input_stock_ticker)
    
    from datetime import datetime, timedelta,date
    today=date.today()
    format_date="%Y-%m-%d"
    today=datetime.strptime(str(today),format_date)
    b_d = datetime.strptime(base_date, format_date)
    price_history=stock.history(period="1d")
    current_price=price_history.iloc[0][0]  
    def func(x,base_date):
        d2=datetime.strptime(base_date, format_date)
        date=x[0]
        for i in x:
            d1 = datetime.strptime(i, format_date)
            if abs((d2-d1).days)<=abs((d2-datetime.strptime(x[0],format_date)).days):
                date=i
        return date

    datelist =  stock.options
    expiry_date=func(datelist,base_date)
    time_to_expiry=((datetime.strptime(expiry_date,format_date)-today).days)/365 #time to expiry in years
    index=datelist.index(expiry_date)

    opt_data=stock.option_chain(datelist[index])


    calibration_dataset=opt_data.calls

    calibration_row=calibration_dataset["openInterest"].idxmax()
    #print(calibration_dataset)

    calibration_dataset_1=calibration_dataset.iloc[calibration_row]

    return [calibration_dataset_1,current_price,expiry_date,time_to_expiry,calibration_dataset]#hier noch einen named array raus machen
