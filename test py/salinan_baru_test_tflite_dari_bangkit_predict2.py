import numpy as np # linear algebra
import pandas as pd # data processing
import matplotlib.pyplot as plt # visuals 

from sklearn.preprocessing import MinMaxScaler # scale the data
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator # time series Generator
from tensorflow.keras.models import Sequential # Sequential model
from tensorflow.keras.layers import Dense, LSTM, Dropout # LSTM
from tensorflow.keras.callbacks import EarlyStopping # Early Stopping
import tensorflow as tf
# load the dataset
df = pd.read_csv('sales_forcasting.csv', parse_dates = True, index_col='DATE')
dataset = df.values
dataset = dataset.astype('float32')

df.plot(subplots=True)

print(df.head())

# scaler 
# rename the column
df.columns = ['Sales']
# plot the data 
df.plot(figsize = (15,6));

# rename the column
df.columns = ['Sales']

# train test split 
test_size = 18
test_index = len(df) - test_size 

train = df.iloc[:test_index]
test = df.iloc[test_index:]

print(train.tail())

print(test.head())

# scaler 
scaler = MinMaxScaler()

# fit the scaler on the training data 
scaler.fit(train)

# use the scaler to transform training and test data 
scaled_train = scaler.transform(train)
scaled_test = scaler.transform(test)

# Timeseries Generator
length = 12 # a whole year 
train_generator = TimeseriesGenerator(scaled_train, scaled_train, length = length, batch_size = 1)
validation_generator = TimeseriesGenerator(scaled_test, scaled_test, length = length, batch_size = 1)

X, y = train_generator[0]

from tensorflow import keras
reconstructed_model = keras.models.load_model("trained_model.h5")

# number of features in our dataset
n_features = 1 
reconstructed_model = keras.models.load_model("trained_model.h5")


# compile the model
reconstructed_model.compile(optimizer='adam', loss = 'mse')

# Early Stopping
early_stop = EarlyStopping(monitor='val_loss', patience=2)

# fir the model
history = reconstructed_model.fit(train_generator, validation_data= validation_generator, callbacks = [early_stop]);

# plot losses 
losses = pd.DataFrame(reconstructed_model.history.history)
losses.plot(figsize = (12,6))

test_predictions = []

first_eval_batch = scaled_train[-length:]
current_batch = first_eval_batch.reshape((1, length, n_features))

for i in range(len(test)):
    
    # get prediction 1 time stamp ahead ([0] is for grabbing just the number instead of [array])
    current_pred = reconstructed_model.predict(current_batch)[0]
    
    # store prediction
    test_predictions.append(current_pred) 
    
    # update batch to now include prediction and drop first value
    current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis=1)

true_predictions = scaler.inverse_transform(test_predictions)
test['Predictions'] = true_predictions

test

test.plot(figsize = (12, 6));

# scale the full data 
full_scaler = MinMaxScaler()
scaled_full_data = full_scaler.fit_transform(df)

# generator for the full data 
length = 12
generator = TimeseriesGenerator(scaled_full_data, scaled_full_data, length = length, batch_size = 1)

forecast = []
# Replace periods with whatever forecast length you want
periods = 12

first_eval_batch = scaled_full_data[-length:]
current_batch = first_eval_batch.reshape((1, length, n_features))

for i in range(periods):
    
    # get prediction 1 time stamp ahead ([0] is for grabbing just the number instead of [array])
    current_pred = reconstructed_model.predict(current_batch)[0]
    
    # store prediction
    forecast.append(current_pred) 
    
    # update batch to now include prediction and drop first value
    current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis=1)

# true values of the forcast  
forecast = scaler.inverse_transform(forecast)

# create a date index 
forecast_index = pd.date_range(start='2019-11-01',periods=periods,freq='MS')

# concatinate index with forcasts  
forecast_df = pd.DataFrame(data=forecast,index=forecast_index,
                           columns=['Forecast'])
forecast_df

ax = df.plot(figsize = (25,6))
forecast_df.plot(ax = ax)

# zoom in
ax = df.plot(figsize = (12,6))
forecast_df.plot(ax=ax)
plt.xlim('2018-01-01','2020-12-01')