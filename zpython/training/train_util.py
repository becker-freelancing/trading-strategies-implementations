import os
import shutil
import subprocess

import numpy as np
import torch


def clean_directory(path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def to_tensor(data: np.ndarray):
    return torch.from_numpy(data).float().to(get_device())


def get_free_gpu_memory():
    result = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader']
    )
    return [int(x) for x in result.decode('utf-8').strip().split('\n')][0] * 1.049 * 1E6


def run_study_for_model(model_class, model_name, study_name, storage_url, metrics_lock,
                        trials_lock, header_content, trial_params_keys):
    trainer = model_class()
    trainer.model_name = model_name
    trainer.study_name = study_name
    trainer.study_storage = storage_url
    trainer.study_name = study_name
    trainer.metrics_lock = metrics_lock
    trainer.trials_lock = trials_lock
    trainer.header_content = header_content
    trainer.trial_params_keys = trial_params_keys
    trainer._run_study()
