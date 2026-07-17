"""
Downloads Ken French's published factor returns (Dartmouth Data Library) and caches
them locally as parquet. This is deliberately the only network-touching module in
the project — H1/H2 depend on this data being exactly what French publishes, not a
reconstruction of it, so we never re-derive factors from raw prices here.

Requires internet access to mba.tuck.dartmouth.edu. NOTE: this will not run inside a
network-restricted sandbox (e.g. an agent sandbox with an allowlist) — run it locally
or in Colab. The parsing/stats code downstream does not depend on network access and
is unit-tested separately against synthetic data.
"""

from __future__ import annotations

import pathlib

import pandas as pd
import pandas_datareader.data as web

CACHE_DIR = pathlib.Path(__file__).resolve().parents[3] / "data_cache"

# Dataset names as registered with pandas_datareader's 'famafrench' source.
FIVE_FACTOR_DATASET = "F-F_Research_Data_5_Factors_2x3"
MOMENTUM_DATASET = "F-F_Momentum_Factor"


def _fetch_and_cache(dataset_name: str, start: str = "1960-01-01") -> pd.DataFrame:
    """Fetch one Ken French dataset and cache it as parquet. Returns the monthly table
    (index 0 of the pandas_datareader result, which is the raw monthly percentages)."""
    cache_path = CACHE_DIR / f"{dataset_name}.parquet"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    reader_result = web.DataReader(dataset_name, "famafrench", start=start)
    monthly = reader_result[0].copy()
    # French's files are in percent (e.g. 1.23 means 1.23%); convert to decimal returns.
    monthly = monthly / 100.0
    monthly.index = monthly.index.to_timestamp()
    monthly.to_parquet(cache_path)
    return monthly


def load_five_factors(start: str = "1960-01-01", refresh: bool = False) -> pd.DataFrame:
    """Mkt-RF, SMB, HML, RMW, CMA, RF — monthly, decimal returns."""
    cache_path = CACHE_DIR / f"{FIVE_FACTOR_DATASET}.parquet"
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)
    return _fetch_and_cache(FIVE_FACTOR_DATASET, start=start)


def load_momentum(start: str = "1960-01-01", refresh: bool = False) -> pd.DataFrame:
    """UMD (momentum) — monthly, decimal returns."""
    cache_path = CACHE_DIR / f"{MOMENTUM_DATASET}.parquet"
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)
    return _fetch_and_cache(MOMENTUM_DATASET, start=start)


def load_all_factors(start: str = "1960-01-01", refresh: bool = False) -> pd.DataFrame:
    """Joins the 5-factor set and momentum into one monthly DataFrame:
    Mkt-RF, SMB, HML, RMW, CMA, UMD, RF."""
    five = load_five_factors(start=start, refresh=refresh)
    mom = load_momentum(start=start, refresh=refresh)
    mom = mom.rename(columns={mom.columns[0]: "UMD"})
    combined = five.join(mom[["UMD"]], how="inner")
    return combined


if __name__ == "__main__":
    df = load_all_factors(refresh=True)
    print(df.tail())
    print(f"\nCached to: {CACHE_DIR}")
