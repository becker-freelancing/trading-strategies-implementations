import matplotlib.pyplot as plt
import numpy as np
from keras.api.layers import Conv1D, Dense, Flatten, MaxPooling1D
from keras.api.models import Sequential
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


# **1. Erstellen einer synthetischen Zeitreihe**
def generate_time_series(n_samples=1000, timesteps=50):
    np.random.seed(42)
    x = np.linspace(0, 100, n_samples)
    y = np.sin(x) + np.random.normal(scale=0.1, size=n_samples)  # Sinuswelle mit Rauschen
    return x, y


x, y = generate_time_series()
scaler = MinMaxScaler()
y_scaled = scaler.fit_transform(y.reshape(-1, 1)).flatten()


# **2. Erstellen von Trainingssequenzen (Sliding Window)**
def create_sequences(data, timesteps):
    X, Y = [], []
    for i in range(len(data) - timesteps):
        X.append(data[i:i + timesteps])
        Y.append(data[i + timesteps])
    return np.array(X), np.array(Y)


timesteps = 20  # Fenstergröße
X, Y = create_sequences(y_scaled, timesteps)

# **3. Aufteilen der Daten in Trainings- und Testsets**
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# **4. Umformen für CNN (CNN erwartet 3D-Input: [Samples, Timesteps, Features])**
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# **5. Erstellen des CNN-Modells**
model = Sequential([
    Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(timesteps, 1)),
    MaxPooling1D(pool_size=2),
    Conv1D(filters=32, kernel_size=3, activation='relu'),
    Flatten(),
    Dense(50, activation='relu'),
    Dense(1)
])

# **6. Kompilieren und Trainieren des Modells**
model.compile(optimizer='adam', loss='mse')
history = model.fit(X_train, Y_train, epochs=1, batch_size=16, validation_data=(X_test, Y_test))

# **7. Evaluierung und Visualisierung der Vorhersagen**
Y_pred = model.predict(X_test)
Y_pred = scaler.inverse_transform(Y_pred.reshape(-1, 1))  # Zurückskalieren
Y_test_actual = scaler.inverse_transform(Y_test.reshape(-1, 1))  # Zurückskalieren

plt.figure(figsize=(10, 5))
plt.plot(Y_test_actual[:100], label="Echte Werte", marker='o')
plt.plot(Y_pred[:100], label="Vorhersagen", marker='x')
plt.legend()
plt.title("CNN Zeitreihenvorhersage")
plt.show()
