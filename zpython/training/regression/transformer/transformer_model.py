from keras import Model
from keras.api.layers import Dense, MultiHeadAttention, LayerNormalization, Conv1D, \
    GlobalAveragePooling1D, Dropout, Input
from keras.api.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.model.regime_model import ModelProvider
from zpython.training.regression.regression_model_trainer import RegressionModelTrainer
from zpython.util.loss import PNLLoss


class TransformerModelTrainer(RegressionModelTrainer):

    def __init__(self):
        super().__init__("transformer", MinMaxScaler)

    def _get_output_length(self):
        return 30

    def _get_target_column(self):
        return "logReturn_closeBid_1min"

    def _get_max_input_length(self) -> int:
        return 150

    def transformer_encoder(self, inputs, head_size, num_heads, ff_dim, dropout=0.):
        # Multi-Head Attention Layer
        x = MultiHeadAttention(key_dim=head_size, num_heads=num_heads, dropout=dropout)(inputs, inputs)
        x = Dropout(dropout)(x)
        x = LayerNormalization(epsilon=1e-6)(x)
        res = x + inputs

        # Feed Forward Part
        x = Conv1D(filters=ff_dim, kernel_size=1, activation='relu')(res)
        x = Dropout(dropout)(x)
        x = Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
        x = LayerNormalization(epsilon=1e-6)(x)
        return x + res

    def _create_model(self, trial: Trial) -> (Model, int, dict):
        # Hyperparameter von Optuna
        head_size = trial.suggest_int('head_size', 32, 128)  # Anzahl der Neuronen pro Schicht
        num_heads = trial.suggest_int('num_heads', 2, 6)  # Anzahl der Neuronen pro Schicht
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)  # Lernrate
        input_length = trial.suggest_int('input_length', 30, 150)
        ff_dim = trial.suggest_int("ff_dim", 64, 256)
        dropout = trial.suggest_float("dropout", 0.05, 0.3)

        params = {
            "num_heads": num_heads,
            "learning_rate": learning_rate,
            "input_length": input_length,
            "head_size": head_size,
            "ff_dim": ff_dim,
            "dropout": dropout
        }

        def model_provider(input_dimension):
            # Modell erstellen
            inputs = Input(shape=(input_length, input_dimension))

            x = self.transformer_encoder(inputs, head_size=head_size, num_heads=num_heads, ff_dim=ff_dim,
                                         dropout=dropout)
            x = self.transformer_encoder(x, head_size=head_size, num_heads=num_heads, ff_dim=ff_dim, dropout=dropout)

            x = GlobalAveragePooling1D()(x)
            x = Dense(128, activation="relu")(x)
            x = Dropout(0.2)(x)
            outputs = Dense(self._get_output_length())(x)

            model = Model(inputs, outputs)
            model.compile(optimizer=Adam(learning_rate=learning_rate), loss=PNLLoss(), metrics=self._get_metrics())
            return model

        return ModelProvider(model_provider), input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_heads",
                "learning_rate",
                "input_length",
                "head_size",
                "ff_dim",
                "dropout"]


def train_transformer():
    trainer = TransformerModelTrainer()
    trainer.train_model()


if __name__ == "__main__":
    train_transformer()
