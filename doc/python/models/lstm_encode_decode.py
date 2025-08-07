num_units_input = trial.suggest_int('num_units_input', 32, 128)
num_units = trial.suggest_int('num_units', 32, 128)
input_length = trial.suggest_int('input_length', 30, 150)
learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2,
                                    log=True)

model = Sequential()
model.add(InputLayer(shape=(input_length, input_dimension)))

model.add(LSTM(num_units_input, return_sequences=False))

model.add(RepeatVector(30))

model.add(LSTM(num_units, activation='relu', return_sequences=True))
model.add(TimeDistributed(Dense(...)))

model.compile(optimizer=Adam(learning_rate=learning_rate), ...)
