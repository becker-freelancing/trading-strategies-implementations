# https://medium.com/lseg-developer-community/market-regime-detection-using-statistical-and-ml-based-approaches-b4c27e7efc8b

import warnings

import numpy as np
import plotly.graph_objects as go
from hmmlearn.hmm import GaussianHMM
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import GaussianMixture

from zpython.util import analysis_data
from zpython.util import split_on_gaps

warnings.filterwarnings('ignore')

print("Read data")
df = analysis_data()
print("Create indicators")

df = split_on_gaps(df, 1)[0]
df = df[["closeTime", "closeBid"]]
df.set_index("closeTime", inplace=True)


def prepare_data_for_model_input(prices, ma):
    '''
        Input:
        prices (df) - Dataframe of close prices
        ma (int) - legth of the moveing average

        Output:
        prices(df) - An enhanced prices dataframe, with moving averages and log return columns
        prices_array(nd.array) - an array of log returns
    '''

    intrument = "ETHUSDT"
    prices[f'{intrument}_ma'] = prices.rolling(ma).mean()
    prices[f'{intrument}_log_return'] = np.log(prices[f'{intrument}_ma'] / prices[f'{intrument}_ma'].shift(1)).dropna()

    prices.dropna(inplace=True)
    prices_array = np.array([[q] for q in prices[f'{intrument}_log_return'].values])

    return prices, prices_array


class RegimeDetection:

    def get_regimes_hmm(self, input_data, params):
        hmm_model = self.initialise_model(GaussianHMM(), params).fit(input_data)
        return hmm_model

    def get_regimes_clustering(self, params):
        clustering = self.initialise_model(AgglomerativeClustering(), params)
        return clustering

    def get_regimes_gmm(self, input_data, params):
        gmm = self.initialise_model(GaussianMixture(), params).fit(input_data)
        return gmm

    def initialise_model(self, model, params):
        for parameter, value in params.items():
            setattr(model, parameter, value)
        return model


def plot_hidden_states(hidden_states, prices_df):
    '''
    Input:
    hidden_states(numpy.ndarray) - array of predicted hidden states
    prices_df(df) - dataframe of close prices

    Output:
    Graph showing hidden states and prices

    '''

    colors = ['blue', 'green']
    n_components = len(np.unique(hidden_states))
    fig = go.Figure()

    for i in range(n_components):
        mask = hidden_states == i
        print('Number of observations for State ', i, ":", len(prices_df.index[mask]))

        fig.add_trace(go.Scatter(x=prices_df.index[mask], y=prices_df["closeBid"][mask],
                                 mode='markers', name='Hidden State ' + str(i), marker=dict(size=4, color=colors[i])))

    fig.update_layout(height=400, width=900, legend=dict(
        yanchor="top", y=0.99, xanchor="left", x=0.01), margin=dict(l=20, r=20, t=20, b=20)).show()


trading_instrument = "closeBid"
prices, prices_array = prepare_data_for_model_input(df, 7)
regime_detection = RegimeDetection()
####
params = {'n_clusters': 2, 'linkage': 'complete', 'affinity': 'manhattan', 'metric': 'manhattan', 'random_state': 100}
clustering = regime_detection.get_regimes_clustering(params)
clustering_states = clustering.fit_predict(prices_array)

plot_hidden_states(np.array(clustering_states), prices[[f'{trading_instrument}']])

####
params = {'n_components': 2, 'covariance_type': 'full', 'max_iter': 100000, 'n_init': 30, 'init_params': 'kmeans',
          'random_state': 100}

gmm_model = regime_detection.get_regimes_gmm(prices_array, params)
gmm_states = gmm_model.predict(prices_array)
plot_hidden_states(np.array(gmm_states), prices[[f'{trading_instrument}']])

####
params = {'n_components': 2, 'covariance_type': "full", 'random_state': 100}

hmm_model = regime_detection.get_regimes_hmm(prices_array, params)
hmm_states = hmm_model.predict(prices_array)
plot_hidden_states(np.array(hmm_states), prices[[f'{trading_instrument}']])
