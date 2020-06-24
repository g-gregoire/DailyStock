# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 21:44:48 2020

@author: Gregoireg
"""
#%% Create DB Tables and set path
def createSchema():
    import sqlite3
    import os
    path = os.path.expanduser("~/Documents/Github/DailyStock") #Set Correct path
    os.chdir(path)
    
    conn = sqlite3.connect('StockData.db')
    conn.execute("PRAGMA foreign_keys = 1") # This needs to be set for FK constraint to work
    c = conn.cursor()
    
    c.execute('CREATE TABLE IF NOT EXISTS StockNames (\
    	"StockID"	INTEGER NOT NULL,\
    	"StockTicker"	TEXT NOT NULL UNIQUE,\
    	"StockName"	TEXT NOT NULL,\
    	"Market"	TEXT NOT NULL,\
    	PRIMARY KEY("StockID" AUTOINCREMENT)\
    )')
    
    c.execute('CREATE TABLE IF NOT EXISTS "StockPrice" (\
    	"PriceID"	INTEGER NOT NULL,\
    	"DatetimeStamp"	TEXT NOT NULL,\
    	"StockID"	INTEGER NOT NULL,\
    	"Price"	REAL NOT NULL,\
    	"Volume"	REAL NOT NULL,\
    	FOREIGN KEY("StockID") REFERENCES "StockNames"("StockID"),\
    	PRIMARY KEY("PriceID" AUTOINCREMENT)\
    )')
    
    conn.commit()
    conn.close()
    
createSchema()

#%% Find StockID Function
import sqlite3
import yfinance as yf

def findStockID(ticker, name = None, market = None):
    conn = sqlite3.connect('StockData.db')
    c = conn.cursor()
    
    c.execute('Select StockID, StockTicker, StockName, Market from StockNames where StockTicker=?', [ticker])
    StockID = c.fetchone()
    
    if StockID != None:
        pass# print(StockID)
    else:
        if name == None:
            try:
                name = yf.Ticker(ticker).info['longName']
            except:
                name = 'Unknown'
        if market == None:
            try:
                market = yf.Ticker(ticker).info['exchange']
            except:
                market = 'Unknown'
        
        c.execute("INSERT INTO StockNames (StockTicker, StockName, Market) VALUES (?, ?, ?)", [ticker, name, market])
        c.execute('Select StockID, StockTicker, StockName, Market from StockNames where StockTicker=?', [ticker])
        StockID = c.fetchone()
        # print(StockID)

    conn.commit()
    conn.close()
    
    return StockID[0]
    
# Usage
ID = findStockID("MSFT")
print(ID)

#%% Download and plot data
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import timedelta 

ticker = "FR.TO"
prd = "1mo"
intvl = "30m"
data = yf.download(tickers= ticker, period=prd, interval=intvl)
data = data.reset_index()
# print(data)

stock = yf.Ticker("FR.TO").info()
print(stock)
#val = data['Close'][-1:]
#price = price.append(val, ignore_index=True)
#print(price)
# plt.plot(price)

#print(time+timedelta(minutes=15))

#%% Insert Data into DB
conn = sqlite3.connect('StockData.db')
conn.execute("PRAGMA foreign_keys = 1") # This needs to be set for FK constraint to work
c = conn.cursor()

ticker = "YRI.TO"
ID = findStockID(ticker)
#c.execute("INSERT INTO StockNames (StockTicker, StockName, Market) VALUES ('GOLD', 'Barrick Gold', 'NYSE')")
#c.execute("INSERT INTO StockNames (StockTicker, StockName, Market) VALUES ('YRI.TO', 'Yamana Gold', 'TSX')")
# c.execute("INSERT INTO StockPrice (StockID, DateTimeStamp, Price, Volume) VALUES (1, '2020-04-21 09:30:00-04:00', 25.15, 936336)")
# c.executemany('INSERT INTO StockPrice (StockID, DateTimeStamp, Price, Volume) VALUES (?, ?, ?, ?)', values)

conn.commit()
conn.close()

#%% View Data

conn = sqlite3.connect('StockData.db')
c = conn.cursor()

for row in c.execute('Select * from StockPrice'):
# for row in c.execute('Select * from StockNames'):
    print(row)

conn.commit()
conn.close()

#%% logData function. 
# Downloads data based on time ranges, pulls stock ID and logs data to DB

def logData (ticker, startDate = None, endDate = None, interval = "15m", period = "1w", show = False, plot = False):
    # yfinance constraints
    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # (optional, default is '1mo')
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # (optional, default is '1d')
    # intraday interval allowed if period < 60 days
    
    import sqlite3
    import yfinance as yf
    import matplotlib.pyplot as plt
    from datetime import timedelta 
    import pandas as pd
    import numpy as np
    
    # Download Data from yfinance
    if startDate == None:
        data = yf.download(tickers = ticker, interval=interval, period=period)
    else:
        data = yf.download(tickers = ticker, start=startDate, end=endDate, interval=interval)
    data = data.reset_index()
    # print(data)
    
    # Set variables for insert
    stockID = findStockID(ticker)
    datetime = data['Datetime']
    price = data['Open']
    volume = data['Volume']/1000
    
    # Create values list for insert
    length = datetime.size
    values = []
    date = []
    for i in range(length):
        values.append((stockID, str(datetime[i])[:-6], price[i], volume[i]))
        date.append(str(datetime[i])[:-6])
    
    conn = sqlite3.connect('StockData.db')
    conn.execute("PRAGMA foreign_keys = 1") # This needs to be set for FK constraint to work
    c = conn.cursor()
    
    c.executemany('INSERT INTO StockPrice (StockID, DateTimeStamp, Price, Volume) VALUES (?, ?, ?, ?)', values)
    
    conn.commit()
    
    if show == True:
        for row in c.execute('Select * from StockPrice'):
            print(row)
            
    if plot == True:
        plt.plot(date, price)
            
    conn.close()
    
#%% View Data Func

def viewData(ticker, startDate, endDate):
    
    stockID = findStockID(ticker)
    print(stockID)
    conn = sqlite3.connect('StockData.db')
    c = conn.cursor()
    for row in c.execute('Select * from StockPrice where StockID = ? and DateTimeStamp BETWEEN ? and ?', (stockID, startDate, endDate)):
    # for row in c.execute('Select * from StockPrice where StockID = 2 and DateTimeStamp BETWEEN "2020-06-01 00:00:00" and "2020-06-06 00:00:00"'):# and DateTimeStamp <= 2020-06-08'):
        print(row)
    conn.close()

viewData("YRI.TO", "2020-06-01", "2020-06-08")
  
  
#%% Test Calls
#import sqlite3

conn = sqlite3.connect('StockData.db')
# conn.execute("PRAGMA foreign_keys = 1") # This needs to be set for FK constraint to work
c = conn.cursor()

ticker = 'YRI.TO'
start = '2020-06-08'
end = '2020-06-09'
interv = "30m"
prd = "1mo"

# logData(ticker = ticker, startDate = start, endDate = end, show = True)
values = logData(ticker = ticker, interval = interv, period = prd, show = True, plot = True)

# c.execute('Select * from StockNames')
# for i in range(2):
#     values = [1, '2020-04-21 09:30:00-04:00', i, 936336]
# c.execute('INSERT INTO StockPrice (StockID, DateTimeStamp, Price, Volume) VALUES (?, ?, ?, ?)', values)
# c.execute('Select * from StockPrice')
# c.execute('Delete from StockPrice')
# c.execute('Drop Table StockPrice')
# print(c.fetchall())
conn.commit()
conn.close()

