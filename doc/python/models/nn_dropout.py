num_layers = trial.suggest_int('num_layers', 1, 3)
num_units_1 = trial.suggest_int('num_units_1', 32, 256)
num_units_2 = trial.suggest_int('num_units_1', 32, 256)
dropout = trial.suggest_float('dropout', 0.05, 0.35)
input_length = trial.suggest_int('input_length', 5, 150)
learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2,
                                    log=True)

model = Sequential()

model.add(InputLayer(shape=(input_length, input_dimension)))

model.add(Flatten())

model.add(Dense(num_units_1, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(dropout))
for _ in range(num_layers - 1):
    model.add(Dense(num_units_2, activation='relu'))

model.add(Dropout(dropout))
model.add(Dense(...))

model.compile(optimizer=Adam(learning_rate=learning_rate), ...)
