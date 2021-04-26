import datetime
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

import core.artificial_signal_generators as sig_gen
import core.dataflow as cdataf
import helpers.dbg as dbg
import instrument_master.kibot as vkibot

_LOG = logging.getLogger(__name__)

_PANDAS_DATE_TYPE = Union[str, pd.Timestamp, datetime.datetime]


class ArmaGenerator(cdataf.DataSource):
    def __init__(
            self,
            nid: str,
            frequency: str,
            start_date: _PANDAS_DATE_TYPE,
            end_date: _PANDAS_DATE_TYPE,
            ar_coeffs: Optional[List[float]] = None,
            ma_coeffs: Optional[List[float]] = None,
            scale: Optional[float] = None,
            burnin: Optional[float] = None,
            seed: Optional[float] = None,
    ) -> None:
        super().__init__(nid)
        self._frequency = frequency
        self._start_date = start_date
        self._end_date = end_date
        self._ar_coeffs = ar_coeffs or [0]
        self._ma_coeffs = ma_coeffs or [0]
        self._scale = scale or 1
        self._burnin = burnin or 0
        self._seed = seed
        self._arma_process = sig_gen.ArmaProcess(
            ar_coeffs=self._ar_coeffs,
            ma_coeffs=self._ma_coeffs
        )

    def fit(self) -> Optional[Dict[str, pd.DataFrame]]:
        """
        :return: training set as df
        """
        self._lazy_load()
        return super().fit()

    def predict(self) -> Optional[Dict[str, pd.DataFrame]]:
        self._lazy_load()
        return super().predict()

    def _lazy_load(self) -> None:
        if self.df is not None:
            return
        rets = self._arma_process.generate_sample(
            date_range_kwargs={
                "start": self._start_date,
                "end": self._end_date,
                "freq": self._frequency,
            },
            scale=self._scale,
            burnin=self._burnin,
            seed=self._seed
        )
        # Cumulatively sum to generate a price series (implicitly assumes the
        # returns are log returns; at small enough scales and short enough
        # times this is practically interchangeable with percentage returns).
        prices = rets.cumsum()
        prices.name = "close"
        self.df = prices.to_frame()
        self.df = self.df.loc[self._start_date : self._end_date]
        # Use constant volume (for now).
        self.df["vol"] = 100


def DataSourceNodeFactory(
    nid: str, source_node_name: str, source_node_kwargs: Dict[str, Any]
) -> cdataf.DataSource:
    """
    Initialize the appropriate data source node.

    :param nid: node identifier
    :param source_node_name: short name for data source node type
    :param source_node_kwargs: kwargs for data source node
    :return: data source node of appropriate type instantiated with kwargs
    """
    dbg.dassert(source_node_name)
    if source_node_name == "disk":
        return cdataf.DiskDataSource(nid, **source_node_kwargs)
    elif source_node_name == "kibot":
        return KibotDataReader(nid, **source_node_kwargs)
    elif source_node_name == "kibot_multi_col":
        return KibotColumnReader(nid, **source_node_kwargs)
    elif source_node_name == "arma":
        return ArmaGenerator(nid, **source_node_kwargs)
    else:
        raise ValueError("Unsupported data source node %s", source_node_name)


class KibotDataReader(cdataf.DataSource):
    def __init__(
        self,
        nid: str,
        symbol: str,
        frequency: Union[str, vkibot.Frequency],
        contract_type: Union[str, vkibot.ContractType],
        start_date: Optional[_PANDAS_DATE_TYPE] = None,
        end_date: Optional[_PANDAS_DATE_TYPE] = None,
        nrows: Optional[int] = None,
    ) -> None:
        """
        Create data source node outputting single instrument data from Kibot.

        :param symbol, frequency, contract_type:
            define the Kibot data to load with the same meaning as in get_kibot_path
        :param start_date: data start date in ET, included
        :param end_date: data end date in Et, included
        :param nrows: same as Kibot read_data
        """
        super().__init__(nid)
        self._symbol = symbol
        self._frequency = (
            vkibot.Frequency(frequency)
            if isinstance(frequency, str)
            else frequency
        )
        self._contract_type = (
            vkibot.ContractType(contract_type)
            if isinstance(contract_type, str)
            else contract_type
        )
        self._start_date = KibotDataReader._process_timestamp(start_date)
        self._end_date = KibotDataReader._process_timestamp(end_date)
        self._nrows = nrows

    def fit(self) -> Optional[Dict[str, pd.DataFrame]]:
        """
        :return: training set as df
        """
        self._lazy_load()
        return super().fit()

    def predict(self) -> Optional[Dict[str, pd.DataFrame]]:
        self._lazy_load()
        return super().predict()

    def _lazy_load(self) -> None:
        if self.df is not None:
            return
        self.df = vkibot.KibotS3DataLoader().read_data(
            exchange="CME",
            asset_class=vkibot.AssetClass.Futures,
            frequency=self._frequency,
            contract_type=self._contract_type,
            symbol=self._symbol,
            nrows=self._nrows,
        )
        self.df = self.df.loc[self._start_date : self._end_date]

    @staticmethod
    def _process_timestamp(
        timestamp: Optional[_PANDAS_DATE_TYPE],
    ) -> Optional[pd.Timestamp]:
        if timestamp is pd.NaT:
            timestamp = None
        if timestamp is not None:
            timestamp = pd.Timestamp(timestamp)
            dbg.dassert_is(timestamp.tz, None)
        return timestamp


class KibotColumnReader(cdataf.DataSource):
    def __init__(
        self,
        nid: str,
        symbols: List[str],
        frequency: Union[str, vkibot.Frequency],
        contract_type: Union[str, vkibot.ContractType],
        col: str,
        start_date: Optional[_PANDAS_DATE_TYPE] = None,
        end_date: Optional[_PANDAS_DATE_TYPE] = None,
        nrows: Optional[int] = None,
    ) -> None:
        """
        Same interface as KibotDataReader but with multiple symbols.
        """
        super().__init__(nid)
        self._symbols = symbols
        self._frequency = (
            vkibot.Frequency(frequency)
            if isinstance(frequency, str)
            else frequency
        )
        self._contract_type = (
            vkibot.ContractType(contract_type)
            if isinstance(contract_type, str)
            else contract_type
        )
        self._col = col
        self._start_date = start_date
        self._end_date = end_date
        self._nrows = nrows

    def fit(self) -> Optional[Dict[str, pd.DataFrame]]:
        self._lazy_load()
        return super().fit()

    def predict(self) -> Optional[Dict[str, pd.DataFrame]]:
        self._lazy_load()
        return super().predict()

    def _lazy_load(self) -> None:
        if self.df is not None:
            return
        dict_df = {}
        for s in self._symbols:
            data = vkibot.KibotS3DataLoader().read_data(
                exchange="CME",
                asset_class=vkibot.AssetClass.Futures,
                frequency=self._frequency,
                contract_type=self._contract_type,
                symbol=s,
                nrows=self._nrows,
            )[self._col]
            data = data.loc[self._start_date : self._end_date]
            dict_df[s] = data
        self.df = pd.DataFrame.from_dict(dict_df)