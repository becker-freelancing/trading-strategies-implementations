from keras.layers import Dense, InputLayer, Flatten
from keras.models import Sequential
from keras.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.model.regime_model import ModelProvider
from zpython.training.regression.single_regression.single_regression_model_trainer import SingleRegressionModelTrainer
from zpython.util.training.loss import PNLLoss


class NNRegressionTrainer(SingleRegressionModelTrainer):

    def __init__(self):
        super().__init__("nn_single", MinMaxScaler)

    def _create_model(self, trial: Trial) -> (ModelProvider, int, dict):
        # Hyperparameter von Optuna
        num_layers = trial.suggest_int('num_layers', 1, 3)  # Anzahl der Schichten
        num_units = trial.suggest_int('num_units', 32, 128)  # Anzahl der Neuronen pro Schicht
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)  # Lernrate
        input_length = trial.suggest_int('input_length', 5, 150)
        flatten_before = trial.suggest_categorical("flatten_before", [True, False])

        params = {
            "num_layers": num_layers,
            "num_units": num_units,
            "learning_rate": learning_rate,
            "input_length": input_length,
            "flatten_before": flatten_before
        }

        def model_provider(input_dimension):
            # Modell erstellen
            model = Sequential()
            model.add(InputLayer(shape=(input_length, input_dimension)))
            if flatten_before:
                model.add(Flatten())
            model.add(Dense(num_units, activation='relu'))  # Eingabeschicht
            for _ in range(num_layers - 1):  # Weitere Schichten
                model.add(Dense(num_units, activation='relu'))
            if not flatten_before:
                model.add(Flatten())
            model.add(Dense(self._get_output_length(), activation='linear'))  # Ausgangsschicht (10 Klassen für MNIST)

            # Kompilieren des Modells
            model.compile(optimizer=Adam(learning_rate=learning_rate), loss=PNLLoss(),
                          metrics=self._get_metrics())
            return model

        return ModelProvider(model_provider), input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_layers", "num_units", "learning_rate", "input_length", "flatten_before"]


def train_nn():
    trainer = NNRegressionTrainer()
    trainer.train_model()


if __name__ == "__main__":
    train_nn()
