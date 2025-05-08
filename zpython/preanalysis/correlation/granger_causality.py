from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

import numpy as np
import pandas as pd
import tqdm
from statsmodels.tsa.api import VAR

from zpython.indicators.indicator_creator import create_multiple_indicators
from zpython.util.data_split import analysis_data, valid_time_frames
from zpython.util.path_util import from_relative_path


def calculate(time_frame):
    data = create_multiple_indicators(analysis_data, time_frame=time_frame)

    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    data.reset_index(inplace=True)
    data = data.drop(["closeTime"], axis=1)

    result = pd.DataFrame(data={},
                          columns=['causing', 'caused', 'caused_lag', 'test', 'test_statistic', 'crit_value', 'pvalue',
                                   'signif', 'method', 'conclusion', 'title', 'h0', 'conclusion_str', 'signif_str',
                                   'signif_lags'])

    for column in tqdm.tqdm(data.columns, "Granger Causality"):
        if column == "logReturn_closeBid_1min" or "Greater" in column or "Less" in column:
            continue  # Skip not calculatable columns
        with ThreadPoolExecutor(max_workers=1) as pool:
            fixed = partial(fit_model, column, data)
            futures = [pool.submit(fixed, target_lag) for target_lag in list(range(30))]
            for f in futures:
                result = pd.concat([result, f.result()])
        # result = fit_model(column, data, result)

        result.to_csv(from_relative_path(f"analysis-bybit/granger/granger_test_{time_frame}.csv"), index=False)


def fit_model(column, data, target_lag):
    # Create VAR Model
    df = data[["logReturn_closeBid_1min", column]].copy()
    df["logReturn_closeBid_1min"] = df["logReturn_closeBid_1min"].shift(-target_lag)
    df = df.dropna()
    fit = VAR(df).fit(maxlags=100)
    res = fit.test_causality(['logReturn_closeBid_1min'], [column],
                             kind="f")  # H0 abgelehnt -> Kausale wirkung vorhanden
    m = fit.summary().model
    # Get Significant Lags
    pvalues = pd.DataFrame(m.pvalues, columns=m.names, index=m.exog_names)["logReturn_closeBid_1min"]
    significant_lags = []
    for idx in pvalues.index:
        if column in idx:
            pval = pvalues[idx]
            name = idx.split(".")[0][1:]
            significant_lags.append([name, pval])
    # Get general information
    res = res.__dict__
    res.pop("df")
    # Save
    res["signif_lags"] = significant_lags
    res["caused_lag"] = target_lag
    res = pd.DataFrame(data=[res])
    return res


for i in valid_time_frames():
    calculate(i)
