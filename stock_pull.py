# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 21:44:48 2020

@author: Gregoireg
"""
#%% Download and plot data

import yfinance as yf
import matplotlib.pyplot as plt
from datetime import timedelta 

ticker = "YRI.TO"
prd = "1mo"
intvl = "30m"
data = yf.download(tickers= ticker, period=prd, interval=intvl)
data = data.reset_index()

time = data['Datetime']
price = data['Open']
volume = data['Volume']

print(price)
#val = data['Close'][-1:]
#price = price.append(val, ignore_index=True)
#print(price)

#print(time+timedelta(minutes=15))
plt.plot(volume)

#%% Create DB Tables
import sqlite3

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

#%% Find StockID Function

def findStockID(Ticker, Market = "None"):
    conn = sqlite3.connect('StockData.db')
    c = conn.cursor()
    
    if Market == "None":
        c.execute('Select StockID from StockNames where StockTicker=?', [Ticker])
        StockID = c.fetchone()
    else:
        c.execute('Select StockID from StockNames where StockTicker=? and Market=?', [Ticker, Market])
        StockID = c.fetchone()
    
    if StockID == None:
        StockID = -1
    
    conn.commit()
    conn.close()
    
    return StockID
    
#ID = findStockID("YRI.TO")
#print(ID)

#%% Create Loggable data structure
import pandas as pd

ticker = "YRI.TO"
stockID = findStockID(ticker)[0]
datetime = data['Datetime']
price = data['Open']
volume = data['Volume']/1000

d = {'Datetime' : datetime,
     'Stock' : "",
     'Price' : price,
     'Volume': volume}

df = pd.DataFrame(d)
df['Stock'] = stockID
df_slice = df[0:10]
print(df_slice)
print(stockID, datetime[0], price[0], volume[0])
#%% Insert Data into DB
conn = sqlite3.connect('StockData.db')
conn.execute("PRAGMA foreign_keys = 1") # This needs to be set for FK constraint to work
c = conn.cursor()

#c.execute("INSERT INTO StockNames (StockTicker, StockName, Market) VALUES ('GOLD', 'Barrick Gold', 'NYSE')")
#c.execute("INSERT INTO StockNames (StockTicker, StockName, Market) VALUES ('YRI.TO', 'Yamana Gold', 'TSX')")
c.execute("INSERT INTO StockPrice (StockID, DateTimeStamp, Price, Volume) VALUES (1, '2020-04-21 09:30:00-04:00', 25.15, 936336)")

conn.commit()
conn.close()

#%% View Data

conn = sqlite3.connect('StockData.db')
c = conn.cursor()

for row in c.execute('Select * from StockPrice'):
    print(row)

conn.commit()
conn.close()

#%% Test Calls
#import sqlite3

intl = df['Volume'][0]/100
print(df_slice['Volume'])

values = [stockID, str(df['Datetime'][0]),df['Price'][0], intl]#df['Volume'][0]]
#print(values, '\n')
#vol = df['Volume'][0]

conn = sqlite3.connect('StockData.db')
conn.execute("PRAGMA foreign_keys = 1") # This needs to be set for FK constraint to work
c = conn.cursor()

#Ticker = 'YRI.TO'
c.execute('Select * from StockNames')
c.executemany('INSERT INTO StockPrice (StockID, DateTimeStamp, Price, Volume) VALUES (?, ?, ?, ?)', df_slice[0:1])
c.execute('Select * from StockPrice')
#c.execute('Delete from StockPrice')
#c.execute('Drop Table StockPrice')
print(c.fetchall())   
conn.commit()
conn.close()

