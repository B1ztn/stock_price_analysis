import numpy as np
from tensorflow.python.keras.models import Sequential 
from tensorflow.python.keras.layers import LSTM 
from tensorflow.python.keras.layers import Dense 
from tensorflow.python.keras.layers import Flatten 
import matplotlib.pyplot as plt 
###LSTM RNN
#prediction for the future 10 days
import os 

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

#prepare independent and dependent features 
def prepare_data(timeseries_data, n_features):
    X, y = [], []
    for i in range(len(timeseries_data)):
        #find the end of this pattern 
        end_ix = i + n_features
        if end_ix > len(timeseries_data)-1:
            break
        #gather input and output parts of the pattern
        seq_x, seq_y = timeseries_data[i:end_ix], timeseries_data[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


timeseries_data = [52,56,53.4,52.1,53.2,54.7,55.6,57.2,58.1]
#choose a number of time steps
n_steps = 3
#splite into samples 
X,y = prepare_data(timeseries_data, n_steps)

#reshape from [samples, timesteps] into [samples, timesteps, features]
n_features = 1
X = X.reshape((X.shape[0], X.shape[1], n_features))


#define the model 
model = Sequential()
model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(n_steps,n_features)))
model.add(LSTM(50, activation='relu'))
model.add(Dense(1))
model.compile(optimizer='adam',loss='mse')
#fit model 
model.fit(X,y,epochs=300, verbose = 0)

#demonstrate prediction for next 10 days
x_input = np.array([58.5,58.9,59.2])
temp_input=list(x_input)
lst_output = []
i = 0

while(i<10):
    if(len(temp_input)>3):
        x_input=np.array(temp_input[1:])
        x_input = x_input.reshape((1,n_steps,n_features))
        yhat = model.predict(x_input, verbose = 0)
        temp_input.append(yhat[0][0])
        temp_input = temp_input[1:]
        lst_output.append(yhat[0][0])
        i=i+1
    else:
        x_input = x_input.reshape((1, n_steps, n_features))
        yhat = model.predict(x_input, verbose = 0)
        temp_input.append(yhat[0][0])
        lst_output.append(yhat[0][0])
        i = i + 1

print(lst_output)


day_new = np.arange(1,10)
day_pred = np.arange(10,20)
plt.plot(day_new, timeseries_data)
plt.plot(day_pred, lst_output)
plt.show()  
