from keras import Model
from keras.api.layers import Dense, InputLayer, Flatten, BatchNormalization, Dropout
from keras.api.models import Sequential
from keras.api.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.training.regression.regression_model_trainer import RegressionModelTrainer


class NNRegressionTrainer(RegressionModelTrainer):

    def __init__(self):
        super().__init__("nndropout", MinMaxScaler)

    def _get_output_length(self):
        return 30

    def _get_target_column(self):
        return "logReturn_closeBid_1min"

    def _get_max_input_length(self) -> int:
        return 150

    def _create_model(self, trial: Trial) -> (Model, int, dict):
        # Hyperparameter von Optuna
        num_layers = trial.suggest_int('num_layers', 1, 3)  # Anzahl der Schichten
        num_units_1 = trial.suggest_int('num_units_1', 32, 256)  # Anzahl der Neuronen pro Schicht
        num_units_2 = trial.suggest_int('num_units_1', 32, 256)  # Anzahl der Neuronen pro Schicht
        dropout = trial.suggest_float('dropout', 0.05, 0.35)  # Anzahl der Neuronen pro Schicht
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)  # Lernrate
        input_length = trial.suggest_int('input_length', 5, 150)

        params = {
            "num_layers": num_layers,
            "num_units_1": num_units_1,
            "num_units_2": num_units_2,
            "dropout": dropout,
            "learning_rate": learning_rate,
            "input_length": input_length
        }

        # Modell erstellen
        model = Sequential()
        model.add(InputLayer(shape=(input_length, 52)))
        model.add(Flatten())
        model.add(Dense(num_units_1, activation='relu'))  # Eingabeschicht
        model.add(BatchNormalization())
        model.add(Dropout(dropout))
        for _ in range(num_layers - 1):  # Weitere Schichten
            model.add(Dense(num_units_2, activation='relu'))
        model.add(Dropout(dropout))
        model.add(Dense(self._get_output_length(), activation='linear'))  # Ausgangsschicht (10 Klassen für MNIST)

        # Kompilieren des Modells
        model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mean_squared_error',
                      metrics=self._get_metrics())

        return model, input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_layers",
                "num_units_1",
                "num_units_2",
                "dropout",
                "learning_rate",
                "input_length"]

    def _get_optuna_optimization_metric_name(self):
        return 'val_rmse'

    def _get_optuna_optimization_metric_direction(self):
        return 'minimize'


if __name__ == "__main__":
    trainer = NNRegressionTrainer()
    trainer.train_model()
