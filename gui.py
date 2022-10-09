
from cgitb import text
from statistics import variance
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import sqlite3
from os.path import exists
import os
import yfinance as yf
from set_calibration_data import set_option_data

class mclass:
    def __init__(self,  window):
        self.window = window
        
        global data

        #messagebox.showinfo(title="Marketdata imported",message="Prefilled cells contain market data of call option with largest volume, calls with lower volume also saved in background (in seperate db), rest to be filled by the user")

        mylabel0=Label(self.window,text="Contract Symbol")
        mylabel0.grid(row=9,column=0)
        self.contract = Entry(window,width=20)
        self.contract.insert(END,data[0].loc["contractSymbol"])
        self.contract.grid(row=9,column=1)
        

                
        mylabel1=Label(self.window,text="Number of Simulations")
        mylabel1.grid(row=0,column=0)
        self.numsims = Entry(window,width=20)
        self.numsims.grid(row=0,column=1)
        
        
        mylabel3=Label(self.window,text="Starting Stock Price")
        mylabel3.grid(row=2,column=0)
        self.s0 = Entry(window,width=20)
        self.s0.insert(END,data[1])
        self.s0.grid(row=2,column=1)
        
        mylabel4=Label(self.window,text="RiskFree Rate")
        mylabel4.grid(row=3,column=0)
        self.rfr = Entry(window,width=20)
        self.rfr.grid(row=3,column=1)

        mylabel5=Label(self.window,text="Deltat")
        mylabel5.grid(row=4,column=0)
        self.deltat = Entry(window,width=20)
        self.deltat.insert(END,data[3])
        self.deltat.grid(row=4,column=1)
        
        mylabel7=Label(self.window,text="Strike")
        mylabel7.grid(row=6,column=0)
        self.strike = Entry(window,width=20)
        self.strike.insert(END,data[0].loc["strike"])
        self.strike.grid(row=6,column=1)

        mylabel8=Label(self.window,text="Bid price")
        mylabel8.grid(row=7,column=0)
        self.bid = Entry(window,width=20)
        self.bid.insert(END,data[0].loc["bid"])
        self.bid.grid(row=7,column=1)

        mylabel9=Label(self.window,text="Ask price")
        mylabel9.grid(row=8,column=0)
        self.ask = Entry(window,width=20)
        self.ask.insert(END,data[0].loc["ask"])
        self.ask.grid(row=8,column=1)
           
        self.button = Button(window, text="Submit Data to Database", command=self.filldatabase).grid(row=10,columnspan=4)
    
    
    def filldatabase(self):
        dbconn = sqlite3.connect('optionpricing.db')
        #create cursor instance
        cursor_db = dbconn.cursor()
        #create db if it does not exist
        if exists('~/optionpricing.db'):
            os.remove('~/optionpricing.db')
        dbconn.execute("""CREATE TABLE optionpricing(
                        numsims integer,
                        bid real,
                        ask real,
                        RiskFreeRate real,
                        Deltat real,
                        S0 text,
                        Strike real,
                        contractSymbol Text)
                        """)
        #fill db with supplied data
        dbconn.execute("INSERT INTO optionpricing VALUES (:numsims,:bid,:ask,:rfr,:deltat,:S0,:strike,:contract)",
                        {
                        'numsims':self.numsims.get(),
                        'bid':self.bid.get(),
                        'ask':self.ask.get(),
                        'rfr':self.rfr.get(),
                        'deltat':self.deltat.get() ,
                        'S0':self.s0.get() ,
                        'strike':self.strike.get(),
                        'contract':self.contract.get()    
                        }
        )
        #commit changes
        dbconn.commit()
        #close connection
        dbconn.close()


        #now write in separate db to fill all calls to expiration date into db (important for heston calibration)


        dbconn = sqlite3.connect('optionpricing_all_calls.db')
        #create cursor instance
        cursor_db = dbconn.cursor()
        #create db if it does not exist
        
        #add numsims and rfr information (to be supplied by user in interface) to data from yfinance
        calibration_data=data[4]
        calibration_data['numsims']=self.numsims.get()
        calibration_data['rfr']=self.rfr.get()

        calibration_data.to_sql(name='calibration_data',con=dbconn,if_exists='replace',index=False)
        
        #commit changes
        dbconn.commit()
        
        #close connection
        dbconn.close()


        messagebox.showinfo(title="Submitted Successfully,Prefilled cells contain market data of call option with largest volume, calls with lower volume also saved in background (in seperate db)",message="Data Submitted, You can close the interface now")

    



stock_data=input("please enter stock ticker: ")
base_date=input("please enter expiration date in format YYYY-mm-dd: ")
data=set_option_data(stock_data,base_date)
window= Tk()
start= mclass (window,)
window.mainloop()