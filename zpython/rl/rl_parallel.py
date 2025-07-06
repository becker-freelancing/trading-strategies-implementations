import tracemalloc

import gymnasium as gym
from stable_baselines3 import PPO

from zpython.rl.data_reader import read_all
from zpython.rl.env_only_long import TradingEnvOnlyLong


def run():
    tracemalloc.start()
    merged = read_all()

    print(merged)

    EPISODE_MAX_LEN = 1440
    LOOKBACK_WINDOW_LEN = EPISODE_MAX_LEN
    TRAIN_START = 0
    TRAIN_END = 10000
    TEST_START = 10000
    TEST_END = 20000
    FEATURE_DIM = 227
    LOGICAL_SEGMENTS = [2, 2, 57, 56, 55, 55]

    from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
    import datetime
    import joblib

    dt_str = str(datetime.datetime.now()).replace(":", "_")

    import gc

    class InfoLoggerWrapper(gym.Wrapper):
        def __init__(self, env: TradingEnvOnlyLong, env_id, file_path, file_name):
            super().__init__(env)
            self.file_name = file_name
            self.file_path = file_path
            self.save_id = 0
            self.subsave_id = 0
            self.env_id = env_id
            self.buffer = []

        def step(self, action):
            obs, reward, done, x, info = self.env.step(action)
            self.buffer.append(info)
            if len(self.buffer) >= 20:
                path = f"{self.file_path}{self.env_id}_{self.save_id}_{self.subsave_id}_{self.file_name}"
                print(f"Saving Buffer {path}")
                joblib.dump(self.buffer, path, compress=1)
                self.subsave_id = self.subsave_id + 1
                self.buffer = []
                gc.collect()
            if done:
                self.save_id = self.save_id + 1
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


    import os


    def make_env(env_id: int, regime="training"):
        def _init():
            env = TradingEnvOnlyLong(
                merged,
                EPISODE_MAX_LEN,
                LOOKBACK_WINDOW_LEN,
                TRAIN_START,
                TRAIN_END,
                TEST_START,
                TEST_END,
                regime=regime
            )
            # Logging-Verzeichnis pro Environment
            env_log_dir = f"./logs_{dt_str}/env_{env_id}_{regime}/"
            os.makedirs(env_log_dir, exist_ok=True)

            env = InfoLoggerWrapper(env, env_id=env_id, file_path=env_log_dir, file_name="info_logger.dump.gz")
            return env

        return _init

    from stable_baselines3.common.vec_env import DummyVecEnv

    num_envs = 16  # oder so viele wie CPU-Kerne verfügbar sind
    env = DummyVecEnv([make_env(i) for i in range(num_envs)])
    eval_env = make_env(999, regime="evaluation")()  # normal, nicht parallelisiert

    model = PPO(CustomActorCriticPolicy, env, verbose=2,
                n_steps=256,
                batch_size=256 // num_envs
                # tensorboard_log=f"./logs_{dt_str}/tensorboard/"
                )

    checkpoint_callback = CheckpointCallback(
        save_freq=10000 // num_envs,  # muss größer sein bei parallelisierten Umgebungen!
        save_path=f'./checkpoints_{dt_str}/',
        name_prefix='ppo_model',
        verbose=2
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

    model.learn(total_timesteps=1_000_000, callback=[checkpoint_callback, eval_callback], progress_bar=True)

    obs = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, _, info = env.step(action)
        print(f"Portfolio Value: {info['portfolio_value']}")

if __name__ == "__main__":
    run()