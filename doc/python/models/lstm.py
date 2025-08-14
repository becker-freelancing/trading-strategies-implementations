num_layers = trial.suggest_int('num_layers', 1, 2)
num_units_input = trial.suggest_int('num_units_input', 32, 128)
num_units = trial.suggest_int('num_units', 32, 128)
input_length = trial.suggest_int('input_length', 30, 150)

learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2,
                                    log=True)

model = Sequential()
model.add(InputLayer(shape=(input_length, input_dimension)))
if num_layers == 1:
    model.add(LSTM(num_units_input, return_sequences=False))
else:
    model.add(LSTM(num_units_input, return_sequences=True))

for i in range(num_layers - 1):
    if i == num_layers - 2:
        model.add(LSTM(num_units, return_sequences=False))
    else:
        model.add(LSTM(num_units, return_sequences=True))

model.add(Dense(...))

model.compile(optimizer=Adam(learning_rate=learning_rate), ...)
