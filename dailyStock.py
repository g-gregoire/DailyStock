# -*- coding: utf-8 -*-
"""
DailyStock.py
This is what runs the core code.
Created on Wed Jul 22 19:55:26 2020

@author: Gregoireg
"""
import os
path = os.path.expanduser("~/Documents/Github/DailyStock")  #Set Correct path
os.chdir(path)
import DB_func as db # internal functions for database/stock pulls
import dataModel as mdl# data & model creation

#Create Database if not yet created
db.createSchema()

#%% Clear the table of data
db.clearData(mode=2) #mode 1 clears the table, 2 drops and recreates the table

#%% Log Data to DB
# Set stock Ticker
ticker = "YRI.TO"

# Ex1: Log data for last day
# db.logData(ticker) #default is one day

# Ex2: Log data for last week
# db.logData(ticker, interval = "15m", period = "1wk")

# Ex3: Log data for last month
db.logData(ticker, interval = "5m", period = "1mo")

#%% Pull Data from DB

data = db.viewData("YRI.TO", period = "1mo", plot = True)
# data = db.viewData(ticker, startDate = "2020-11-01", endDate = "2020-11-28") #default is last day

#%% Test Model Calls
# Set Hyperparams
windowSize = 15
batchSize = 32
numEpochs = 500

price, ds_train, limit, price_valid = mdl.createDS(data, window_size = windowSize, batch_size = batchSize)
model = mdl.createModel()
history = mdl.runModel(model, ds_train, epoch = numEpochs)

#%% Forecast calls and model results

forecast = mdl.predict(model, data, limit, window_size = windowSize, batch_size = batchSize, plot = False)
mdl.metrics(history, price_valid, forecast)
