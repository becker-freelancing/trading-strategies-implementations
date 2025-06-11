import os


def get_base_path():
    app_data_path = os.getenv("APPDATA")

    if not app_data_path:
        user_home = os.path.expanduser("~")
        app_data_path = os.path.join(user_home, ".config")

    return (app_data_path + "/krypto-java/").replace("\\", "/")


def from_relative_path(path):
    return get_base_path() + path


def root_result_dir():
    return from_relative_path(".results/")


def result_dir_for_strategy(strategy_name):
    return os.path.join(root_result_dir(), strategy_name)


def from_relative_path_from_models_dir(path):
    return from_relative_path(f"models/{path}")
