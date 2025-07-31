num_units_cnn = trial.suggest_int('num_units_cnn', 32, 128)
num_units = trial.suggest_int('num_units', 32, 128)
num_units_gru = trial.suggest_int('num_units_gru', 32, 128)
input_length = trial.suggest_int('input_length', 5, 150)
kernel_size = trial.suggest_int("kernel_size", 2, 5)
pool_size = trial.suggest_int("pool_size", 1, 5)
learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2,
                                    log=True)

model = Sequential()
model.add(InputLayer(shape=(input_length, input_dimension)))
model.add(Conv1D(num_units_cnn, kernel_size=kernel_size,
                 activation="relu"))
model.add(MaxPooling1D(pool_size=pool_size))
model.add(GRU(num_units_gru, return_sequences=False))
model.add(Dense(num_units, activation="relu"))
model.add(Dense(...))

model.compile(optimizer=Adam(learning_rate=learning_rate), ...)
