num_units_cnn = trial.suggest_int('num_units_cnn', 32, 128)
num_units = trial.suggest_int('num_units', 32, 128)
input_length = trial.suggest_int('input_length', 5, 150)
kernel_size_1 = trial.suggest_int('kernel_size_1', 2, 9)
kernel_size_2 = trial.suggest_int('kernel_size_2', 2, 9)
kernel_size_3 = trial.suggest_int('kernel_size_3', 2, 9)
pool_size = trial.suggest_int('pool_size', 1, 5)
learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2,
                                    log=True)

input_layer = Input(shape=(input_length, input_dimension))
conv_1 = Conv1D(num_units_cnn, kernel_size=kernel_size_1,
                padding='same', activation='relu')(input_layer)
conv_2 = Conv1D(num_units_cnn, kernel_size=kernel_size_2,
                padding='same', activation='relu')(input_layer)
conv_3 = Conv1D(num_units_cnn, kernel_size=kernel_size_3,
                padding='same', activation='relu')(input_layer)

concat = Concatenate()([conv_1, conv_2, conv_3])

gap = GlobalAveragePooling1D()(concat)
dense1 = Dense(num_units, activation='relu')(gap)

output_layer = Dense(...)(dense1)

model = Model(input_layer, output_layer)

model.compile(optimizer=Adam(learning_rate=learning_rate), ...)
