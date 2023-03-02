from __future__ import annotations

from typing import Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from pygef.bore import BoreData
from pygef.cpt import CPTData


def init_fig(
    fig: plt.Figure | None, dpi: int, figsize: Tuple[int, int] | None
) -> Tuple[plt.Figure, bool]:
    figure_given = True
    if fig is None:
        figure_given = False
        fig = plt.figure(figsize=figsize, dpi=dpi)
    return fig, figure_given


def plot_cpt(
    data: CPTData, fig: plt.Figure | None = None, dpi: int = 100
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes, plt.Axes]]:
    """
    Create a plot with three axes.
        - cone_resistance [Mpa]
        - friction_ratio [%] (twiny)
        - friction [MPa] (twiny)

    :param data: (BoreData) Bore data object
    :param fig: (Figure, optional) Figure object used to add axes
    :param dpi: (int, optional)  Default is 100 Resolution of the figure.
    :return: Figure, Axes
    """
    df = data.data.select(
        pl.when(pl.all().abs() > 1e4).then(None).otherwise(pl.all()).keep_name()
    )

    fig, figure_given = init_fig(fig, dpi, figsize=(8, 12))
    ax1 = fig.subplots(1, 1)
    ax2 = ax1.twiny()
    ax3 = ax1.twiny()

    ax1.set_xbound(0, 40)
    ax1.set_ylabel("Depth [m]")
    ax1.set_xlabel("$q_c$ [MPa]")
    ax1.xaxis.label.set_color("tab:blue")
    ax1.invert_yaxis()
    ax1.grid()

    ax2.spines["bottom"].set_position(("outward", 0))
    ax2.set_xlabel("fs [MPa]")
    ax1.set_xbound(0, 10)
    ax2.xaxis.label.set_color("tab:orange")
    ax2.invert_yaxis()

    ax3.spines["top"].set_position(("outward", 40))
    ax3.set_xlabel("rf [%]")
    ax3.invert_xaxis()
    ax3.invert_yaxis()
    ax3.set_xbound(0, 10)
    ax3.xaxis.label.set_color("tab:gray")

    # add data to figure
    if "coneResistance" in df.columns:
        ax1.plot(df["coneResistance"], df["depth"], color="tab:blue", label="$q_c$")

    if "frictionRatio" in df.columns:
        ax3.plot(
            df["frictionRatio"], df["depth"], label="rf measured", color="tab:gray"
        )

    if "localFriction" in df.columns and "coneResistance" in df.columns:
        ax3.plot(
            df["localFriction"] / df["coneResistance"] * 100,
            df["depth"],
            label="rf computed",
            ls="dashed",
            color="tab:gray",
        )

    if "localFriction" in df.columns:
        ax3.plot(df["localFriction"], df["depth"], color="tab:orange", label="fs")

    plt.legend(loc="upper left")
    return fig, (ax1, ax2, ax3)


def plot_bore(
    data: BoreData, fig: plt.Figure | None = None, dpi: int = 100
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a plot with one axes.
        - soil distribution

    :param data: Bore data object
    :param fig: Figure object used to add axes
    :param dpi: Default is 100 Resolution of the figure.
    """
    fig, figure_given = init_fig(fig, dpi, figsize=(8, 12))
    ax = fig.subplots(1, 1)

    df = data.data
    soil_dist = np.stack(df["soil_dist"].to_numpy())
    cum_soil_dist = soil_dist.cumsum(axis=1)

    # peat, clay, silt, sand, gravel, rocks
    c = ["#a76b29", "#578E57", "#0078C1", "#DBAD4B", "#708090", "#59626b"]
    legend = ["peat", "clay", "silt", "sand", "gravel", "rocks"]
    ax.invert_yaxis()
    ax.set_ylabel("depth [m]")
    ax.set_xlabel("cumulative soil fraction")

    for i in range(5):
        ax.fill_betweenx(
            np.array(list(zip(df["upper_boundary"], df["lower_boundary"]))).flatten(),
            np.zeros(df.shape[0] * 2),
            np.repeat(cum_soil_dist[:, -(i + 1)], 2),
            color=c[i],
        )

    # add the name of the soil to the plot
    for row in df.rows(named=True):
        y = (row["lower_boundary"] - row["upper_boundary"]) / 2 + row["upper_boundary"]
        ax.annotate(text=row["geotechnical_soil_name"], xy=(0.25, y))

    # add legend
    patches = [mpatches.Patch(color=color, label=key) for key, color in zip(legend, c)]
    plt.legend(handles=patches, bbox_to_anchor=(1, 1), loc="best")

    return fig, ax
