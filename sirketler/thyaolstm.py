# -*- coding: utf-8 -*-
"""thyaoLstm.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GRHVEYvMtoE3-J9uZ7SL1hiTaOd3sVqm
"""

!pip install yfinance

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# %matplotlib inline
import seaborn as sns
import datetime as dt
import seaborn as sb
import yfinance as yf

thyao = yf.download('THYAO.IS','2009-01-01','2023-01-14')
thyao.tail()

thyao.describe()

thyao.info()

plt.figure(figsize=(10, 5))

plt.title('THY Kapanış Fiyatı')
thyao['Close'].plot()
plt.ylabel('Kapanış Fiyatı TL (₺)', fontsize=10)
plt.xlabel('Tarih', fontsize=10)

plt.tight_layout()

features = ['Open', 'High', 'Low', 'Close', 'Volume']
plt.subplots(figsize=(20,10))
for i, col in enumerate(features):
  plt.subplot(2,3,i+1)
  sb.distplot(thyao[col])
plt.show()

plt.subplots(figsize=(20,10))
for i, col in enumerate(features):
  plt.subplot(2,3,i+1)
  sb.boxplot(thyao[col])
plt.show()

ma_day = [10, 20, 50]

for ma in ma_day:
  column_name = f"MA for {ma} days"
  thyao[column_name] = thyao['Adj Close'].rolling(ma).mean()

thyao[['Adj Close', 'MA for 10 days', 'MA for 20 days', 'MA for 50 days']].plot(figsize=(10,5))

data = thyao.filter(['Close'])
dataset = data.values
training_data_len = int(np.ceil(len(dataset) * .95))
training_data_len

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score

scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)
scaled_data

train_data = scaled_data[0:int(training_data_len), :]

x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])
    if i<= 61:
        print(x_train)
        print(y_train)
        print()

x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

from keras.models import Sequential
from keras.layers import Dense, LSTM

model = Sequential()
model.add(LSTM(128, return_sequences=True, input_shape= (x_train.shape[1], 1)))
model.add(LSTM(64, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(x_train, y_train, batch_size=1, epochs=1)

test_data = scaled_data[training_data_len - 60: , :]
x_test = []
y_test = dataset[training_data_len:, :]
for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))
rmse

train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions

plt.figure(figsize=(10,5))
plt.title('Model')
plt.xlabel('Tarih Aralığı', fontsize=10)
plt.ylabel('Kapanış Fiyatı TL (₺)', fontsize=10)
plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.legend(['Eğitim', 'Gerçek', 'Tahmin'], loc='lower right')
plt.show()

valid["2023-01"]