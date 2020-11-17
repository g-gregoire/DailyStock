# -*- coding: utf-8 -*-
"""
stock_pull.py
This file creates the database architecture required to hold all the stock data, 
and pulls said stock data into the database
Created on Mon Apr 27 21:44:48 2020

@author: Gregoireg
"""
#%% Import Required packages, functions, and initialize DB schema
import sqlite3
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as d
from dateutil.relativedelta import *
import numpy as np
import os
path = os.path.expanduser("~/Documents/Github/DailyStock") #Set Correct path
os.chdir(path)

# Create DB Tables and set path
def createSchema():
    
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

# Find StockID Function
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
    
# Logs data for a certain stock and date range
def logData (ticker, startDate = None, endDate = None, interval = "15m", period = "1d", show = False, plot = False):
    # yfinance constraints
    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # (optional, default is '1mo')
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # (optional, default is '1d')
    # intraday interval allowed if period < 60 days
    
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
    print(values)
    conn = sqlite3.connect('StockData.db')
    conn.execute("PRAGMA foreign_keys = 1") # This needs to be set for FK constraint to work
    c = conn.cursor()
    
    c.executemany('INSERT INTO StockPrice (StockID, DateTimeStamp, Price, Volume) VALUES (?, ?, ?, ?)', values)
    
    conn.commit()
    
    # Show the data that was logged
    if show == True:
        for row in c.execute('Select * from StockPrice'):
            print(row)
    
    # Plot the data that was logged
    if plot == True:
        plt.plot(date, price)
            
    conn.close()
    
#%% View Data Func

def viewData(ticker, startDate = None, endDate = None, period = "1d", plot = False):
    
    now = d.datetime.now()
    today = d.datetime(now.year, now.month, now.day)
    
    if startDate == None:
        
        if period == "1d":
            startDate = today - d.timedelta(days=1)
            endDate = today
            
        elif period == "1wk":
            startDate = today - d.timedelta(weeks=1)
            endDate = today
        
        elif period == "1mo":
            startDate = today + relativedelta(months=-1)
            endDate = today
    
    else:
        startDate = d.datetime.strptime(startDate, '%Y-%m-%d')
        endDate = d.datetime.strptime(endDate, '%Y-%m-%d')

    startDate = startDate + d.timedelta(hours=9)
    endDate = endDate + d.timedelta(hours=16.5)

    stockID = findStockID(ticker)
    
    conn = sqlite3.connect('StockData.db')
    c = conn.cursor()
    values = np.empty((1,5))
    c.execute('Select * from StockPrice where StockID = ? and DateTimeStamp BETWEEN ? and ?', (stockID, startDate, endDate))

    for data in c.fetchall():
        print(data)
        values = np.append(values, [data], axis=0)
    values = np.delete(values,0,0)
    
    # Plot the data that was logged
    if plot == True:
        price = values[:,3].astype(np.float)
        date = values[:,1]
        plt.plot(date, price)
    
    conn.close()
    
    return values

#%% Clear the price databases
def clearData():
    
    conn = sqlite3.connect('StockData.db')
    c = conn.cursor()
    
    c.execute('Delete from StockPrice')
    
    conn.commit()            
    conn.close()
