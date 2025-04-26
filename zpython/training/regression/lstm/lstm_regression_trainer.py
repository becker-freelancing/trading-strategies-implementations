from keras import Model
from keras.api.layers import Dense, InputLayer, LSTM
from keras.api.models import Sequential
from keras.api.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.training.regression.regression_model_trainer import RegressionModelTrainer


class NNRegressionTrainer(RegressionModelTrainer):

    def __init__(self):
        super().__init__("lstm", MinMaxScaler)

    def _get_output_length(self):
        return 30

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
        model = Sequential()
        model.add(InputLayer(shape=(input_length, 52)))
        if num_layers == 1:
            model.add(LSTM(num_units_input, return_sequences=False))
        else:
            model.add(LSTM(num_units_input, return_sequences=True))

        for i in range(num_layers - 1):  # Weitere Schichten
            if i == num_layers - 2:
                model.add(LSTM(num_units, return_sequences=False))
            else:
                model.add(LSTM(num_units, return_sequences=True))

        model.add(Dense(self._get_output_length(), activation='linear'))

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
