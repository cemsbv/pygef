# needed for python 3.7
from __future__ import annotations
from copy import copy

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import polars as pl


def colors_robertson() -> dict[str, str]:
    return {
        "Peat": "#a76b29",
        "Clays - silty clay to clay": "#578E57",
        "Silt mixtures - clayey silt to silty clay": "#0078C1",
        "Sand mixtures - silty sand to sandy silt": "#DBAD4B",
        "Sands - clean sand to silty sand": "#e5c581",
        "Gravelly sand to dense sand": "#708090",
        None: "black",
    }


def colors_been_jefferies() -> dict[str, str]:
    return {
        "Peat": "#a76b29",
        "Clays": "#578E57",
        "Clayey silt to silty clay": "#0078C1",
        "Silty sand to sandy silt": "#DBAD4B",
        "Sands: clean sand to silty": "#e5c581",
        "Gravelly sands": "#708090",
        None: "black",
    }


def num_columns(classification, df_group):
    """
    Get the columns number to plot.

    :param classification: (str) classification
    :param df_group: grouped dataframe.
    :return: number of columns to plot
    """
    if classification is None:
        return 2
    if df_group is None and classification is not None:
        return 4
    else:
        return 5


def plot_cpt(
    df, df_group, classification, show, figsize, grid_step_x, colors, dpi, z_NAP
):
    """
    Main function to plot qc, Fr and soil classification.

    :param df: Complete df.
    :param df_group: Grouped df.
    :param show: If show is True the figure is shown.
    :param figsize: Figure size (x, y)
    :return:
    """
    title = None
    title_group = None

    if classification is not None:
        print(df)
        df, title = assign_color(df, classification, colors)
    if df_group is not None:
        df_group = copy(df_group)
        df_group = df_group.rename({"layer": "soil_type"})
        df_group, title_group = assign_color(df_group, classification, colors=colors)
        if colors is None:
            title_group = "Filtered"
        else:
            title_group = "User defined filter"
    if z_NAP:
        depth_max = df["elevation_with_respect_to_nap"].min()
        depth_min = df["elevation_with_respect_to_nap"].max()
    else:
        depth_max = df["depth"].max()
        depth_min = df["depth"].min()

    fig = plt.figure(figsize=figsize, dpi=dpi)
    n = 0
    num_col = num_columns(classification, df_group)
    for c, unit in zip(["qc", "friction_number"], ["[MPa]", "[%]"]):
        n += 1
        ax = fig.add_subplot(1, num_col, n)
        if z_NAP:
            plt.plot(
                df[c].to_numpy(), df["elevation_with_respect_to_nap"].to_numpy(), "C0"
            )
            if n == 1:
                ax.set_ylabel("Z NAP [m]")
        else:
            plt.plot(df[c].to_numpy(), df["depth"].to_numpy(), "C0")
            if n == 1:
                ax.set_ylabel("Z [m]")
        if n > 1:
            # keep grid, but no labels
            ax = plt.gca()
            labels = [item.get_text() for item in ax.get_yticklabels()]
            empty_string_labels = [""] * len(labels)
            ax.set_yticklabels(empty_string_labels)
            plt.xlim([0, min(15, df[c].max() + 1)])
        plt.xlim(0, df[c].max() * 1.05)
        ax.set_xlabel(f"{c} {unit}")

        plt.grid()

        # custom x grid
        if grid_step_x is not None:
            ax.set_xticks(np.arange(0, df[c].max() + grid_step_x, grid_step_x))
        plt.ylim(depth_max, depth_min)

    if classification is not None:
        fig = add_plot_classification(
            fig, df, depth_max, depth_min, title, num_col, z_NAP=z_NAP
        )
    if df_group is not None:
        fig = add_grouped_classification(
            fig, df_group, depth_max, depth_min, title_group, num_col, z_NAP=z_NAP
        )

    if classification is not None:
        # custom legend
        legend_dict = get_legend(classification, colors=colors)
        patch_list = []
        for key in legend_dict:
            data_key = mpatches.Patch(color=legend_dict[key], label=key)
            patch_list.append(data_key)

        plt.legend(handles=patch_list, bbox_to_anchor=(1, 1), loc="upper left")
    if show:
        plt.show()
    else:
        return fig


def assign_color(df, classification, colors):
    """
    Add to the dataframe the column 'colour' based on the chosen classification.

    :param df: original dataframe.
    :param classification: Chosen classification.
    :param colors: (Dictionary) Dictionary with the user color associated to each layer.
    :return:
    """
    if colors is None:
        if classification == "robertson":
            colors = colors_robertson()
            df = df.with_column(
                pl.col("soil_type").apply(lambda row: colors[row]).alias("colour")
            )

            return (
                df,
                "Robertson",
            )
        elif classification == "been_jefferies":
            colors = colors_been_jefferies()
            df = df.with_column(
                pl.col("soil_type").apply(lambda row: colors[row]).alias("colour")
            )

            return (
                df,
                "Been Jefferies",
            )
    else:
        df = df.with_column(
            pl.col("soil_type").apply(lambda row: colors[row]).alias("colour")
        )

        return (
            df,
            "User defined",
        )


def add_plot_classification(fig, df, depth_max, depth_min, title, num_col, z_NAP):
    """
    Add to the plot the selected classification.

    :param fig: Original figure.
    :param depth_max: Maximum depth.
    :param depth_min: Minimum depth.
    :return:
    """
    ax = fig.add_subplot(1, num_col, 3)
    df = df.with_column(pl.col("soil_type").fill_null("UNKNOWN"))
    for st in df["soil_type"].unique():
        partial_df = df[df["soil_type"] == st]
        if z_NAP:
            plt.hlines(
                y=partial_df["elevation_with_respect_to_nap"],
                xmin=0,
                xmax=1,
                colors=partial_df["colour"],
                label=st,
            )
        else:
            plt.hlines(
                y=partial_df["depth"],
                xmin=0,
                xmax=1,
                colors=partial_df["colour"],
                label=st,
            )
    ax.set_xticks([])
    ax.set_title(f"{title}")
    plt.ylim(depth_max, depth_min)
    return fig


def add_grouped_classification(
    fig, df_group, depth_max, depth_min, title_group, num_col, z_NAP
):
    """
    Add to the plot the selected classification.

    :param fig: Original figure.
    :param depth_max: Maximum depth.
    :param depth_min: Minimum depth.
    :return: Complete figure.
    """
    ax = fig.add_subplot(1, num_col, 4)
    df = df_group
    for i, layer in enumerate(df["soil_type"]):
        if z_NAP:
            plt.barh(
                y=df["z_centr_nap"][i],
                height=df["thickness"][i],
                width=5,
                color=df["colour"][i],
                label=layer,
            )
        else:
            plt.barh(
                y=df["z_centr"][i],
                height=df["thickness"][i],
                width=5,
                color=df["colour"][i],
                label=layer,
            )
    ax.set_xticks([])
    ax.set_title(f"{title_group} classification")
    plt.ylim(depth_max, depth_min)
    return fig


def plot_merged_cpt_bore(df, figsize=None, show=True):
    fig = plt.figure(figsize=figsize)
    subplot_val = 131
    plt.subplot(subplot_val)
    plt.plot(df["qc"].to_numpy(), -df["depth"].to_numpy())

    subplot_val += 1
    plt.subplot(subplot_val)
    plt.plot(df["friction_number"].to_numpy(), -df["depth"].to_numpy())

    subplot_val += 1
    plt.subplot(subplot_val)
    if "silt_component" in df.columns:
        df = df.copy()
        df["loam_component"] += df["silt_component"]
    v = df[
        [
            "gravel_component",
            "sand_component",
            "loam_component",
            "clay_component",
            "peat_component",
        ]
    ]

    c = ["#a76b29", "#578E57", "#0078C1", "#DBAD4B", "#708090"]
    for i in range(5):
        plt.fill_betweenx(
            -df["depth"],
            np.zeros(v.shape[0]),
            np.cumsum(v, axis=1)[:, -(i + 1)],
            color=c[i],
        )

    if show:
        plt.show()
    return fig


def plot_bore(df, figsize=(11, 8), show=True, dpi=100):
    fig = plt.figure(figsize=figsize, dpi=dpi)

    v = df[
        [
            "gravel_component",
            "sand_component",
            "loam_component",
            "clay_component",
            "peat_component",
        ]
    ]

    # TODO: replace with proper polars code
    vp = v.to_pandas()
    vp.iloc[:, 2] += df.to_pandas()["silt_component"]

    # TODO: what does this do?
    # vp[vp.sum(1) < 0] = np.nan

    c = ["#a76b29", "#578E57", "#0078C1", "#DBAD4B", "#708090"]

    for i in range(5):
        plt.fill_betweenx(
            -np.repeat(df["depth_top"], 2),
            np.zeros(vp.shape[0] * 2),
            np.roll(np.repeat(np.cumsum(vp, axis=1).iloc[:, -(i + 1)], 2), 1),
            color=c[i],
        )

    legend_dict = {
        "Gravel": "#708090",
        "Sand": "#DBAD4B",
        "Loam": "#0078C1",
        "Clay": "#578E57",
        "Peat": "#a76b29",
    }
    patch_list = []
    for key in legend_dict:
        data_key = mpatches.Patch(color=legend_dict[key], label=key)
        patch_list.append(data_key)

    plt.legend(handles=patch_list, bbox_to_anchor=(1, 1), loc="upper left")

    if show:
        plt.show()
    return fig


def get_legend(classification, colors) -> dict[str, str]:
    if colors is not None:
        return colors
    elif classification == "robertson":
        return colors_robertson()
    elif classification == "been_jefferies":
        return colors_been_jefferies()
