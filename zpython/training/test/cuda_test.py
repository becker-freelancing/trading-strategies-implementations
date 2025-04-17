import torch

print("CUDA verfügbar:", torch.cuda.is_available())
print("Aktives Gerät:", torch.cuda.current_device())
print("Gerätename:",
      torch.cuda.get_device_name(torch.cuda.current_device()) if torch.cuda.is_available() else "Keine GPU")

import torch
import torch.nn as nn
import torch.optim as optim
import optuna
from torch.utils.data import DataLoader, TensorDataset

# GPU-Unterstützung
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(device)
# Beispiel-Dummy-Daten (kann ersetzt werden)
X = torch.randn(100000, 13, 52)  # 100 Samples, Input: (13, 52)
y = torch.randn(100000, 10, 1)  # Output: (10, 1)

print(X.shape)

dataset = TensorDataset(X, y)
dataloader = DataLoader(dataset, batch_size=64, shuffle=True)


# Netzwerkdefinition mit hyperparametern
class MyModel(nn.Module):
    def __init__(self, trial):
        super(MyModel, self).__init__()
        input_size = 13 * 52
        output_size = 10 * 1
        hidden_size = trial.suggest_int("hidden_size", 64, 512)
        num_layers = trial.suggest_int("num_layers", 1, 3)
        dropout_rate = trial.suggest_float("dropout", 0.1, 0.5)

        layers = []
        in_features = input_size
        for _ in range(num_layers):
            layers.append(nn.Linear(in_features, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
            in_features = hidden_size

        layers.append(nn.Linear(hidden_size, output_size))
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten input: (13, 52) -> (676,)
        return self.model(x)


# Trainings- und Evaluierungsfunktion
def train_model(trial):
    print("Train")
    model = MyModel(trial).to(device)
    criterion = nn.MSELoss()

    optimizer_name = trial.suggest_categorical("optimizer", ["Adam", "SGD", "RMSprop"])
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    optimizer = getattr(optim, optimizer_name)(model.parameters(), lr=lr)

    for epoch in range(10):  # klein halten für Optuna-Speed
        model.train()
        total_loss = 0
        for batch_X, batch_y in dataloader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y.view(batch_y.size(0), -1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
    return total_loss / len(dataloader)


# Optuna-Studie
study = optuna.create_study(direction="minimize")
study.optimize(train_model, n_trials=20)

# Beste Hyperparameter anzeigen
print("Beste Parameter:", study.best_params)
