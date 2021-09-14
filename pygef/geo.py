import numpy as np


def delta_depth(df, pre_excavated_depth=None):
    """
    Take pre-excavated depth into account.

    This function corrects the depth column and adds a column (np.diff(depth))

    :param df: (DataFrame) with depth column
    :param pre_excavated_depth: (flt)
    :return: (DataFrame) [depth, delta_depth]
    """
    df["delta_depth"] = np.r_[np.array([df["depth"][0]]), np.diff(df["depth"])]

    return df


def soil_pressure(df):
    df["soil_pressure"] = (df["gamma"] * df["delta_depth"]).cumsum()

    return df


def water_pressure(df, water_level):
    df["water_pressure"] = df["depth"].apply(lambda depth: (depth - water_level) * 9.81)
    df[df["water_pressure"] < 0, "water_pressure"] = 0.0

    return df


def effective_soil_pressure(df):
    df["effective_soil_pressure"] = df["soil_pressure"] - df["water_pressure"]

    return df


def qt(df, area_quotient_cone_tip=None):
    if "u2" in df.columns and area_quotient_cone_tip is not None:
        df["qt"] = df["qc"] + df["u2"].apply(
            lambda u2: u2 * (1.0 - area_quotient_cone_tip)
        )
    else:
        df["qt"] = df["qc"]

    return df


def normalized_cone_resistance(df):
    df["normalized_cone_resistance"] = (df["qt"] - df["soil_pressure"]) / df[
        "effective_soil_pressure"
    ]
    df[df["normalized_cone_resistance"] < 0, "normalized_cone_resistance"] = 1.0

    return df


def normalized_friction_ratio(df):
    if "fs" in df.columns:
        fs = df["fs"]
    else:
        fs = df["friction_number"] * df["qc"] / 100.0

    df["normalized_friction_ratio"] = (fs / (df["qt"] - df["soil_pressure"])) * 100

    df[df["normalized_friction_ratio"] < 0, "normalized_friction_ratio"] = 0.1

    return df
