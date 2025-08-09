num_layers = trial.suggest_int('num_layers', 1, 3)
num_units = trial.suggest_int('num_units', 32, 128)
num_units_res_prep = trial.suggest_int('num_units_res_prep', 32, 128)
num_units_res = trial.suggest_int('num_units_res', 32, 128)
input_length = trial.suggest_int('input_length', 5, 150)
learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2,
                                    log=True)

input_layer = Input(shape=(input_length, input_dimension))

x = Flatten()(input_layer)

res = Dense(num_units_res_prep, activation='relu')(x)
res = Dense(num_units_res, activation='linear')(res)

x = Dense(num_units_res, activation='relu')(x)
x = Add()([x, res])
x = Dense(num_units, activation='relu')(x)

output = Dense(...)(x)

model = Model(input_layer, output)

model.compile(optimizer=Adam(learning_rate=learning_rate), ...)
