import numpy as np
from pygef import geo
import pygef.utils as utils


# TODO: at test coverage to travis.yaml Nice to have. :)


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
    return df.assign(
        excess_pore_pressure_ratio=(u2 - df["water_pressure"])
        / (df["qt"] - df["soil_pressure"])
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

    ic_mask = df["type_index"].values > 3.22
    # gamma_(sat) and ic > 3.6
    df.loc[ic_mask, "gamma_predict"] = 11

    ic_mask = df["type_index"].values <= 3.22
    # gamma_(sat) and ic < 3.6
    df.loc[ic_mask, "gamma_predict"] = 16

    ic_mask = df["type_index"].values <= 2.76
    # gamma_(sat) and ic < x
    df.loc[ic_mask, "gamma_predict"] = 18

    ic_mask = df["type_index"].values <= 2.40
    # gamma_sat and ic < x
    df.loc[ic_mask & mask_below_water, "gamma_predict"] = 19

    ic_mask = df["type_index"].values <= 1.80
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

    ic_mask = df["type_index"].values > 3.22
    df.loc[ic_mask, "soil_type"] = "Peat"

    ic_mask = df["type_index"].values <= 3.22
    df.loc[ic_mask, "soil_type"] = "Clays"

    ic_mask = df["type_index"].values <= 2.76
    df.loc[ic_mask, "soil_type"] = "Clayey silt to silty clay"

    ic_mask = df["type_index"].values <= 2.40
    df.loc[ic_mask, "soil_type"] = "Silty sand to sandy silt"

    ic_mask = df["type_index"].values <= 1.80
    df.loc[ic_mask, "soil_type"] = "Sands: clean sand to silty"

    ic_mask = df["type_index"].values <= 1.25
    df.loc[ic_mask, "soil_type"] = "Gravelly sands"
    return df


def type_index(df):
    return df.assign(
        type_index=(
            (
                (
                    3
                    - np.log10(
                        df["normalized_cone_resistance"]
                        * (1 - df["excess_pore_pressure_ratio"])
                        + 1
                    )
                )
                ** 2
                + (1.5 + 1.3 * np.log10(df["normalized_friction_ratio"])) ** 2
            )
            ** 0.5
        )
    )


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
    gamma = np.ones(original_df.shape[0]) * 18

    c = 0
    while True:
        c += 1
        df = original_df.assign(gamma=gamma)

        def condition(x):
            return np.all(x["gamma_predict"] == gamma)

        df = been_jeffrey(
            df,
            water_level,
            area_quotient_cone_tip=area_quotient_cone_tip,
            pre_excavated_depth=pre_excavated_depth,
        )
        df = df.assign(gamma_predict=np.nan_to_num(df["gamma_predict"]))
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
        .pipe(utils.nan_to_zero)
        .pipe(type_index)
        .pipe(ic_to_gamma, water_level)
    )
    return df
