from keras import Model
from keras.api.layers import Dense, Flatten, Input, Add
from keras.api.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.model.regime_model import ModelProvider
from zpython.training.regression.regression_model_trainer import RegressionModelTrainer
from zpython.util.loss import PNLLoss


class NNRegressionTrainer(RegressionModelTrainer):

    def __init__(self):
        super().__init__("nnresidual", MinMaxScaler)

    def _get_output_length(self):
        return 30

    def _get_target_column(self):
        return "logReturn_closeBid_1min"

    def _get_max_input_length(self) -> int:
        return 150

    def _create_model(self, trial: Trial) -> (Model, int, dict):
        # Hyperparameter von Optuna
        num_layers = trial.suggest_int('num_layers', 1, 3)  # Anzahl der Schichten
        num_units = trial.suggest_int('num_units', 32, 128)  # Anzahl der Neuronen pro Schicht
        num_units_res_prep = trial.suggest_int('num_units_res_prep', 32, 128)  # Anzahl der Neuronen pro Schicht
        num_units_res = trial.suggest_int('num_units_res', 32, 128)  # Anzahl der Neuronen pro Schicht
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)  # Lernrate
        input_length = trial.suggest_int('input_length', 5, 150)
        flatten_before = trial.suggest_categorical("flatten_before", [True, False])

        params = {
            "num_layers": num_layers,
            "num_units": num_units,
            "learning_rate": learning_rate,
            "input_length": input_length,
            "flatten_before": flatten_before,
            "num_units_res_prep": num_units_res_prep,
            "num_units_res": num_units_res
        }

        def model_provider(input_dimension):
            input_layer = Input(shape=(input_length, input_dimension))
            x = Flatten()(input_layer)
            res = Dense(num_units_res_prep, activation="relu")(x)
            res = Dense(num_units_res, activation="linear")(res)
            x = Dense(num_units_res, activation="relu")(x)
            x = Add()([x, res])
            x = Dense(num_units, activation="relu")(x)
            output = Dense(self._get_output_length())(x)

            model = Model(input_layer, output)

            # Kompilieren des Modells
            model.compile(optimizer=Adam(learning_rate=learning_rate), loss=PNLLoss(),
                          metrics=self._get_metrics())
            return model

        return ModelProvider(model_provider), input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_layers",
                "num_units",
                "learning_rate",
                "input_length",
                "flatten_before",
                "num_units_res_prep",
                "num_units_res"]


if __name__ == "__main__":
    trainer = NNRegressionTrainer()
    trainer.train_model()
