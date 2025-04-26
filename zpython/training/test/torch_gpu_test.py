import subprocess

import keras
import torch


def get_free_gpu_memory():
    result = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,nounits,noheader']
    )
    return [int(x) for x in result.decode('utf-8').strip().split('\n')][0] * 1.049 * 1E6




print("Keras Backend: ", keras.backend.backend())
print("CUDA verfügbar:", torch.cuda.is_available())
print("Name der GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Keine GPU")
print("Free Memory: ", get_free_gpu_memory())
