import numpy as np
import polars as pl
from polars import col, lit

import pygef.utils as utils
from pygef import geo


def excess_pore_pressure_ratio(df):
    """
    Assign the excess pore pressure ratio, if the water pressure u2 is defined. Else, raise ERROR.

    :param df: (DataFrame)
    :return: (DataFrame)
    """
    try:
        u2 = df["u2"]
    except KeyError:
        raise SystemExit("ERROR: u2 not defined in .gef file, change classifier")

    df["excess_pore_pressure_ratio"] = (u2 - df["water_pressure"]) / (
        df["qt"] - df["soil_pressure"]
    )

    return df


def ic_to_gamma(water_level):
    """
    Return the expression needed to compute "gamma_predict"
    """
    below_water = (1.0 - col("depth")) < water_level
    ti = col("type_index")
    return (
        pl.when(ti > 3.22)
        .then(11.0)
        .when((ti <= 3.22) & (ti > 2.76))
        .then(16.0)
        .when((ti <= 2.76) & ~(below_water))
        .then(18.0)
        .when(ti <= 2.40 & below_water)
        .then(19.0)
        .when(ti <= 1.80 & below_water)
        .then(20.0)
        .otherwise(1.0)
        .alias("gamma_predict")
    )


def ic_to_soil_type():
    """
    Assign the soil type to the corresponding Ic.
    """
    ti = col("type_index")
    return (
        pl.when(ti > 3.22)
        .then("Peat")
        .when((ti <= 3.22) & (ti > 2.67))
        .then("Clays")
        .when((ti <= 2.67) & (ti > 2.4))
        .then("Clayey silt to silty clay")
        .when((ti <= 2.4) & (ti > 1.8))
        .then("Silty sand to sandy silt")
        .when((ti <= 1.8) & (ti > 1.25))
        .then("Sands: clean sand to silty")
        .when(ti <= 1.25)
        .then("Gravelly sands")
        .otherwise("")
        .alias("soil_type")
    )


def type_index() -> pl.Expr:
    return (
        (
            (
                pl.lit(3.0)
                - np.log10(
                    col("normalized_cone_resistance")
                    * (1.0 - col("excess_pore_pressure_ratio"))
                    + 1.0
                )
            )
            ** 2
            + (1.5 + 1.3 * np.log10(col("normalized_friction_ratio"))) ** 2
        )
        ** 0.5
    ).alias("type_index")


def iterate_been_jeffrey(
    original_df, water_level, area_quotient_cone_tip=None, pre_excavated_depth=None
):
    """
    Iteration function for Been & Jefferies classifier.

    :param original_df: (DataFrame)
    :param water_level: (int) Water level with respect to ground level.
    :param area_quotient_cone_tip: (float)
    :param pre_excavated_depth: (float)
    :return: (DataFrame)
    """
    gamma = np.ones(original_df.shape[0]) * 18.0

    c = 0
    while True:
        c += 1
        df = original_df
        df["gamma"] = gamma

        def condition(x):
            return np.all(x["gamma_predict"].series_equal(pl.Series(gamma)))

        df = been_jeffrey(
            df,
            water_level,
            area_quotient_cone_tip=area_quotient_cone_tip,
            pre_excavated_depth=pre_excavated_depth,
        )
        df["gamma_predict"] = np.nan_to_num(df["gamma_predict"])
        if condition(df):
            break
        elif c > 10:
            break
        else:
            gamma = df["gamma_predict"]

    return df.with_column(ic_to_soil_type())


def been_jeffrey(
    df, water_level, area_quotient_cone_tip=None, pre_excavated_depth=None
):
    """
    Implementation of Been & Jefferies.

    :param df: (DataFrame)
    :param water_level: (float)
    :param area_quotient_cone_tip: (float)
    :param pre_excavated_depth: (float)
    :return: (DataFrame)
    """
    df = (
        df.with_column(col("depth").diff().alias("delta_depth"))
        .pipe(geo.soil_pressure)
        .pipe(geo.qt, area_quotient_cone_tip)
        .pipe(geo.water_pressure, water_level)
        .pipe(geo.effective_soil_pressure)
        .pipe(
            utils.kpa_to_mpa,
            ["soil_pressure", "effective_soil_pressure", "water_pressure"],
        )
        .pipe(excess_pore_pressure_ratio)
        .pipe(geo.normalized_cone_resistance)
        .pipe(geo.normalized_friction_ratio)
        .pipe(utils.none_to_zero)
        .with_columns([type_index()])
        .with_column(ic_to_gamma(water_level))
    )
    return df
