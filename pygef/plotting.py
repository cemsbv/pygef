from __future__ import annotations
import matplotlib.pyplot as plt
from pygef import CPTData
import polars as pl


def plot_cpt(
    data: CPTData, fig: plt.Figure | None, dpi: int = 100
) -> plt.Figure | None:
    df = data.data.select(
        pl.when(pl.all().abs() > 1e4).then(None).otherwise(pl.all()).keep_name()
    )

    figure_given = True
    if fig is None:
        figure_given = False
        fig = plt.figure(figsize=(8, 12), dpi=dpi)

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
