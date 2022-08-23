from __future__ import annotations

import numpy as np
import polars as pl
import pygef.utils as utils
from pygef import geo
import pygef.expressions as exprs


def n_exponent(df: pl.DataFrame, p_a: float) -> pl.DataFrame:
    return df.with_column(
        (
            0.381 * pl.col("type_index_n")
            + 0.05 * (pl.col("effective_soil_pressure") / p_a)
            - 0.15
        )
        .clip(0.0, 1.0)
        .alias("n")
    )


def normalized_cone_resistance_n(df: pl.DataFrame, p_a: float) -> pl.DataFrame:
    return df.with_column(
        (
            (pl.col("qt") - pl.col("soil_pressure"))
            / p_a
            * (p_a / pl.col("effective_soil_pressure") ** pl.col("n"))
        )
        .clip(0.0, 1e8)
        .alias("normalized_cone_resistance")
    )


def type_index(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_column(
        (
            (
                (3.47 - pl.col("normalized_cone_resistance").log10()) ** 2.0
                + (pl.col("normalized_friction_ratio").log10() + 1.22) ** 2.0
            ).sqrt()
        ).alias("type_index")
    )


def ic_to_soil_type(ti: pl.Expr = pl.col("type_index")):
    """
    Assign the soil type to the corresponding Ic.
    """

    return (
        pl.when(ti > 3.6)
        .then("Peat")
        .when((ti <= 3.6) & (ti > 2.95))
        .then("Clays - silty clay to clay")
        .when((ti <= 2.95) & (ti > 2.6))
        .then("Silt mixtures - clayey silt to silty clay")
        .when((ti <= 2.6) & (ti > 2.05))
        .then("Sand mixtures - silty sand to sandy silt")
        .when((ti <= 2.05) & (ti > 1.31))
        .then("Sands - clean sand to silty sand")
        .when(ti <= 1.31)
        .then("Gravelly sand to dense sand")
        .otherwise(None)
        .alias("soil_type")
    )


def none_to_zero(df):
    return df.fill_null(0)


def iterate_robertson(
    original_df,
    water_level,
    new=True,
    area_quotient_cone_tip=None,
    p_a=0.1,
):
    """
    Iteration function for Robertson classifier.

    :param original_df: (DataFrame)
    :param water_level: (int) Water level with respect to ground level.
    :param new: (bool) True to use the new classification, False otherwise. Default: True
    :param area_quotient_cone_tip: (float)
    :param pre_excavated_depth: (float)
    :param p_a: (float) Atmospheric pressure. Default: 0.1 MPa.
    :return: (DataFrame)
    """
    n = pl.Series("n", np.ones(original_df.shape[0]))
    gamma = (n * 18).rename("gamma")
    gamma_predict = gamma
    type_index_n = n.rename("type_index_n")

    c = 0
    while True:
        c += 1
        if new:
            df = original_df.with_columns([n, type_index_n, gamma])
            f = new_robertson

            def condition(x):
                return np.all(
                    x["gamma_predict"].series_equal(gamma)
                    and np.all(x["n"].series_equal(n))
                )

        else:
            df = original_df.with_columns(gamma, gamma_predict)
            f = old_robertson

            def condition(x):
                return np.all(x["gamma_predict"].series_equal(gamma))

        df = f(
            df,
            water_level,
            area_quotient_cone_tip=area_quotient_cone_tip,
            p_a=p_a,
        )

        # df["gamma_predict"] = np.nan_to_num(df["gamma_predict"])
        if condition(df):
            break
        elif c == 4:
            break
        else:
            gamma_predict = df["gamma_predict"]
            if new:
                n = df["n"]

    return df.with_column(ic_to_soil_type())


def old_robertson(df, water_level, area_quotient_cone_tip=None):
    """
    Old (1990) implementation of Robertson.

    :param df: (DataFrame)
    :param water_level: (float)
    :param area_quotient_cone_tip: (float)
    :param pre_excavated_depth: (float)
    :return: (DataFrame) Classified dataframe.
    """
    df = (
        df.pipe(geo.delta_depth)
        .pipe(geo.soil_pressure)
        .pipe(geo.qt, area_quotient_cone_tip)
        .pipe(geo.water_pressure, water_level)
        .pipe(geo.effective_soil_pressure)
        .pipe(
            utils.kpa_to_mpa,
            ["soil_pressure", "effective_soil_pressure", "water_pressure"],
        )
        .pipe(geo.normalized_cone_resistance)
        .pipe(geo.normalized_friction_ratio)
        .pipe(utils.none_to_zero)
        .pipe(type_index)
        .with_columns(
            [
                exprs.ic_to_gamma(water_level),
                pl.when(pl.col("gamma_predict").is_nan())
                .then(0.0)
                .otherwise(pl.col("gamma_predict"))
                .keep_name(),
            ]
        )
    )

    return df


def new_robertson(
    df: pl.DataFrame,
    water_level: float,
    area_quotient_cone_tip: float | None = None,
    p_a: float = 0.1,
):
    """
    New (2016) implementation of Robertson.

    :param df: (DataFrame)
    :param water_level: (float)
    :param area_quotient_cone_tip: (float)
    :param pre_excavated_depth: (float)
    :param p_a: (float)
    :return: (DataFrame) Classified dataframe.
    """

    df = (
        df.pipe(geo.delta_depth)
        .pipe(geo.soil_pressure)
        .pipe(geo.qt, area_quotient_cone_tip)
        .pipe(geo.water_pressure, water_level)
        .pipe(geo.effective_soil_pressure)
        .pipe(
            utils.kpa_to_mpa,
            ["soil_pressure", "effective_soil_pressure", "water_pressure"],
        )
        .pipe(n_exponent, p_a)
        .pipe(normalized_cone_resistance_n, p_a)
        .pipe(geo.normalized_friction_ratio)
        .pipe(utils.none_to_zero)
        .pipe(type_index)
        .with_column(
            # gamma_predict
            exprs.ic_to_gamma(water_level),
        )
        .with_columns(
            [
                pl.when(pl.col("gamma_predict").is_nan())
                .then(0.0)
                .otherwise(pl.col("gamma_predict"))
                .keep_name(),
            ]
        )
    )
    return df
