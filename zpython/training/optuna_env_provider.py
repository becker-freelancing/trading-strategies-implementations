import os
from pathlib import Path

from dotenv import load_dotenv


def get_optuna_storage_url():
    _load_env()
    env = os.environ
    return f"mysql+pymysql://{env['DB_USER_OPTUNA']}:{env['DB_PASSWORD_OPTUNA']}@{env['DB_SERVER_OPTUNA']}/{env['DB_NAME_OPTUNA']}"


def _load_env():
    env_path = Path(__file__).parent
    while not str(env_path).endswith("trading-strategies-implementations"):
        env_path = env_path.parent
    env_path = env_path.joinpath("optuna_db.env")
    load_dotenv(env_path)


def get_optuna_study_name():
    _load_env()
    env = os.environ
    return env.get("OPTUNA_STUDY_NAME")
