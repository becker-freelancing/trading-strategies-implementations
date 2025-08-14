num_layers = trial.suggest_int('num_layers', 1, 3)
num_units = trial.suggest_int('num_units', 32, 128)
input_length = trial.suggest_int('input_length', 5, 150)
learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2,
                                    log=True)
flatten_before = trial.suggest_categorical('flatten_before',
                                           [True, False])

model = Sequential()

model.add(InputLayer(shape=(input_length, input_dimension)))

if flatten_before:
    model.add(Flatten())

model.add(Dense(num_units, activation='relu'))
for _ in range(num_layers - 1):
    model.add(Dense(num_units, activation='relu'))

if not flatten_before:
    model.add(Flatten())

model.add(Dense(...))

model.compile(optimizer=Adam(learning_rate=learning_rate), ...)
