import numpy as np
import polars as pl
import pygef.utils as utils
from pygef import geo
from pygef.expressions import ic_to_soil_type, type_index, ic_to_gamma


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
        df.with_column(pl.col("depth").diff().alias("delta_depth"))
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
        .with_column(type_index())
        .with_column(ic_to_gamma(water_level))
    )
    return df
