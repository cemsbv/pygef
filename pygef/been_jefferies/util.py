import numpy as np
import polars as pl

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


def ic_to_gamma(df, water_level):
    """
    Assign the right gamma (unit soil weight kN/m^3) to the corresponding Ic.

    :param df: (DataFrame) Original DataFrame.
    :param water_level: (int) Water level with respect to ground level.
    :return: Updated DataFrame.
    """
    mask_below_water = (1.0 - df["depth"]) < water_level
    # TODO: how to fill it properly with the same initial values?
    df["gamma_predict"] = np.tile(1.0, len(df.rows()))

    ic_mask = df["type_index"] > 3.22
    # gamma_(sat) and ic > 3.6
    df[ic_mask, "gamma_predict"] = 11.0

    ic_mask = df["type_index"] <= 3.22
    # gamma_(sat) and ic < 3.6
    df[ic_mask, "gamma_predict"] = 16.0

    ic_mask = df["type_index"] <= 2.76
    # gamma_(sat) and ic < x
    df[ic_mask, "gamma_predict"] = 18.0

    ic_mask = df["type_index"] <= 2.40
    # gamma_sat and ic < x
    df[ic_mask & mask_below_water, "gamma_predict"] = 19.0

    ic_mask = df["type_index"] <= 1.80
    # gamma_sat and ic < x
    df[ic_mask & mask_below_water, "gamma_predict"] = 20.0

    return df


def ic_to_soil_type(df):
    """
    Assign the soil type to the corresponding Ic.

    :param df: (DataFrame) Original DataFrame.
    :return: (DataFrame) Updated DataFrame.
    """
    # TODO: how to fill it properly with the same initial values?
    df["soil_type"] = np.tile("", len(df.rows()))

    ic_mask = df["type_index"] > 3.22
    df[ic_mask, "soil_type"] = "Peat"

    ic_mask = df["type_index"] <= 3.22
    df[ic_mask, "soil_type"] = "Clays"

    ic_mask = df["type_index"] <= 2.76
    df[ic_mask, "soil_type"] = "Clayey silt to silty clay"

    ic_mask = df["type_index"] <= 2.40
    df[ic_mask, "soil_type"] = "Silty sand to sandy silt"

    ic_mask = df["type_index"] <= 1.80
    df[ic_mask, "soil_type"] = "Sands: clean sand to silty"

    ic_mask = df["type_index"] <= 1.25
    df[ic_mask, "soil_type"] = "Gravelly sands"
    return df


def type_index(df):
    df["type_index"] = (
        (
            3
            - np.log10(
                df["normalized_cone_resistance"].to_numpy()
                * (1 - df["excess_pore_pressure_ratio"].to_numpy())
                + 1
            )
        )
        ** 2
        + (1.5 + 1.3 * np.log10(df["normalized_friction_ratio"].to_numpy())) ** 2
    ) ** 0.5

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

    return df.pipe(ic_to_soil_type)


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
        df.pipe(geo.delta_depth, pre_excavated_depth)
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
        .pipe(type_index)
        .pipe(ic_to_gamma, water_level)
    )
    return df
