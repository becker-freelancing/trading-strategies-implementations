import os
import threading
from math import floor

import torch
from torch.utils.data import Dataset, DataLoader

from zpython.training.train_util import get_device
from zpython.util.market_regime import MarketRegime


class RegimeDataSet(Dataset):

    def __init__(self, regime: MarketRegime):
        self.regime = regime


class RegimeDataLoader(DataLoader):

    def __init__(self, data_set: RegimeDataSet, batch_size, shuffle):
        super().__init__(dataset=data_set, batch_size=batch_size, shuffle=shuffle)
        self.regime = data_set.regime

    def feature_shape(self):
        return self.dataset.feature_shape()

    def label_shape(self):
        return self.dataset.label_shape()


class LazyNumpyDataSet(RegimeDataSet):

    def __init__(self, path_provider, input_length, regime, limit):
        super().__init__(regime)
        self.path_provider = path_provider
        self.input_length = input_length
        self.current_cache_idx = -1
        self.device = get_device()
        self.x_cache = None
        self.y_cache = None
        self.next_x = None
        self.next_y = None
        self.next_file_idx = None
        self._feature_shape = None
        self._label_shape = None
        self.limit = limit

    def feature_shape(self):
        if self._feature_shape is None:
            i = self._get_max_file_idx()
            x, y = torch.load(self._file_path(i))
            last_len = x.shape[0]
            total_len = max((i - 1) * 15000 + last_len, last_len)
            self._feature_shape = (total_len, min(x.shape[1], self.input_length), x.shape[2])
        return self._feature_shape

    def _get_max_file_idx(self):
        i = 0
        while True:
            path = self._file_path(i)
            if not os.path.exists(path):
                i -= 1
                break
            i += 1
        return i

    def label_shape(self):
        if self._label_shape is None:
            x, y = torch.load(self._file_path(0))
            self._label_shape = (self.feature_shape()[0], y.shape[1])
        return self._label_shape

    def __len__(self):
        if self.limit is None:
            return self.feature_shape()[0]
        return min(self.feature_shape()[0], self.limit)

    def _file_path(self, idx):
        pass

    def _load_file_sync(self, file_idx):
        path = self._file_path(file_idx)
        x_cache, y_cache = torch.load(path)
        x_cache = torch.tensor(x_cache, dtype=torch.float32).to(self.device)
        y_cache = torch.tensor(y_cache, dtype=torch.float32).to(self.device)
        perm = torch.randperm(x_cache.size(0))
        x_cache = x_cache[perm]
        y_cache = y_cache[perm]
        return x_cache, y_cache, file_idx

    def _preload(self, preload_file_idx):
        def _async_preload():
            if not os.path.exists(self._file_path(preload_file_idx)):
                return
            self.next_x, self.next_y, self.next_file_idx = self._load_file_sync(preload_file_idx)

        load_thread = threading.Thread(target=_async_preload)
        load_thread.start()

    def _get_next_and_preload(self, needed_file_idx):
        if self.next_file_idx != needed_file_idx:
            self.x_cache, self.y_cache, self.current_cache_idx = self._load_file_sync(needed_file_idx)
        else:
            self.x_cache = self.next_x
            self.y_cache = self.next_y
            self.current_cache_idx = self.next_file_idx

        self.x_cache = self.x_cache
        self.y_cache = self.y_cache
        self._preload(needed_file_idx + 1)

    def _load(self, idx):
        file_idx = int(floor(idx / 15000))
        if self.current_cache_idx == file_idx:
            return
        self._get_next_and_preload(file_idx)

    def __getitem__(self, idx):
        self._load(idx)
        tensor_idx = int(idx % 15000)
        x = self.x_cache[tensor_idx][-self.input_length:, :]
        y = self.y_cache[tensor_idx]
        return x, y


class LazyTrainTensorDataSet(LazyNumpyDataSet):

    def __init__(self, path_provider, input_length, regime, limit):
        super().__init__(path_provider,
                         input_length,
                         regime,
                         limit)

    def _file_path(self, idx):
        path = self.path_provider(idx, regime=self.regime, train=True)
        return path


class LazyValidationTensorDataSet(LazyNumpyDataSet):

    def __init__(self, path_provider, input_length, regime, limit):
        super().__init__(path_provider,
                         input_length,
                         regime,
                         limit)

    def _file_path(self, idx):
        path = self.path_provider(idx, regime=self.regime, train=False)
        return path


class FeatureShuffleTensorDataSet(Dataset):

    def __init__(self, dataset, feature_shuffle_idx):
        super().__init__()
        self.dataset = dataset
        self.feature_shuffle_idx = feature_shuffle_idx

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, item):
        x, y = self.dataset[item]
        x[:, self.feature_shuffle_idx] = x[:, self.feature_shuffle_idx][torch.randperm(x.size(0))]
        return x, y
