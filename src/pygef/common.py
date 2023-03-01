from __future__ import annotations

from dataclasses import dataclass
from typing import List

import polars as pl


@dataclass
class Location:
    """DataClass that holds the standardized location information"""

    srs_name: str
    x: float
    y: float


def assign_multiple_columns(
    df: pl.DataFrame, columns: List[str], partial_df: pl.DataFrame
) -> pl.DataFrame:
    """
    Helper function to assign multiple columns

    :param df: original Dataframe
    :param columns: updated column values
    :param partial_df: updated Dataframe
    :return: DataFrame
    """
    return df.drop(columns).hstack(partial_df[columns])


def kpa_to_mpa(df: pl.DataFrame, columns: List[str]) -> pl.DataFrame:
    """
    Transform from kPa to MPa.

    :param df: DataFrame
    :param columns: columns names
    :return: DataFrame
    """
    return assign_multiple_columns(df, columns, df[columns] * 10**-3)


def nap_to_depth(zid: float, ref: float) -> float:
    """
    Transform depth with respect to reference level to depth

    :param zid: surface reference level
    :param ref: z
    :return: depth
    """
    return -(ref - zid)


def depth_to_nap(zid: float, depth: float) -> float:
    """
    Transform depth to depth with respect to reference level

    :param zid: surface reference level
    :param depth: z
    :return: depth with respect to reference level
    """
    return zid - depth
