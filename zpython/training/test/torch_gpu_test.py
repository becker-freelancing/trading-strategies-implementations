import keras
import torch

print("Keras Backend: ", keras.backend.backend())
print("CUDA verfügbar:", torch.cuda.is_available())
print("Name der GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Keine GPU")
