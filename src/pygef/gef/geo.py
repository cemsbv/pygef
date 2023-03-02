from __future__ import annotations

import polars as pl


def delta_depth(df: pl.DataFrame) -> pl.DataFrame:
    """
    Take pre-excavated depth into account.

    This function corrects the depth column and adds a column (np.diff(depth))

    :param df: (DataFrame) with depth column
    :return: (DataFrame) [depth, delta_depth]
    """
    return df.with_columns(
        pl.col("depth")
        .diff(n=1, null_behavior="ignore")
        .fill_null(strategy="zero")
        .alias("delta_depth")
    )


def soil_pressure(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (pl.col("gamma") * pl.col("delta_depth")).cumsum().alias("soil_pressure")
    )


def water_pressure(df: pl.DataFrame, water_level: float) -> pl.DataFrame:
    return df.with_columns(
        ((pl.col("depth") - water_level) * 9.81).clip_min(0.0).alias("water_pressure")
    )


def effective_soil_pressure(df: pl.DataFrame):
    return df.with_columns(
        (pl.col("soil_pressure") - pl.col("water_pressure")).alias(
            "effective_soil_pressure"
        )
    )


def qt(df, area_quotient_cone_tip=None):
    if "u2" in df.columns and area_quotient_cone_tip is not None:
        return df.with_columns(
            (pl.col("qc") + pl.col("u2") * (1.0 - area_quotient_cone_tip)).alias("qt")
        )
    else:
        return df.with_columns(pl.col("qc").alias("qt"))


def normalized_cone_resistance(df: pl.DataFrame) -> pl.DataFrame:
    name = "normalized_cone_resistance"
    return df.with_columns(
        ((pl.col("qt") - pl.col("soil_pressure")) / pl.col("effective_soil_pressure"))
        .clip_min(0.0)
        .alias(name)
    )


def normalized_friction_ratio(df: pl.DataFrame) -> pl.DataFrame:
    if "fs" in df.columns:
        fs = pl.col("fs")
    else:
        fs = pl.col("friction_number") * pl.col("qc") / 100.0

    name = "normalized_friction_ratio"
    return df.with_columns(
        ((fs / (pl.col("qt") - pl.col("soil_pressure"))) * 100)
        .clip_min(0.1)
        .alias(name)
    )
