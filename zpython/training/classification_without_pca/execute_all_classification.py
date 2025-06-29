from concurrent.futures import ThreadPoolExecutor

from zpython.training.classification_without_pca.cnn.attention_cnn_regression_trainer import train_attention_cnn
from zpython.training.classification_without_pca.cnn.cnn_gru_regression_trainer import train_cnn_gru
from zpython.training.classification_without_pca.cnn.deep_cnn_regression_trainer import train_deep_cnn
from zpython.training.classification_without_pca.cnn.multi_scale_cnn_regression_trainer import train_multi_scale_cnn
from zpython.training.classification_without_pca.cnn.simple_cnn_regression_trainer import train
from zpython.training.classification_without_pca.lstm.bi_lstm_regression_trainer import train_bi_lstm
from zpython.training.classification_without_pca.lstm.dropout_lstm_regression_trainer import train_dropout_lstm
from zpython.training.classification_without_pca.lstm.encode_decode_lstm_regression_trainer import \
    train_encode_decose_lstm
from zpython.training.classification_without_pca.lstm.lstm_regression_trainer import train_lstm
from zpython.training.classification_without_pca.nn.nn_dropout_regression_trainer import train_dropout_nn
from zpython.training.classification_without_pca.nn.nn_residual_regression_trainer import train_residual_nn
from zpython.training.classification_without_pca.transformer.transformer_model import train_transformer

with ThreadPoolExecutor(max_workers=2) as pool:
    futures = []
    for fn in [
        train_attention_cnn, train_cnn_gru, train_deep_cnn, train_multi_scale_cnn, train, train_bi_lstm,
        train_dropout_lstm,
        train_encode_decose_lstm,
        train_lstm, train_dropout_nn,
        train_residual_nn, train_transformer]:
        f = pool.submit(fn)
        futures.append(f)

    for f in futures:
        f.result()
