import logging

import pandas as pd
import sklearn.decomposition as sdecom

import core.artificial_signal_generators as casgen
import core.config_builders as ccbuild
import helpers.unit_test as hut
from core.dataflow.nodes.unsupervised_sklearn_models import (
    Residualizer,
    UnsupervisedSkLearnModel,
)

_LOG = logging.getLogger(__name__)


class TestUnsupervisedSkLearnModel(hut.TestCase):
    def test1(self) -> None:
        """
        Test `fit()` call.
        """
        # Load test data.
        data = self._get_data()
        # Create sklearn config and modeling node.
        config = ccbuild.get_config_from_nested_dict(
            {
                "x_vars": [0, 1, 2, 3],
                "model_func": sdecom.PCA,
                "model_kwargs": {"n_components": 2},
            }
        )
        node = UnsupervisedSkLearnModel("sklearn", **config.to_dict())
        # Fit model.
        df_out = node.fit(data)["df_out"]
        df_str = hut.convert_df_to_string(df_out.round(3), index=True)
        self.check_string(df_str)

    def test2(self) -> None:
        """
        Test `predict()` after `fit()`.
        """
        data = self._get_data()
        config = ccbuild.get_config_from_nested_dict(
            {
                "x_vars": [0, 1, 2, 3],
                "model_func": sdecom.PCA,
                "model_kwargs": {"n_components": 2},
            }
        )
        node = UnsupervisedSkLearnModel("sklearn", **config.to_dict())
        node.fit(data.loc["2000-01-03":"2000-01-31"])
        # Predict.
        df_out = node.predict(data.loc["2000-02-01":"2000-02-25"])["df_out"]
        df_str = hut.convert_df_to_string(df_out.round(3), index=True)
        self.check_string(df_str)

    def _get_data(self) -> pd.DataFrame:
        """
        Generate multivariate normal returns.
        """
        mn_process = casgen.MultivariateNormalProcess()
        mn_process.set_cov_from_inv_wishart_draw(dim=4, seed=0)
        realization = mn_process.generate_sample(
            {"start": "2000-01-01", "periods": 40, "freq": "B"}, seed=0
        )
        return realization


class TestResidualizer(hut.TestCase):
    def test1(self) -> None:
        """
        Test `fit()` call.
        """
        # Load test data.
        data = self._get_data()
        # Load sklearn config and create modeling node.
        config = ccbuild.get_config_from_nested_dict(
            {
                "x_vars": [0, 1, 2, 3],
                "model_func": sdecom.PCA,
                "model_kwargs": {"n_components": 2},
            }
        )
        node = Residualizer("sklearn", **config.to_dict())
        #
        df_out = node.fit(data)["df_out"]
        df_str = hut.convert_df_to_string(df_out.round(3), index=True)
        self.check_string(df_str)

    def test2(self) -> None:
        """
        Test `predict()` after `fit()`.
        """
        # Load test data.
        data = self._get_data()
        # Load sklearn config and create modeling node.
        config = ccbuild.get_config_from_nested_dict(
            {
                "x_vars": [0, 1, 2, 3],
                "model_func": sdecom.PCA,
                "model_kwargs": {"n_components": 2},
            }
        )
        node = Residualizer("sklearn", **config.to_dict())
        node.fit(data.loc["2000-01-03":"2000-01-31"])
        # Predict.
        df_out = node.predict(data.loc["2000-02-01":"2000-02-25"])["df_out"]
        df_str = hut.convert_df_to_string(df_out.round(3), index=True)
        self.check_string(df_str)

    def _get_data(self) -> pd.DataFrame:
        """
        Generate multivariate normal returns.
        """
        mn_process = casgen.MultivariateNormalProcess()
        mn_process.set_cov_from_inv_wishart_draw(dim=4, seed=0)
        realization = mn_process.generate_sample(
            {"start": "2000-01-01", "periods": 40, "freq": "B"}, seed=0
        )
        return realization