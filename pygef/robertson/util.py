import numpy as np
from pygef import geo
import pygef.utils as utils


# TODO: at test coverage to travis.yaml Nice to have. :)


def n_exponent(df, p_a):
    mask = (
        0.381 * df["type_index_n"].values
        + 0.05 * (df["effective_soil_pressure"].values / p_a)
        - 0.15
    ) < 1
    df = df.assign(n=1)
    df.loc[mask, "n"] = (
        0.381 * df["type_index_n"][mask].values
        + 0.05 * (df["effective_soil_pressure"][mask].values / p_a)
        - 0.15
    )
    return df


def normalized_cone_resistance_n(df, p_a):
    df = df.assign(
        normalized_cone_resistance=(
            (df["qt"].values - df["soil_pressure"].values)
            / p_a
            * (p_a / df["effective_soil_pressure"].values) ** df["n"].values
        )
    )
    df.loc[
        df["normalized_cone_resistance"].values < 0, "normalized_cone_resistance"
    ] = 1
    return df


def type_index(df):
    return df.assign(
        type_index=(
            (
                (3.47 - np.log10(df["normalized_cone_resistance"].values)) ** 2
                + (np.log10(df["normalized_friction_ratio"].values) + 1.22) ** 2
            )
            ** 0.5
        )
    )


def ic_to_gamma(df, water_level):
    """
    Assign the right gamma (unit soil weight kN/m^3) to the corresponding Ic.

    :param df: (DataFrame) Original DataFrame.
    :param water_level: (int) Water level with respect to ground level.
    :return: Updated DataFrame.
    """
    mask_below_water = -df["depth"].values < water_level
    df = df.assign(gamma_predict=1)

    ic_mask = df["type_index"].values > 3.6
    # gamma_(sat) and ic > 3.6
    df.loc[ic_mask, "gamma_predict"] = 11

    ic_mask = df["type_index"].values <= 3.6
    # gamma_(sat) and ic < 3.6
    df.loc[ic_mask, "gamma_predict"] = 16

    ic_mask = df["type_index"].values <= 2.95
    # gamma_(sat) and ic < x
    df.loc[ic_mask, "gamma_predict"] = 18

    ic_mask = df["type_index"].values <= 2.6
    # gamma_sat and ic < x
    df.loc[ic_mask & mask_below_water, "gamma_predict"] = 19

    ic_mask = df["type_index"].values <= 2.05
    # gamma_sat and ic < x
    df.loc[ic_mask & mask_below_water, "gamma_predict"] = 20

    return df


def ic_to_soil_type(df):
    """
    Assign the soil type to the corresponding Ic.

    :param df: (DataFrame) Original DataFrame.
    :return: (DataFrame) Updated DataFrame.
    """
    df = df.assign(soil_type="")

    ic_mask = df["type_index"].values > 3.6
    df.loc[ic_mask, "soil_type"] = "Peat"

    ic_mask = df["type_index"].values <= 3.6
    df.loc[ic_mask, "soil_type"] = "Clays - silty clay to clay"

    ic_mask = df["type_index"].values <= 2.95
    df.loc[ic_mask, "soil_type"] = "Silt mixtures - clayey silt to silty clay"

    ic_mask = df["type_index"].values <= 2.6
    df.loc[ic_mask, "soil_type"] = "Sand mixtures - silty sand to sandy silt"

    ic_mask = df["type_index"].values <= 2.05
    df.loc[ic_mask, "soil_type"] = "Sands - clean sand to silty sand"

    ic_mask = df["type_index"].values <= 1.31
    df.loc[ic_mask, "soil_type"] = "Gravelly sand to dense sand"

    return df


def nan_to_zero(df):
    return df.fillna(0)


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
    gamma = np.ones(original_df.shape[0]) * 18
    n = np.ones(original_df.shape[0])
    type_index_n = np.ones(original_df.shape[0])

    c = 0
    while True:
        c += 1
        if new:
            df = original_df.assign(n=n, type_index_n=type_index_n, gamma=gamma)
            f = new_robertson

            def condition(x):
                return np.all(x["gamma_predict"] == gamma) and np.all(x["n"] == n)

        else:
            df = original_df.assign(gamma=gamma)
            f = old_robertson

            def condition(x):
                return np.all(x["gamma_predict"] == gamma)

        df = f(
            df,
            water_level,
            area_quotient_cone_tip=area_quotient_cone_tip,
            pre_excavated_depth=pre_excavated_depth,
            p_a=p_a,
        )

        df = df.assign(gamma_predict=np.nan_to_num(df["gamma_predict"]))
        if condition(df):
            break
        elif c == 4:
            break
        else:
            gamma = df["gamma_predict"]
            if new:
                n = df["n"]

    return df.pipe(ic_to_soil_type)


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
        .pipe(utils.nan_to_zero)
        .pipe(type_index)
        .pipe(ic_to_gamma, water_level)
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
        .pipe(utils.nan_to_zero)
        .pipe(type_index)
        .pipe(ic_to_gamma, water_level)
    )
    return df
