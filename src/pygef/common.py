from __future__ import annotations

from enum import Enum
from typing import List

import polars as pl
from pydantic.dataclasses import dataclass


@dataclass
class Location:
    """DataClass that holds the standardized location information"""

    srs_name: str
    x: float
    y: float


class VerticalDatumClass(Enum):
    """DataClass that holds the standardized vertical reference information"""

    Unknown = "-1"
    NAP = "31000"  # Normaal Amsterdams Peil
    BOP = "32000"  # Ostend Level (GEF)
    MSL = "49000"  # Mean Sea Level
    LAT = "00001"  # Lowest Astronomical Tide
    TAW = "32001"  # (GEF)


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


def offset_to_depth(ref: float | None, offset: float | None) -> float | None:
    """
    Transform depth with respect to reference level to depth

    :param offset: surface reference level
    :param ref: z
    :return: depth
    """
    if offset is None or ref is None:
        return None
    return -(ref - offset)


def depth_to_offset(depth: float | None, offset: float | None) -> float | None:
    """
    Transform depth to depth with respect to reference level

    :param offset: surface reference level
    :param depth: z
    :return: depth with respect to reference level
    """
    if offset is None or depth is None:
        return None
    return offset - depth
