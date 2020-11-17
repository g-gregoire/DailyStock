# -*- coding: utf-8 -*-
"""
DailyStock.py
This is what runs the core code.
Created on Wed Jul 22 19:55:26 2020

@author: Gregoireg
"""
import os
path = os.path.expanduser("~/Documents/Github/DailyStock") #Set Correct path
os.chdir(path)
import DB_func as db # internal functions for database/stock pulls
import dataModel # data & model creation

#Create Database if not yet created
db.createSchema()

#%% Clear the table of data
db.clearData()

#%% Log Data to DB
# Set stock Ticker
ticker = "YRI.TO"

# Ex1: Log data for last day
# db.logData(ticker) #default is one day

# Ex2: Log data for last week
# db.logData(ticker, interval = "15m", period = "1wk")

# Ex3: Log data for last month
db.logData(ticker, interval = "15m", period = "1mo")

#%% Pull Data from DB

data = db.viewData("YRI.TO", period = "1mo", plot = False)
# data = db.viewData(ticker, startDate = "2020-07-01", endDate = "2020-07-28") #default is last day

#%% Test Model Calls

price, ds_train = dataModel.createDS(data, window_size = 30, batch_size = 10)
model = dataModel.createModel()
history = dataModel.runModel(model, ds_train, epoch=500)

#%% Forecast calls

forecast = dataModel.predict(model, data, window_size = 30, batch_size = 10)
# print(data.size)
# print(forecast.size)

import matplotlib.pyplot as plt
plt.plot(forecast)
# plt.plot(data)
