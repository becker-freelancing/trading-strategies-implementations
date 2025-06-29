from keras import Model
from keras.api.layers import Dense, Flatten, Conv1D, MaxPooling1D, InputLayer
from keras.api.models import Sequential
from keras.api.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.model.regime_model import ModelProvider
from zpython.training.classification_without_pca.classification_model_trainer import \
    ClassificationWithoutPcaModelTrainer


class CNNRegressionTrainer(ClassificationWithoutPcaModelTrainer):

    def __init__(self):
        super().__init__("deepcnn", MinMaxScaler)

    def _get_target_column(self):
        return "logReturn_closeBid_1min"

    def _get_max_input_length(self) -> int:
        return 150

    def _create_model(self, trial: Trial) -> (Model, int, dict):
        # Hyperparameter von Optuna
        num_units_cnn = trial.suggest_int('num_units_cnn', 32, 128)  # Anzahl der Neuronen pro Schicht
        num_units = trial.suggest_int('num_units', 32, 128)  # Anzahl der Neuronen pro Schicht
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)  # Lernrate
        input_length = trial.suggest_int('input_length', 5, 150)
        flatten_before = trial.suggest_categorical("flatten_before", [True, False])
        kernel_size = trial.suggest_int("kernel_size", 2, 5)
        pool_size = trial.suggest_int("pool_size", 1, 5)

        params = {
            "num_units_cnn": num_units_cnn,
            "learning_rate": learning_rate,
            "input_length": input_length,
            "flatten_before": flatten_before,
            "kernel_size": kernel_size,
            "pool_size": pool_size,
            "num_units": num_units
        }

        # Modell erstellen
        def model_provider(input_dimension):
            model = Sequential()
            model.add(InputLayer(shape=(input_length, input_dimension)))
            model.add(Conv1D(num_units_cnn, kernel_size=kernel_size, activation="relu", padding="same"))
            model.add(Conv1D(num_units_cnn, kernel_size=kernel_size, activation="relu", padding="same"))
            model.add(MaxPooling1D(pool_size=pool_size))
            if flatten_before:
                model.add(Flatten())
            model.add(Dense(num_units, activation="relu"))
            if not flatten_before:
                model.add(Flatten())
            model.add(Dense(self._get_output_length(), activation='softmax'))

            # Kompilieren des Modells
            model.compile(optimizer=Adam(learning_rate=learning_rate), loss="categorical_crossentropy",
                          metrics=self._get_metrics())
            return model

        return ModelProvider(model_provider), input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_units_cnn",
                "learning_rate",
                "input_length",
                "flatten_before",
                "kernel_size",
                "pool_size",
                "num_units"]


def train_deep_cnn():
    trainer = CNNRegressionTrainer()
    trainer.train_model()


if __name__ == "__main__":
    train_deep_cnn()
