# -*- coding: utf-8 -*-
"""
model.py
This file
Created on Wed Jul 22 19:51:25 2020

@author: Gregoireg
"""

#%% Import Required packages, functions, and initialize DB schema
import os
path = os.path.expanduser("~/Documents/Github/DailyStock") #Set Correct path
os.chdir(path)
import tensorflow as tf
import numpy as np
# import DB_func as db
# Main functions from stock_pull are 
# - createSchema: creates DB and sets path
# - logdata: logs data for specific time interval to DB
# - viewData: prints data for specific time range

#%% Create Data Structure for Tensorflow

def createDS(data, split_p = 0.8, window_size = 20, batch_size = 10, shuffle_size=10):
    price = data[:,3]
    limit = int(np.ceil(price.size*split_p))
    price_train = price[:limit].astype(np.float64) #select range of array and convert to float
    # print(price_train)
    
    dataset = tf.expand_dims(price_train, axis=-1)
    dataset = tf.data.Dataset.from_tensor_slices(dataset)
    dataset = dataset.window(window_size + 1, shift=1, drop_remainder= True)
    dataset = dataset.flat_map(lambda x: x.batch(window_size + 1))
    dataset = dataset.map(lambda x: (x[:-1], x[-1:]))
    dataset = dataset.shuffle(shuffle_size)
    dataset_train = dataset.batch(batch_size).prefetch(1)    
    
    return price, dataset_train
    # also create test set
    
# price, ds_train = createDS(data, window_size = 20, batch_size = 2)
# for x, y in ds_train:
#     print(x)
#     print(y)

#%% Create then compile and fit Tensorflow model

def createModel(): 
    tf.keras.backend.clear_session()
    model = tf.keras.models.Sequential([
      tf.keras.layers.Conv1D(filters=60, kernel_size=5,
                          strides=1, padding="causal",
                          activation="relu",
                          input_shape=[None, 1]),
      tf.keras.layers.LSTM(64, return_sequences=True),
      tf.keras.layers.LSTM(64, return_sequences=True),
      tf.keras.layers.Dense(30, activation="relu"),
      tf.keras.layers.Dense(10, activation="relu"),
      tf.keras.layers.Dense(1),
      tf.keras.layers.Lambda(lambda x: x * 400)
    ])
    
    return model


# This function compiles and fits the model 
def runModel(model, dataset, epoch):
    optimizer = tf.keras.optimizers.SGD(lr=8e-7, momentum=0.9)
    model.compile(loss=tf.keras.losses.Huber(), optimizer=optimizer, metrics=["mae"])
    history = model.fit(dataset, epochs=epoch)
    
    return history
    

def predict(model, data, window_size = 20, batch_size = 10):
    price = data[:,3].astype(np.float64) #select range of array and convert to float
    
    dataset = tf.expand_dims(price, axis=-1)
    dataset = tf.data.Dataset.from_tensor_slices(dataset)
    dataset = dataset.window(window_size, shift=1, drop_remainder= True)
    dataset = dataset.flat_map(lambda w: w.batch(window_size))
    dataset = dataset.batch(batch_size).prefetch(1) 
    forecast = model.predict(dataset)
    
    forecast = forecast[:, -1, 0]
    print(forecast)
    
    return forecast

# #%% Test Model Calls

# price, ds_train = createDS(data, window_size = 30, batch_size = 10)
# model = createModel()
# history = runModel(model, ds_train, epoch=5)

# #%% Forecast calls

# forecast = predict(model, data, window_size = 30, batch_size = 10)

# forecast = forecast[:, -1, 0]
# print(forecast)
# print(price.size)
