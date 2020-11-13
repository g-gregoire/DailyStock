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
import tensorflow as tf
import numpy as np
import DB_func as db # internal functions for database/stock pulls
import dataModel as dataModel # data & model creation
# Main functions from stock_pull are 
# - createSchema: creates DB and sets path
# - logdata: logs data for specific time interval to DB
# - viewData: prints data for specific time range

#Create Database if not yet created
db.createSchema()


#%% Log Data to DB

# db.logData("YRI.TO") #default is one day

#%% Pull Data from DB

data = db.viewData("YRI.TO", startDate = "2020-07-01", endDate = "2020-07-28") #default is last day

#%% Test Model Calls

price, ds_train = dataModel.createDS(data, window_size = 30, batch_size = 10)
model = dataModel.createModel()
history = dataModel.runModel(model, ds_train, epoch=5)

#%% Forecast calls

forecast = dataModel.predict(model, data, window_size = 30, batch_size = 10)

# forecast = forecast[:, -1, 0]
# print(forecast)

