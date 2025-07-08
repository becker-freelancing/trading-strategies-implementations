def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0.):
    x = MultiHeadAttention(key_dim=head_size, num_heads=num_heads, dropout=dropout)(inputs, inputs)
    x = Dropout(dropout)(x)
    x = LayerNormalization(epsilon=1e-6)(x)
    res = x + inputs

    x = Conv1D(filters=ff_dim, kernel_size=1, activation='relu')(res)
    x = Dropout(dropout)(x)
    x = Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    x = LayerNormalization(epsilon=1e-6)(x)
    return x + res


head_size = trial.suggest_int('head_size', 32, 128)
num_heads = trial.suggest_int('num_heads', 2, 6)
learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)
input_length = trial.suggest_int('input_length', 30, 150)
ff_dim = trial.suggest_int("ff_dim", 64, 256)
dropout = trial.suggest_float("dropout", 0.05, 0.3)

inputs = Input(shape=(input_length, input_dimension))

x = self.transformer_encoder(inputs, head_size=head_size, num_heads=num_heads, ff_dim=ff_dim, dropout=dropout)
x = self.transformer_encoder(x, head_size=head_size, num_heads=num_heads, ff_dim=ff_dim, dropout=dropout)

x = GlobalAveragePooling1D()(x)
x = Dense(128, activation="relu")(x)
x = Dropout(0.2)(x)
outputs = Dense(...)(x)

model = Model(inputs, outputs)
model.compile(optimizer=Adam(learning_rate=learning_rate), ...)
