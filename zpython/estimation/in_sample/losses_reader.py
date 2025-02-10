import pandas as pd


def read_loss(path):
    losses = pd.read_csv(path)
    losses.set_index("Epoch", inplace=True)
    return losses
