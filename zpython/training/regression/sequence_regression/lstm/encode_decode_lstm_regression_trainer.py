from keras import Model
from keras.api.layers import Dense, InputLayer, LSTM, RepeatVector, TimeDistributed
from keras.api.models import Sequential
from keras.api.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.model.regime_model import ModelProvider
from zpython.training.regression.sequence_regression.sequence_regression_model_trainer import \
    SequenceRegressionModelTrainer
from zpython.util.training.loss import PNLLoss


class NNRegressionTrainer(SequenceRegressionModelTrainer):

    def __init__(self):
        super().__init__("encodedecodelstm", MinMaxScaler)

    def _get_output_length(self):
        return 30

    def _get_target_column(self):
        return "logReturn_closeBid_1min"

    def _get_max_input_length(self) -> int:
        return 150

    def _create_model(self, trial: Trial) -> (Model, int, dict):
        # Hyperparameter von Optuna
        num_units_input = trial.suggest_int('num_units_input', 32, 128)  # Anzahl der Neuronen pro Schicht
        num_units = trial.suggest_int('num_units', 32, 128)  # Anzahl der Neuronen pro Schicht
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)  # Lernrate
        input_length = trial.suggest_int('input_length', 30, 150)

        params = {
            "num_units": num_units,
            "learning_rate": learning_rate,
            "input_length": input_length,
            "num_units_input": num_units_input
        }

        # Modell erstellen
        def model_provider(input_dimension):
            model = Sequential()
            model.add(InputLayer(shape=(input_length, input_dimension)))
            model.add(LSTM(num_units_input, return_sequences=False))

            model.add(RepeatVector(30))
            model.add(LSTM(num_units, activation="relu", return_sequences=True))
            model.add(TimeDistributed(Dense(self._get_output_length())))

            # Kompilieren des Modells
            model.compile(optimizer=Adam(learning_rate=learning_rate), loss=PNLLoss(),
                          metrics=self._get_metrics())
            return model

        return ModelProvider(model_provider), input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_layers", "num_units", "learning_rate", "num_units_dropout"]


def train_encode_decose_lstm():
    trainer = NNRegressionTrainer()
    trainer.train_model()


if __name__ == "__main__":
    train_encode_decose_lstm()
