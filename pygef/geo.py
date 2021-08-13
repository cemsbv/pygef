import numpy as np
import polars as pl


def delta_depth(df, pre_excavated_depth=None):
    """
    Take pre-excavated depth into account.

    This function corrects the depth column and adds a column (np.diff(depth))

    :param df: (DataFrame) with depth column
    :param pre_excavated_depth: (flt)
    :return: (DataFrame) [depth, delta_depth]
    """
    polars_df = pl.from_pandas(df)
    polars_df["delta_depth"] = np.r_[
        np.array([df["depth"][0]]), np.diff(df["depth"].values)
    ]
    return polars_df.to_pandas()


def soil_pressure(df):
    polars_df = pl.from_pandas(df)
    polars_df["soil_pressure"] = np.cumsum(
        polars_df["gamma"] * polars_df["delta_depth"], axis=0
    )
    return polars_df.to_pandas()


def water_pressure(df, water_level):
    polars_df = pl.from_pandas(df)
    polars_df["water_pressure"] = polars_df["depth"].apply(
        lambda depth: (depth - water_level) * 9.81
    )
    polars_df[polars_df["water_pressure"] < 0, "water_pressure"] = 0
    return polars_df.to_pandas()


def effective_soil_pressure(df):
    polars_df = pl.from_pandas(df)
    polars_df["effective_soil_pressure"] = (
        polars_df["soil_pressure"] - polars_df["water_pressure"]
    )
    return polars_df.to_pandas()


def qt(df, area_quotient_cone_tip=None):
    polars_df = pl.from_pandas(df)
    if "u2" in df.columns and area_quotient_cone_tip is not None:
        polars_df["qt"] = polars_df["qc"] + polars_df["u2"].apply(
            lambda u2: u2 * (1.0 - area_quotient_cone_tip)
        )
    else:
        polars_df["qt"] = polars_df["qc"]

    return polars_df.to_pandas()


def normalized_cone_resistance(df):
    polars_df = pl.from_pandas(df)
    polars_df["normalized_cone_resistance"] = (
        polars_df["qt"] - polars_df["soil_pressure"]
    ) / polars_df["effective_soil_pressure"]
    polars_df[
        polars_df["normalized_cone_resistance"] < 0, "normalized_cone_resistance"
    ] = 1
    return polars_df.to_pandas()


def normalized_friction_ratio(df):
    polars_df = pl.from_pandas(df)

    if "fs" in df.columns:
        fs = polars_df["fs"]
    else:
        fs = polars_df["friction_number"] * polars_df["qc"] / 100

    polars_df["normalized_friction_ratio"] = (
        fs / (polars_df["qt"] - polars_df["soil_pressure"])
    ) * 100

    polars_df[
        polars_df["normalized_friction_ratio"] < 0, "normalized_friction_ratio"
    ] = 0.1

    return polars_df.to_pandas()
