from keras import Model
from keras.api.layers import Dense, InputLayer, Flatten
from keras.api.models import Sequential
from keras.api.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.training.regression.regression_model_trainer import RegressionModelTrainer


class NNRegressionTrainer(RegressionModelTrainer):

    def __init__(self):
        super().__init__("nn", MinMaxScaler)

    def _get_output_length(self):
        return 10

    def _get_target_column(self):
        return "logReturn_closeBid_1min"

    def _get_max_input_length(self) -> int:
        return 50

    def _create_model(self, trial: Trial) -> (Model, int, dict):
        # Hyperparameter von Optuna
        num_layers = trial.suggest_int('num_layers', 1, 3)  # Anzahl der Schichten
        num_units = trial.suggest_int('num_units', 32, 128)  # Anzahl der Neuronen pro Schicht
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)  # Lernrate
        input_length = trial.suggest_int('input_length', 5, 50)

        params = {
            "num_layers": num_layers,
            "num_units": num_units,
            "learning_rate": learning_rate,
            "input_length": input_length
        }

        # Modell erstellen
        model = Sequential()
        model.add(InputLayer(shape=(input_length, 52)))
        model.add(Flatten())
        model.add(Dense(num_units, activation='relu'))  # Eingabeschicht
        for _ in range(num_layers - 1):  # Weitere Schichten
            model.add(Dense(num_units, activation='relu'))
        model.add(Dense(10, activation='linear'))  # Ausgangsschicht (10 Klassen für MNIST)

        # Kompilieren des Modells
        model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mean_squared_error',
                      metrics=self._get_metrics())

        return model, input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_layers", "num_units", "learning_rate"]

    def _get_max_epochs_to_train(self):
        return 30

    def _get_optuna_optimization_metric_name(self):
        return 'val_rmse'

    def _get_optuna_optimization_metric_direction(self):
        return 'minimize'


if __name__ == "__main__":
    trainer = NNRegressionTrainer()
    trainer.train_model()
