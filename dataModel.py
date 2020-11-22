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
import matplotlib.pyplot as plt
# import DB_func as db
# Main functions from stock_pull are 
# - createSchema: creates DB and sets path
# - logdata: logs data for specific time interval to DB
# - viewData: prints data for specific time range

#%% Create Data Structure for Tensorflow

def createDS(data, split_p = 0.8, window_size = 20, batch_size = 10, shuffle_size=100):
    price = data[:,3]
    limit = int(np.ceil(price.size*split_p))
    price_train = price[:limit].astype(np.float64) #select range of array and convert to float
    price_valid = price[limit:].astype(np.float64) #select range of array and convert to float
    
    dataset = tf.expand_dims(price_train, axis=-1)
    dataset = tf.data.Dataset.from_tensor_slices(dataset)
    dataset = dataset.window(window_size + 1, shift=1, drop_remainder= True)
    dataset = dataset.flat_map(lambda x: x.batch(window_size + 1))
    dataset = dataset.map(lambda x: (x[:-1], x[-1:]))
    dataset = dataset.shuffle(shuffle_size)
    dataset_train = dataset.batch(batch_size).prefetch(1)    
    
    return price, dataset_train, limit, price_valid
    # also create test set
    
# price, ds_train = createDS(data, window_size = 20, batch_size = 2)
# for x, y in ds_train:
#     print(x)
#     print(y)

#%% Create then compile and fit Tensorflow model

# This function creates the model that we will train
def createModel(): 
    tf.keras.backend.clear_session()
    model = tf.keras.models.Sequential([
      tf.keras.layers.Conv1D(filters=60, kernel_size=5,
                          strides=1, padding="causal",
                          activation="relu",
                          input_shape=[None, 1]),
      tf.keras.layers.LSTM(64, return_sequences=True),
      tf.keras.layers.LSTM(64, return_sequences=True),
      # tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
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
    

def predict(model, data, limit, window_size = 20, batch_size = 10, show = False, plot = False):
    price = data[:,3].astype(np.float64) #select range of array and convert to float
    
    dataset = tf.expand_dims(price, axis=-1)
    dataset = tf.data.Dataset.from_tensor_slices(dataset)
    dataset = dataset.window(window_size, shift=1, drop_remainder= True)
    dataset = dataset.flat_map(lambda w: w.batch(window_size))
    dataset = dataset.batch(batch_size).prefetch(1) 
    forecast = model.predict(dataset)
    
    forecast = forecast[limit - window_size:-1, -1, 0]
    
    # Show the data that was predicted
    if show == True:
        print(forecast)
    
    # Plot the data that was predicted
    if plot == True:
        plt.plot(forecast)
        plt.figure()
        
    return forecast

#%% Tuning functions

# Results Function
def metrics(history, x_valid, forecast):
    mae=history.history['mae']
    loss=history.history['loss']
    
    epochs=range(len(loss)) # Get number of epochs
    zoom_range = int(np.ceil(len(loss)*0.4)) # Get 40% point for zoomed in view
    
    # Plot MAE and Loss
    plt.plot(epochs, mae, 'r')
    plt.plot(epochs, loss, 'b')
    plt.title('MAE and Loss')
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.legend(["MAE", "Loss"])
    plt.figure()
    
    epochs_zoom = epochs[zoom_range:]
    mae_zoom = mae[zoom_range:]
    loss_zoom = loss[zoom_range:]
    
    # Plot Zoomed MAE and Loss
    plt.plot(epochs_zoom, mae_zoom, 'r')
    plt.plot(epochs_zoom, loss_zoom, 'b')
    plt.title('MAE and Loss')
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.legend(["MAE", "Loss"])    
    plt.figure()

    # Plot Forecast and Validation data
    plt.plot(x_valid, 'r')
    plt.plot(forecast, 'b')
    plt.title('Forecast and Validation Data')
    plt.ylabel("Price")
    plt.legend(["Validation", "Prediction"])    
    plt.figure()

    mae_val = tf.keras.metrics.mean_absolute_error(x_valid, forecast).numpy()
    print("MAE: ", mae_val)
    
