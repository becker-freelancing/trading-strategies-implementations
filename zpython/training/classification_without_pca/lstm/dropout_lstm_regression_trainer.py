from keras import Model
from keras.layers import Dense, InputLayer, LSTM, Dropout
from keras.models import Sequential
from keras.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.model.regime_model import ModelProvider
from zpython.training.classification_without_pca.classification_model_trainer import \
    ClassificationWithoutPcaModelTrainer


class NNRegressionTrainer(ClassificationWithoutPcaModelTrainer):

    def __init__(self):
        super().__init__("dropoutlstm", MinMaxScaler)

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
        dropout = trial.suggest_float('dropout', 0.05, 0.5)

        params = {
            "num_layers": num_layers,
            "num_units": num_units,
            "learning_rate": learning_rate,
            "input_length": input_length,
            "num_units_input": num_units_input,
            "dropout": dropout
        }

        # Modell erstellen
        def model_provider(input_dimension):
            model = Sequential()
            model.add(InputLayer(shape=(input_length, input_dimension)))
            if num_layers == 1:
                model.add(LSTM(num_units_input, return_sequences=False))
            else:
                model.add(LSTM(num_units_input, return_sequences=True))

            model.add(Dropout(dropout))
            for i in range(num_layers - 1):  # Weitere Schichten
                if i == num_layers - 2:
                    model.add(LSTM(num_units, return_sequences=False))
                else:
                    model.add(LSTM(num_units, return_sequences=True))
                model.add(Dropout(dropout))

            model.add(Dense(self._get_output_length(), activation='softmax'))

            # Kompilieren des Modells
            model.compile(optimizer=Adam(learning_rate=learning_rate), loss="categorical_crossentropy",
                          metrics=self._get_metrics())
            return model

        return ModelProvider(model_provider), input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_layers", "num_units", "learning_rate", "input_length", "num_units_input", "dropout"]


def train_dropout_lstm():
    trainer = NNRegressionTrainer()
    trainer.train_model()


if __name__ == "__main__":
    train_dropout_lstm()
