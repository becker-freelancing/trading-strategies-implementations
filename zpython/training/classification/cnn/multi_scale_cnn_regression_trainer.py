from keras import Model
from keras.layers import Dense, Conv1D, Input, Concatenate, GlobalAveragePooling1D
from keras.optimizers import Adam
from optuna import Trial
from sklearn.preprocessing import MinMaxScaler

from zpython.model.regime_model import ModelProvider
from zpython.training.classification.classification_model_trainer import \
    ClassificationModelTrainer


class CNNRegressionTrainer(ClassificationModelTrainer):

    def __init__(self):
        super().__init__("multiscalecnn", MinMaxScaler)

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
        kernel_size_1 = trial.suggest_int("kernel_size_1", 2, 9)
        kernel_size_2 = trial.suggest_int("kernel_size_2", 2, 9)
        kernel_size_3 = trial.suggest_int("kernel_size_3", 2, 9)
        pool_size = trial.suggest_int("pool_size", 1, 5)

        params = {
            "num_units_cnn": num_units_cnn,
            "learning_rate": learning_rate,
            "input_length": input_length,
            "kernel_size": kernel_size_1,
            "pool_size": pool_size,
            "num_units": num_units
        }

        # Modell erstellen
        def model_provider(input_dimension):
            input_layer = Input(shape=(input_length, input_dimension))
            conv_1 = Conv1D(num_units_cnn, kernel_size=kernel_size_1, padding="same", activation="relu")(input_layer)
            conv_2 = Conv1D(num_units_cnn, kernel_size=kernel_size_2, padding="same", activation="relu")(input_layer)
            conv_3 = Conv1D(num_units_cnn, kernel_size=kernel_size_3, padding="same", activation="relu")(input_layer)

            concat = Concatenate()([conv_1, conv_2, conv_3])

            gap = GlobalAveragePooling1D()(concat)
            dense1 = Dense(num_units, activation="relu")(gap)

            output_layer = Dense(self._get_output_length(), activation='softmax')(dense1)

            model = Model(inputs=input_layer, outputs=output_layer)

            # Kompilieren des Modells
            model.compile(optimizer=Adam(learning_rate=learning_rate), loss="categorical_crossentropy",
                          metrics=self._get_metrics())
            return model

        return ModelProvider(model_provider), input_length, params

    def _get_optuna_trial_params(self) -> list[str]:
        return ["num_units_cnn",
                "learning_rate",
                "input_length",
                "kernel_size",
                "pool_size",
                "num_units"]


def train_multi_scale_cnn():
    trainer = CNNRegressionTrainer()
    trainer.train_model()


if __name__ == "__main__":
    train_multi_scale_cnn()
