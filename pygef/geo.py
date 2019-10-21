import numpy as np


def delta_depth(df, pre_excavated_depth=None):
    """
    Take pre-excavated depth into account.

    This function corrects the depth column and adds a column (np.diff(depth))

    :param df: (DataFrame) with depth column
    :param pre_excavated_depth: (flt)
    :return: (DataFrame) [depth, delta_depth]
    """
    return df.assign(
        depth=df["depth"],
        delta_depth=np.r_[np.array([df["depth"][0]]), np.diff(df["depth"].values)],
    )


def soil_pressure(df):
    return df.assign(soil_pressure=np.cumsum(df["gamma"] * df["delta_depth"], axis=0))


def water_pressure(df, water_level):
    df = df.assign(water_pressure=(df["depth"].values - water_level) * 9.81)
    df.loc[df["water_pressure"] < 0, "water_pressure"] = 0
    return df


def effective_soil_pressure(df):
    return df.assign(
        effective_soil_pressure=(
            df["soil_pressure"].values - df["water_pressure"].values
        )
    )


def qt(df, area_quotient_cone_tip=None):
    if "u2" in df.columns and area_quotient_cone_tip is not None:
        return df.assign(
            qt=df["qc"].values + df["u2"].values * (1 - area_quotient_cone_tip)
        )

    return df.assign(qt=df["qc"])


def normalized_cone_resistance(df):
    df = df.assign(
        normalized_cone_resistance=(
            (df["qt"] - df["soil_pressure"]) / (df["effective_soil_pressure"])
        )
    )
    df.loc[df["normalized_cone_resistance"] < 0, "normalized_cone_resistance"] = 1
    return df


def normalized_friction_ratio(df):
    if "fs" in df.columns:
        fs = df["fs"].values
    else:
        fs = df["friction_number"].values * df["qc"].values / 100
    df = df.assign(
        normalized_friction_ratio=(
            (fs / (df["qt"].values - df["soil_pressure"].values)) * 100
        )
    )
    df.loc[
        df["normalized_friction_ratio"].values < 0, "normalized_friction_ratio"
    ] = 0.1
    return df
