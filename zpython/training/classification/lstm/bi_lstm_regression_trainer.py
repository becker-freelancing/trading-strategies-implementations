from keras import Model
from keras.api.layers import Dense, InputLayer, LSTM, Bidirectional
from keras.api.models import Sequential
from keras.api.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.model.regime_model import ModelProvider
from zpython.training.classification.classification_model_trainer import \
    ClassificationModelTrainer


class NNRegressionTrainer(ClassificationModelTrainer):

    def __init__(self):
        super().__init__("bilstm", MinMaxScaler)

    def _get_target_column(self):
        return "logReturn_closeBid_1min"

    def _get_max_input_length(self) -> int:
        return 150

    def _create_model(self, trial: Trial) -> (Model, int, dict):
        # Hyperparameter von Optuna
        num_layers = trial.suggest_int('num_layers', 1, 2)  # Anzahl der Schichten
        num_units_input = trial.suggest_int('num_units_input', 32, 128)  # Anzahl der Neuronen pro Schicht
        num_units = trial.suggest_int('num_units', 32, 128)  # Anzahl der Neuronen pro Schicht
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)  # Lernrate
        input_length = trial.suggest_int('input_length', 30, 150)

        params = {
            "num_layers": num_layers,
            "num_units": num_units,
            "learning_rate": learning_rate,
            "input_length": input_length,
            "num_units_input": num_units_input
        }

        # Modell erstellen
        def model_provider(input_dimension):
            model = Sequential()
            model.add(InputLayer(shape=(input_length, input_dimension)))
            if num_layers == 1:
                model.add(Bidirectional(LSTM(num_units_input, return_sequences=False)))
            else:
                model.add(Bidirectional(LSTM(num_units_input, return_sequences=True)))

            for i in range(num_layers - 1):  # Weitere Schichten
                if i == num_layers - 2:
                    model.add(Bidirectional(LSTM(num_units, return_sequences=False)))
                else:
                    model.add(Bidirectional(LSTM(num_units, return_sequences=True)))

            model.add(Dense(self._get_output_length(), activation='softmax'))

            # Kompilieren des Modells
            model.compile(optimizer=Adam(learning_rate=learning_rate), loss="categorical_crossentropy",
                          metrics=self._get_metrics())
            return model

        return ModelProvider(model_provider), input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_layers", "num_units", "learning_rate", "input_length", "num_units_input"]


def train_bi_lstm():
    trainer = NNRegressionTrainer()
    trainer.train_model()


if __name__ == "__main__":
    train_bi_lstm()
