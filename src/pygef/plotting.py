from __future__ import annotations

from typing import List, Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
from matplotlib.gridspec import GridSpec

from pygef.bore import BoreData
from pygef.cpt import CPTData

try:
    import contextily as ctx
except ImportError:
    ctx = None

FigureSize = (8, 12)
TickLoc = plticker.MultipleLocator(base=0.5)


def plot_cpt(
    data: CPTData,
    ax: plt.Axes | None = None,
    dpi: int = 100,
    use_offset: bool = False,
) -> Tuple[plt.Axes, plt.Axes, plt.Axes]:
    """
    Create a plot with three axes.
        - cone_resistance [MPa]
        - friction_ratio [%] (twiny)
        - friction [MPa] (twiny)

    :param data: (BoreData) Bore data object
    :param ax: (Axes, optional) Axes object used to add axes
    :param dpi: (int, optional)  Default is 100 Resolution of the figure.
    :param use_offset: (bool, optional)  Default is False Plot depth with respect to offset.
    """
    df = data.data
    if use_offset:
        yname = "depthOffset"
        label_name = "depth" if "depth" in data.columns else "penetrationLength"
    else:
        yname = "depth" if "depth" in data.columns else "penetrationLength"
        label_name = yname

    if ax is None:
        fig = plt.figure(figsize=FigureSize, dpi=dpi, layout="tight")
        ax = fig.subplots(1, 1)

    p1 = None
    p11 = None
    p12 = None
    ax2 = ax.twiny()
    p2 = None
    ax3 = ax.twiny()
    p3 = None
    p4 = None

    axes = (ax, ax2, ax3)

    # set the properties on the coneResistance axes
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    ax.spines["top"].set_position(("axes", 1))
    ax.set_xlim(0, 40)
    ax.set_xlabel("$q_c$ [MPa]")
    ax.xaxis.label.set_color("#2d2e87")
    if not use_offset:
        ax.invert_yaxis()

    # set axis label
    if use_offset:
        ax.set_ylabel(f"{label_name} [m w.r.t. vertical position offset]")
    else:
        ax.set_ylabel(f"{label_name} [m]")

    # create grid
    major_ticks = np.arange(0, 41, 5)
    minor_ticks = np.arange(0, 41, 2.5)
    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.grid(which="both")
    ax.grid(which="minor", alpha=0.2)
    ax.grid(which="major", alpha=0.5)
    ax.yaxis.set_major_locator(TickLoc)

    # set the properties on the localFriction axes
    ax2.xaxis.set_ticks_position("top")
    ax2.xaxis.set_label_position("top")
    ax2.spines["top"].set_position(("axes", 1.05))
    ax2.set_xlabel("$f_s$ [MPa]")
    ax2.set_xlim(0, 0.8)
    ax2.xaxis.label.set_color("#e04913")

    # set the properties on the frictionRatio axes
    ax3.xaxis.set_ticks_position("top")
    ax3.xaxis.set_label_position("top")
    ax3.spines["top"].set_position(("axes", 1.1))
    ax3.set_xlabel("$R_f$ [%]")
    ax3.set_xlim(0, 16)
    ax3.invert_xaxis()
    ax3.xaxis.label.set_color("tab:gray")

    # add data to figure
    # plot coneResistance
    if "coneResistance" in data.columns:
        (p1,) = ax.plot(
            df["coneResistance"], df[yname], color="#2d2e87", label="coneResistance"
        )
    # plot localFriction
    if "localFriction" in df.columns:
        (p2,) = ax2.plot(
            df["localFriction"], df[yname], color="#e04913", label="localFriction"
        )

    # plot measured frictionRatio
    if "frictionRatio" in df.columns:
        (p3,) = ax3.plot(
            df["frictionRatio"],
            df[yname],
            label="frictionRatio measured",
            color="tab:gray",
        )

    # plot computed frictionRatio
    if "frictionRatioComputed" in df.columns:
        (p4,) = ax3.plot(
            df["frictionRatioComputed"],
            df[yname],
            label="frictionRatio computed",
            ls="dashed",
            color="tab:gray",
        )
    # add hlines
    if data.groundwater_level is not None:
        value = data.groundwater_level_offset if use_offset else data.groundwater_level
        p11 = ax.axhline(
            value,
            label=f"groundwater level: {value:.2f}",
            color="tab:blue",
            ls="dashed",
        )
    if data.predrilled_depth is not None:
        value = data.predrilled_depth_offset if use_offset else data.predrilled_depth
        p12 = ax.axhline(
            value,
            label=f"predrilled depth: {value:.2f}",
            color="tab:brown",
            ls="dashed",
        )

    # add legend
    ax.legend(
        loc="upper center",
        title=f"CPT: {data.alias if data.bro_id is None else data.bro_id}",
        handles=[i for i in [p1, p2, p3, p4, p11, p12] if i is not None],
    )
    return axes


def plot_bore(
    data: BoreData,
    ax: plt.Axes | None = None,
    dpi: int = 100,
    legend: bool = True,
    use_offset: bool = False,
) -> plt.Axes:
    """
    Create a plot with one axes.
        - soil distribution

    :param data: Bore data object
    :param ax: Axes object
    :param dpi: Default is 100 Resolution of the figure.
    :param legend: Default is True Add legend to the figure.
    :param use_offset: (bool, optional)  Default is False Plot depth with respect to offset.
    """
    if use_offset:
        yupper = "upperBoundaryOffset"
        ylower = "lowerBoundaryOffset"
    else:
        yupper = "upperBoundary"
        ylower = "lowerBoundary"

    if ax is None:
        fig = plt.figure(figsize=FigureSize, dpi=dpi, layout="tight")
        ax = fig.subplots(1, 1)

    df = data.data
    soil_dist = np.stack(df["soilDistribution"].to_numpy())
    cum_soil_dist = soil_dist.cumsum(axis=1)

    # peat, clay, silt, sand, gravel, rocks
    legend_colors = [
        "#a76b29",
        "#578E57",
        "#0078C1",
        "#DBAD4B",
        "#708090",
        "#59626b",
    ]
    legend_names = ["peat", "clay", "silt", "sand", "gravel", "rocks"]
    if not use_offset:
        ax.invert_yaxis()
    # set axis label
    if use_offset:
        ax.set_ylabel("depth [m w.r.t. vertical position offset]")
    else:
        ax.set_ylabel("depth [m]")
    ax.set_xlabel("cumulative soil fraction [-]")
    ax.yaxis.set_major_locator(TickLoc)

    for i in range(5):
        ax.fill_betweenx(
            np.array(list(zip(df[yupper], df[ylower]))).flatten(),
            np.zeros(df.shape[0] * 2),
            np.repeat(cum_soil_dist[:, -(i + 1)], 2),
            color=legend_colors[i],
        )

    # add the name of the soil to the plot
    for row in df.rows(named=True):
        y = (row[ylower] - row[yupper]) / 2 + row[yupper]
        ax.annotate(text=row["geotechnicalSoilName"], xy=(0.25, y))

    # add legend
    if legend:
        patches = [
            mpatches.Patch(color=color, label=key)
            for key, color in zip(legend_names, legend_colors)
        ]
        ax.legend(
            handles=patches,
            bbox_to_anchor=(1, 1),
            loc="upper left",
            title=f"BHRgt: {data.alias if data.bro_id is None else data.bro_id}",
        )

    return ax


def plot_merge(
    bore_data: BoreData, cpt_data: CPTData, dpi: int = 100, basemap: bool = True
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Create one plot that combines the CPT and BHRgt data.

    plot with three axes.
        - cone_resistance [Mpa]
            - friction_ratio [%] (twiny)
            - friction [MPa] (twiny)
        - soil distribution
        - map of the Bore and CPT location

    :param bore_data: Bore data object
    :param cpt_data: CPT data object
    :param dpi: Default is 100 Resolution of the figure.
    :param basemap: Default is True Add a basemap to the map with contextily
    """

    # init subplots
    fig = plt.figure(figsize=FigureSize, dpi=dpi, layout="constrained")
    gs = GridSpec(2, 2, figure=fig, width_ratios=[2, 1], height_ratios=[1, 0.5])
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharey=ax1)
    ax3 = fig.add_subplot(gs[2:])
    axes = [ax1, ax2, ax3]

    # fill axes and update ylabels
    _ = plot_cpt(cpt_data, ax1, use_offset=True)
    _ = plot_bore(bore_data, ax2, legend=False, use_offset=True)
    ax2.set_ylabel("")

    # plot BHRgt location
    ax3.scatter(
        bore_data.delivered_location.x,
        bore_data.delivered_location.y,
        marker="s",
        color="tab:brown",
        label=f"BHRgt: {bore_data.bro_id}",
    )
    # plot cpt location
    ax3.scatter(
        cpt_data.delivered_location.x,
        cpt_data.delivered_location.y,
        marker="v",
        color="tab:green",
        label=f"CPT: {cpt_data.bro_id}",
    )
    # make sure there is no offset in the axis
    ax3.ticklabel_format(useOffset=False, style="plain")
    # set axis to equal
    ax3.set_box_aspect(1)
    # rotate labes axis
    ax3.xaxis.set_tick_params(rotation=45)
    # add legend
    ax3.legend(
        loc="upper left",
        title="Location",
    )

    # add base map
    if basemap:
        # check if contextily is installed
        if ctx is None:
            raise ImportError(
                "cannot import name contextily. To use this feature install pygef[map]."
            )

        # make sure the extent of the figure is not larger than 500 m by 500 m
        ax3.set_xbound(
            cpt_data.delivered_location.x - 250, cpt_data.delivered_location.x + 250
        )
        ax3.set_ybound(
            cpt_data.delivered_location.y - 250, cpt_data.delivered_location.y + 250
        )
        ctx.add_basemap(
            ax3,
            crs=cpt_data.delivered_location.srs_name,
            source=ctx.providers.OpenStreetMap.Mapnik,
        )

    # add watermark to plot
    plt.gcf().text(
        0,
        0,
        "created by pyGEF supported by CRUX Engineering Microservices BV (CEMS)",
        fontsize=10,
        color="gray",
        alpha=0.5,
    )

    return fig, axes
