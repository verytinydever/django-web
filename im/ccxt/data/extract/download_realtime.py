#!/usr/bin/env python
"""
Script to download data from CCXT in real-time.
"""
import argparse
import logging
import os
import time

import pandas as pd

import helpers.dbg as dbg
import helpers.io_ as hio
import helpers.parser as hparse
import im.ccxt.data.extract.exchange_class as deecla

_LOG = logging.getLogger(__name__)


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--dst_dir",
        action="store",
        required=True,
        type=str,
        help="Folder to download files to",
    )
    parser.add_argument(
        "--api_keys",
        action="store",
        type=str,
        default=deecla.API_KEYS_PATH,
        help="Path to JSON file that contains API keys for exchange access",
    )
    parser.add_argument(
        "--exchange_ids",
        action="store",
        required=True,
        type=str,
        help="CCXT names of exchanges to download data for, separated by spaces, e.g. 'binance gemini',"
        "'all' for each exchange (currently includes Binance and Kucoin by default)",
    )
    parser.add_argument(
        "--currency_pairs",
        action="store",
        required=True,
        type=str,
        help="Name of the currency pair to download data for, separated by spaces, e.g. 'BTC/USD ETH/USD',"
        " 'all' for each currency pair in exchange",
    )
    parser.add_argument(
        "--incremental",
        action="store_true"
    )
    parser = hparse.add_verbosity_arg(parser)
    return parser  # type: ignore[no-any-return]


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    dbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    # Create the directory.
    hio.create_dir(args.dst_dir, incremental=args.incremental)
    start_datetime = pd.Timestamp(args.start_datetime)
    # If end_date is not provided, get current time.
    if not args.end_datetime:
        end_datetime = pd.Timestamp.now()
    else:
        end_datetime = pd.Timestamp(args.end_datetime)
    if args.exchange_ids == "all":
        # Iterate over all available exchanges.
        exchange_ids = ["binance", "kucoin"]
    else:
        # Get a single exchange.
        exchange_ids = args.exchange_ids.split()
    _LOG.info("Getting data for exchanges %s", ", ".join(exchange_ids))
    while True:
        for exchange_id in exchange_ids:
            # Initialize the exchange class.
            exchange = deecla.CcxtExchange(exchange_id, api_keys_path=args.api_keys)
            if args.currency_pairs == "all":
                # Iterate over all currencies available for exchange.
                present_pairs = exchange.currency_pairs
            else:
                # Iterate over provided currency.
                currency_pairs = args.currency_pairs.split()
                # Leave only currencies present in exchange.
                present_pairs = [
                    curr for curr in currency_pairs if curr in exchange.currency_pairs
                ]
            for pair in present_pairs:
                # Download OHLCV data.
                pair_data = exchange.download_ohlcv_data(
                    start_datetime, end_datetime, curr_symbol=pair, step=5
                )
                # Set up sleep time between iterations.
                time.sleep(60)

if __name__ == "__main__":
    _main(_parse())