from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, overload

import polars as pl
from numpy.typing import NDArray


def convert_coordinate_system_to_gml(value: str) -> str:
    """function that maps the coordinate system code to standardized location information"""

    if value == "31000":
        return "urn:ogc:def:crs:EPSG::28992"
    elif value == "31001":
        return "urn:ogc:def:crs:EPSG::32603"
    elif value == "31002":
        return "urn:ogc:def:crs:EPSG::32609"
    elif value == "32000":
        return "urn:ogc:def:crs:EPSG::31370"
    elif value == "49000":
        return "urn:ogc:def:crs:EPSG::31467"
    # 00000 = own coordinate system see #MEASUREMENTTEXT = 7
    # 00001 = Geographic Coordinate System
    # 01000 = SPCS
    return "urn:ogc:def:crs:EPSG::404000"


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
    OCS = "00000"  # Own Coordinate System
    GCS = "00001"  # Geographic Coordinate System
    SPCS = "01000"  # SPCS


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


@overload
def offset_to_depth(ref: float, offset: float) -> float: ...


@overload
def offset_to_depth(ref: NDArray, offset: float) -> NDArray: ...


def offset_to_depth(
    ref: float | None | NDArray, offset: float | None
) -> float | None | NDArray:
    """
    Transform depth with respect to reference level to depth

    :param offset: surface reference level
    :param ref: z
    :return: depth
    """
    if offset is None or ref is None:
        return None
    return -(ref - offset)


@overload
def depth_to_offset(depth: float | None, offset: float | None) -> float | None: ...


@overload
def depth_to_offset(depth: NDArray, offset: float) -> NDArray: ...


def depth_to_offset(
    depth: float | None | NDArray, offset: float | None
) -> float | None | NDArray:
    """
    Transform depth to depth with respect to reference level

    :param offset: surface reference level
    :param depth: z
    :return: depth with respect to reference level
    """
    if offset is None or depth is None:
        return None
    return offset - depth
