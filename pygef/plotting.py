from __future__ import annotations

from typing import Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pygef import CPTData, BoreData
import polars as pl
import numpy as np


def init_fig(
    fig: plt.Figure | None, dpi: int, figsize: Tuple[int, int] | None
) -> Tuple[plt.Figure, bool]:
    figure_given = True
    if fig is None:
        figure_given = False
        fig = plt.figure(figsize=figsize, dpi=dpi)
    return fig, figure_given


def plot_cpt(
    data: CPTData, fig: plt.Figure | None, dpi: int = 100
) -> plt.Figure | None:
    df = data.data.select(
        pl.when(pl.all().abs() > 1e4).then(None).otherwise(pl.all()).keep_name()
    )

    fig, figure_given = init_fig(fig, dpi, figsize=(8, 12))

    axs = fig.subplots(1, 3, gridspec_kw={"width_ratios": [2, 1, 1]})
    (ax1, ax2, ax3) = axs

    # only set left axes y label
    # it is clear that this label is used for all y axes
    ax1.set_ylabel("depth")

    titles = ["cone_resistance [Mpa]", "friction_ratio [%]", "friction [MPa]"]
    for (ax, title) in zip(axs, titles):
        ax.invert_yaxis()
        ax.set_title(title)

    depth = df["depth"]

    ax1.plot(df["coneResistance"], depth)

    if "frictionRatio" in df.columns:
        ax2.plot(df["frictionRatio"], depth, label="measured Rf")
    ax2.plot(
        df["localFriction"] / df["coneResistance"] * 100,
        depth,
        label="computed Rf",
        ls="dashed",
    )
    ax2.set_xbound(0, 10)
    ax3.plot(
        df["localFriction"],
        depth,
    )
    ax2.legend()

    if figure_given:
        return fig
    else:
        plt.show()
        return None


def plot_bore(
    data: BoreData, fig: plt.Figure | None, dpi: int = 100
) -> plt.Figure | None:
    fig, figure_given = init_fig(fig, dpi, figsize=(4, 12))
    ax = fig.subplots(1, 1)

    df = data.data
    soil_dist = np.stack(df["soil_dist"].to_numpy())  # type: ignore[call-overload]
    cum_soil_dist = soil_dist.cumsum(axis=1)

    # peat, clay, silt, sand, gravel, rocks
    c = ["#a76b29", "#578E57", "#0078C1", "#DBAD4B", "#708090", "#59626b"]
    legend = ["peat", "clay", "silt", "sand", "gravel", "rocks"]
    ax.invert_yaxis()
    ax.set_ylabel("depth [m]")
    ax.set_xlabel("cumulative soil fraction")

    for i in range(5):
        ax.fill_betweenx(
            np.repeat(df["upper_boundary"], 2),
            np.zeros(df.shape[0] * 2),
            np.roll(np.repeat(cum_soil_dist[:, -(i + 1)], 2), 1),
            color=c[i],
        )

    patches = [mpatches.Patch(color=color, label=key) for key, color in zip(legend, c)]
    plt.legend(handles=patches, bbox_to_anchor=(1, 1), loc="upper left")

    if figure_given:
        return fig
    else:
        plt.show()
        return None
