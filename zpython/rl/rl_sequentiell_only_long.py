import gymnasium as gym
from stable_baselines3 import PPO

from zpython.rl.data_reader import read_all
from zpython.rl.env_only_long import TradingEnvOnlyLong

merged = read_all()

print(merged)

EPISODE_MAX_LEN = 1440
LOOKBACK_WINDOW_LEN = EPISODE_MAX_LEN
TRAIN_START = 0
TRAIN_END = 79680
TEST_START = 79680
TEST_END = 99600
FEATURE_DIM = 227
LOGICAL_SEGMENTS = [2, 2, 57, 56, 55, 55]

from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor

env = TradingEnvOnlyLong(merged, EPISODE_MAX_LEN, LOOKBACK_WINDOW_LEN, TRAIN_START, TRAIN_END, TEST_START, TEST_END)
eval_env = TradingEnvOnlyLong(merged, EPISODE_MAX_LEN, LOOKBACK_WINDOW_LEN, TRAIN_START, TRAIN_END, TEST_START,
                              TEST_END,
                      regime="evaluation")

import datetime
import joblib

dt_str = str(datetime.datetime.now()).replace(":", "_")


class InfoLoggerWrapper(gym.Wrapper):
    def __init__(self, env: TradingEnvOnlyLong, file_path, file_name):
        super().__init__(env)
        self.file_name = file_name
        self.file_path = file_path
        self.save_id = 0

    def step(self, action):
        obs, reward, done, x, info = self.env.step(action)
        if done:
            path = f"{self.file_path}{self.save_id}_{self.file_name}"
            self.save_id = self.save_id + 1
            joblib.dump(self.env.statistics_recorder, path, compress=3)
        return obs, reward, done, x, info


# Build Config
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from zpython.rl.transformer_2 import TransformerModel

from stable_baselines3.common.policies import ActorCriticPolicy


class TransformerFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim):
        super().__init__(observation_space, features_dim)
        self.model = TransformerModel(LOOKBACK_WINDOW_LEN, FEATURE_DIM, LOGICAL_SEGMENTS)

    def forward(self, observations):
        logits, _ = self.model(observations)
        return logits


from stable_baselines3.common.torch_layers import MlpExtractor


class CustomActorCriticPolicy(ActorCriticPolicy):
    def __init__(self, observation_space, action_space, lr_schedule, **kwargs):
        super().__init__(
            observation_space,
            action_space,
            lr_schedule,
            features_extractor_class=TransformerFeatureExtractor,
            features_extractor_kwargs=dict(features_dim=4),  # passend zu deinem Modell
            **kwargs
        )

    def _build_mlp_extractor(self) -> None:
        """
        Create the policy and value networks.
        Part of the layers can be shared.
        """
        # Note: If net_arch is None and some features extractor is used,
        #       net_arch here is an empty list and mlp_extractor does not
        #       really contain any layers (acts like an identity module).
        self.mlp_extractor = MlpExtractor(
            4,
            net_arch=self.net_arch,
            activation_fn=self.activation_fn,
            device=self.device,
        )


env = InfoLoggerWrapper(env, file_path=f"./logs_{dt_str}/", file_name="info_train_logger.dump.gz")
eval_env = InfoLoggerWrapper(eval_env, file_path=f"./logs_{dt_str}/", file_name="info_eval_logger.dump.gz")
env = Monitor(env, filename=f"./logs_{dt_str}/custom_train_monitor.csv")
eval_env = Monitor(eval_env, filename=f"./logs_{dt_str}/custom_eval_monitor.csv")

checkpoint_callback = CheckpointCallback(
    save_freq=100,  # Anzahl an Trainingsschritten
    save_path=f'./checkpoints_{dt_str}/',  # Speicherpfad
    name_prefix='ppo_model'  # Dateiname beginnt damit
)

eval_callback = EvalCallback(
    eval_env,
    best_model_save_path=f'./best_model_{dt_str}/',
    log_path=f'./logs_{dt_str}/',
    eval_freq=10_000,
    deterministic=True,
    render=False,
    verbose=2
)

model = PPO(CustomActorCriticPolicy, env, verbose=2, tensorboard_log=f"./logs_{dt_str}/tensorboard/")
model.learn(total_timesteps=1_000_000, callback=[checkpoint_callback, eval_callback], progress_bar=True)

obs = env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, done, _, info = env.step(action)
    print(f"Portfolio Value: {info['portfolio_value']}")
