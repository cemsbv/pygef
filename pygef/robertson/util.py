import numpy as np
import polars as pl
import pygef.utils as utils
from pygef import geo
import pygef.expressions as exprs


def n_exponent(df, p_a):
    df["n"] = (
        0.381 * df["type_index_n"] + 0.05 * (df["effective_soil_pressure"] / p_a) - 0.15
    )

    # Set the maximum for N to 1.0
    df[df["n"] > 1.0, "n"] = 1.0

    return df


def normalized_cone_resistance_n(df, p_a):
    # We have to convert the series to numpy because they don't support pow
    df["normalized_cone_resistance"] = (
        (df["qt"] - df["soil_pressure"])
        / p_a
        * (p_a / df["effective_soil_pressure"]) ** df["n"]
    )
    df[df["normalized_cone_resistance"] < 0.0, "normalized_cone_resistance"] = 1.0

    return df


def type_index(df):
    # We have to convert the series to numpy because they don't support pow
    df["type_index"] = (
        (3.47 - np.log10(df["normalized_cone_resistance"])) ** 2.0
        + (np.log10(df["normalized_friction_ratio"]) + 1.22) ** 2.0
    ) ** 0.5

    return df


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
        .otherwise("")
        .alias("soil_type")
    )


def none_to_zero(df):
    return df.fill_null(0)


def iterate_robertson(
    original_df,
    water_level,
    new=True,
    area_quotient_cone_tip=None,
    pre_excavated_depth=None,
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
    gamma = np.ones(original_df.shape[0]) * 18.0
    n = np.ones(original_df.shape[0])
    type_index_n = np.ones(original_df.shape[0])

    c = 0
    while True:
        c += 1
        if new:
            df = original_df
            df["n"] = n
            df["type_index_n"] = type_index_n
            df["gamma"] = gamma
            f = new_robertson

            def condition(x):
                return np.all(
                    x["gamma_predict"].series_equal(pl.Series(gamma))
                    and np.all(x["n"].series_equal(pl.Series(n)))
                )

        else:
            df = original_df
            df["gamma"] = gamma
            f = old_robertson

            def condition(x):
                return np.all(x["gamma_predict"].series_equal(pl.Series(gamma)))

        df = f(
            df,
            water_level,
            area_quotient_cone_tip=area_quotient_cone_tip,
            pre_excavated_depth=pre_excavated_depth,
            p_a=p_a,
        )

        df["gamma_predict"] = np.nan_to_num(df["gamma_predict"])
        if condition(df):
            break
        elif c == 4:
            break
        else:
            gamma = df["gamma_predict"]
            if new:
                n = df["n"]

    return df.with_column(ic_to_soil_type())


def old_robertson(
    df, water_level, area_quotient_cone_tip=None, pre_excavated_depth=None
):
    """
    Old (1990) implementation of Robertson.

    :param df: (DataFrame)
    :param water_level: (float)
    :param area_quotient_cone_tip: (float)
    :param pre_excavated_depth: (float)
    :return: (DataFrame) Classified dataframe.
    """
    df = (
        df.pipe(geo.delta_depth, pre_excavated_depth)
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
        .pipe(lambda df: df.with_column(exprs.ic_to_gamma(water_level)))
    )

    return df


def new_robertson(
    df, water_level, area_quotient_cone_tip=None, pre_excavated_depth=None, p_a=0.1
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
        df.pipe(geo.delta_depth, pre_excavated_depth)
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
        .pipe(lambda df: df.with_column(exprs.ic_to_gamma(water_level)))
    )
    return df
