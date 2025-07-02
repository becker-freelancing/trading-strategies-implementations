# transformer_pytorch.py
# 1:1 Konvertierung des TensorFlow-Modells in PyTorch

import torch
import torch.nn as nn
import torch.nn.functional as F


class InputSplit(nn.Module):
    def __init__(self, num_obs_in_history, d_obs, d_obs_logical_segments):
        super().__init__()
        self.num_obs_in_history = num_obs_in_history
        self.d_obs = d_obs
        self.d_obs_logical_segments = d_obs_logical_segments

    def forward(self, obs_history_flat):
        b_size = obs_history_flat.size(0)
        obs_history = obs_history_flat.view(b_size, self.num_obs_in_history, self.d_obs)
        return torch.split(obs_history, self.d_obs_logical_segments, dim=-1)


class TimeEncoding(nn.Module):
    def __init__(self, num_obs_in_history, d_time_enc):
        super().__init__()
        self.dense_time_encoding = nn.Linear(1 + 2, d_time_enc)  # 1 = linspace, 2 = obs_time
        self.layer_norm = nn.LayerNorm(d_time_enc)
        self.num_obs_in_history = num_obs_in_history

    def forward(self, obs_history_time):
        b_size = obs_history_time.size(0)
        device = obs_history_time.device
        time_abs_scaled = torch.linspace(0., 1., self.num_obs_in_history, device=device).view(1, -1, 1).repeat(b_size,
                                                                                                               1, 1)
        time_concat = torch.cat([time_abs_scaled, obs_history_time], dim=-1)
        out = self.dense_time_encoding(time_concat)
        return self.layer_norm(out)


class AccountEncoding(nn.Module):
    def __init__(self, d_account_enc):
        super().__init__()
        self.linear = nn.Linear(2, d_account_enc)
        self.norm = nn.LayerNorm(d_account_enc)

    def forward(self, obs_history_account):
        return self.norm(self.linear(obs_history_account))


# Encoded die "internen" Daten, was in diesem Fall Uhrzeit und der Zustand des Accounts ist
class ObsEncodingInternal(nn.Module):
    def __init__(self, num_obs_in_history, d_time_enc, d_account_enc):
        super().__init__()
        self.time_enc = TimeEncoding(num_obs_in_history, d_time_enc)
        self.account_enc = AccountEncoding(d_account_enc)

    def forward(self, obs_time, obs_account):
        enc_time = self.time_enc(obs_time)
        enc_account = self.account_enc(obs_account)
        return torch.cat([enc_time, enc_account], dim=-1)


# Encoded zwei Paare ineinander
class CandlesticksEncoding(nn.Module):
    def __init__(self, d_pair_1, d_pair_2, d_enc):
        super().__init__()
        self.linear_pair_1 = nn.Linear(d_pair_1, d_enc * 4 // 3)
        self.linear_pair_2 = nn.Linear(d_pair_2, d_enc * 4 // 3)
        self.linear_final = nn.Linear(d_enc * 8 // 3, d_enc)
        self.norm = nn.LayerNorm(d_enc)

    def forward(self, pair_1, pair_2):
        pair_1_enc = F.gelu(self.linear_pair_1(pair_1))
        pair_2_enc = F.gelu(self.linear_pair_2(pair_2))
        concat = torch.cat([pair_1_enc, pair_2_enc], dim=-1)
        return self.norm(self.linear_final(concat))


# Codiert die "externen" Daten, was in diesem Fall die Preisdaten sind
class ObsEncodingExternal(nn.Module):
    def __init__(self, d_candlesticks_enc=96):
        super().__init__()
        self.eth_candle_encoder = CandlesticksEncoding(d_pair_1=57, d_pair_2=55,
                                                       d_enc=d_candlesticks_enc)  # Für ETH M1 und ETH M15
        self.btc_candle_encoder = CandlesticksEncoding(d_pair_1=56, d_pair_2=55,
                                                       d_enc=d_candlesticks_enc)  # Für BTC M1 und BTC M15

    def forward(self, eth_m1, btc_m1, eth_15, btc_15):
        eth_enc = self.eth_candle_encoder(eth_m1, eth_15)
        btc_enc = self.btc_candle_encoder(btc_m1, btc_15)

        return torch.cat([eth_enc, btc_enc], dim=-1)


class AttentionBlock(nn.Module):
    def __init__(self, d_model, num_heads, dropout=0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=num_heads, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_model * 3 // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model * 3 // 2, d_model),
            nn.Dropout(dropout)
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x):
        attn_output, _ = self.attn(x, x, x)
        x = self.norm1(x + attn_output)
        x = self.norm2(x + self.ff(x))
        return x


class TransformerModel(nn.Module):
    def __init__(self, num_obs, d_obs, d_obs_logical_segments):
        super().__init__()
        self.num_obs = num_obs
        self.d_obs = d_obs
        self.d_obs_logical_segments = d_obs_logical_segments
        self.input_split = InputSplit(self.num_obs, self.d_obs, self.d_obs_logical_segments)

        self.internal_enc = ObsEncodingInternal(self.num_obs, 32, 32)
        self.external_enc = ObsEncodingExternal()
        self.concat_dim = 64 + 192

        self.transformer = nn.Sequential(
            *[AttentionBlock(d_model=self.concat_dim, num_heads=4) for _ in range(3)]
        )

        self.pool = lambda x: x[:, -1, :]
        self.head_policy = nn.Linear(self.concat_dim * 2, 4)
        self.head_value = nn.Linear(self.concat_dim * 2, 1)

    def forward(self, x):
        splits = self.input_split(x)
        int_enc = self.internal_enc(splits[0], splits[1])
        ext_enc = self.external_enc(*splits[2:])

        stem_enc = torch.cat([int_enc, ext_enc], dim=-1)
        trans_out = self.transformer(stem_enc)

        pooled = torch.cat([self.pool(stem_enc), self.pool(trans_out)], dim=-1)
        logits = self.head_policy(pooled)
        value = self.head_value(pooled)
        return logits, value.squeeze(-1)


if __name__ == '__main__':
    model = TransformerModel()
    dummy_input = torch.rand(15, 168 * 183)
    logits, value = model(dummy_input)
    print(logits.shape, value.shape)
