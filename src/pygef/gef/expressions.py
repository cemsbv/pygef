from __future__ import annotations

import polars as pl


def ic_to_gamma(water_level):
    """
    Return the expression needed to compute "gamma_predict"
    """
    below_water = (1.0 - pl.col("depth")) < water_level
    ti = pl.col("type_index")
    return (
        pl.when(ti > 3.22)
        .then(11.0)
        .when((ti <= 3.22) & (ti > 2.76))
        .then(16.0)
        .when((ti <= 2.76) & ~(below_water))
        .then(18.0)
        .when((ti <= 2.40) & below_water)
        .then(19.0)
        .when((ti <= 1.80) & below_water)
        .then(20.0)
        .otherwise(1.0)
        .alias("gamma_predict")
    )


def ic_to_soil_type(ti: pl.Expr = pl.col("type_index")):
    """
    Assign the soil type to the corresponding Ic.
    """
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
                - (
                    pl.col("normalized_cone_resistance")
                    * (1.0 - pl.col("excess_pore_pressure_ratio"))
                    + 1.0
                ).log10()
            )
            ** 2
            + (1.5 + 1.3 * (pl.col("normalized_friction_ratio")).log10()) ** 2
        )
        ** 0.5
    ).alias("type_index")
