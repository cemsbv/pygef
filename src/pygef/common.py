from dataclasses import dataclass
from typing import List

import polars as pl


@dataclass
class Location:
    srs_name: str
    x: float
    y: float


def assign_multiple_columns(
    df: pl.DataFrame, columns: List[str], partial_df: pl.DataFrame
) -> pl.DataFrame:
    return df.drop(columns).hstack(partial_df[columns])


def kpa_to_mpa(df: pl.DataFrame, columns: List[str]) -> pl.DataFrame:
    return assign_multiple_columns(df, columns, df[columns] * 10**-3)


def none_to_zero(df: pl.DataFrame) -> pl.DataFrame:
    return df.fill_null(0.0)


def nap_to_depth(zid: float, nap: float) -> float:
    return -(nap - zid)


def depth_to_nap(zid: float, depth: float) -> float:
    return zid - depth
