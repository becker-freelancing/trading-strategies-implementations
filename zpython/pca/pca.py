import matplotlib

matplotlib.use("TkAgg")
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from zpython.util.indicator_creator import create_indicators
from sklearn.preprocessing import MinMaxScaler


def pca():
    df = create_indicators()
    df = df.dropna()
    X = df.to_numpy()
    X = MinMaxScaler().fit_transform(X)
    pca = PCA()
    pca.fit(X)

    explained_variance = pca.explained_variance_ratio_
    variance = pca.explained_variance_
    names = df.columns.values

    pc1_loadings = pca.components_[0]  # Erste Komponente
    abs_loadings = np.abs(pc1_loadings)  # Absolutwerte, da negative Beiträge auch groß sein können

    # Features sortieren nach Beitrag zu PC1
    sorted_indices = np.argsort(abs_loadings)[::-1]  # absteigend sortieren
    sorted_features = [names[i] for i in sorted_indices]

    # Ausgabe
    for feature, loading in zip(sorted_features, abs_loadings[sorted_indices]):
        print(f"{feature}: {loading:.4f}")

    # Plot erstellen
    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(explained_variance), marker='o', linestyle='--', label='Cumulative explained variance')
    plt.bar(range(len(explained_variance)), explained_variance, alpha=0.6, label='Individual explained Variance')
    plt.xlabel('Principal Component')
    plt.ylabel('Explained Variance Ratio')
    plt.title('Explained Variance Plot')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


pca()
