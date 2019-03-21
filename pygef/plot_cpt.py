import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

colours_robertson = {'Peat': '#a76b29',
                     'Clays - silty clay to clay': '#578E57',
                     'Silt mixtures - clayey silt to silty clay': '#0078C1',
                     'Sand mixtures - silty sand to sandy silt': '#DBAD4B',
                     'Sands - clean sand to silty sand': 'gold',
                     'Gravelly sand to dense sand': '#708090',
                     None: 'black'
                     }

colours_been_jeffrey = {'Peat': '#a76b29',
                        'Clays': '#578E57',
                        'Clayey silt to silty clay': '#0078C1',
                        'Silty sand to sandy silt': '#DBAD4B',
                        'Sands: clean sand to silty': 'gold',
                        'Gravelly sands': '#708090',
                        None: 'black'
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
        return 3
    else:
        return 4


def plot_cpt(df, df_group, classification, show=True, figsize=(12, 30)):
    """
    Main function to plot qc, Fr and soil classification.
    :param df: Complete df.
    :param df_group: Grouped df.
    :param show: If show is True the figure is shown.
    :param figsize: Figure size (x, y) , x i the width y is the height.
    :return:
    """
    title = None
    title_group = None

    if classification is not None:
        df, title = assign_color(df, classification)
    if df_group is not None:
        df_group = df_group.copy()
        df_group = df_group.rename(columns={'layer': 'soil_type'})
        df_group, title_group = assign_color(df_group, classification)
        title_group = 'Filtered'

    depth_max = df['depth'].max()
    depth_min = df['depth'].min()
    fig = plt.figure(figsize=figsize)
    n = 0
    num_col = num_columns(classification, df_group)
    for c, unit in zip(['qc', 'Fr'], ['[MPa]', '[%]']):
        n += 1
        fig_i = fig.add_subplot(1, num_col, n)
        plt.plot(df[c], df['depth'], 'b')
        fig_i.set_xlabel(f'{c} {unit}')
        fig_i.set_ylabel('Z [m]')
        plt.grid()
        fig_i.set_xticks(np.arange(0, df[c].max() + 2, 2))
        fig_i.xaxis.set_tick_params(labeltop='on')
        plt.ylim(depth_max, depth_min)

    if classification is not None:
        fig = add_plot_classification(fig, df, depth_max, depth_min, title, num_col)
    if df_group is not None:
        fig = add_grouped_classification(fig, df_group, depth_max, depth_min, title_group, num_col)
    if show:
        plt.show()
    else:
        return fig


def assign_color(df, classification):
    """
    Add to the dataframe the column 'colour' based on the chosen classification.
    :param df: original dataframe.
    :param classification: Chosen classification.
    :return:
    """
    if classification == 'robertson':
        return df.assign(colour=df.apply(lambda row: colours_robertson[row['soil_type']], axis=1)), 'Robertson'
    elif classification == 'been_jeffrey':
        return df.assign(colour=df.apply(lambda row: colours_been_jeffrey[row['soil_type']], axis=1)), \
               'Been Jeffrey'


def add_plot_classification(fig, df, depth_max, depth_min, title, num_col):
    """
    Add to the plot the selected classification.
    :param fig: Original figure.
    :param depth_max: Maximum depth.
    :param depth_min: Minimum depth.
    :return:
    """
    plot_classify = fig.add_subplot(1, num_col, 3)
    df = df.copy()
    df['soil_type'].loc[df['soil_type'].isna()] = 'UNKNOWN'
    for st in np.unique(df['soil_type']):
        partial_df = df[df['soil_type'] == st]
        plt.hlines(y=partial_df['depth'], xmin=0, xmax=1, colors=partial_df['colour'], label=st)
    plot_classify.set_xlabel('-')
    plot_classify.set_ylabel('Z (m)')
    plot_classify.set_title(f'{title} classification')
    plt.ylim(depth_max, depth_min)
    plt.legend(loc='best', fontsize='xx-small')
    return fig


def add_grouped_classification(fig, df_group, depth_max, depth_min, title_group, num_col):
    """
    Add to the plot the selected classification.
    :param fig: Original figure.
    :param depth_max: Maximum depth.
    :param depth_min: Minimum depth.
    :return: Complete figure.
    """
    plot_classify = fig.add_subplot(1, num_col, 4)
    df = df_group
    for i, layer in enumerate(df['soil_type']):
        plt.barh(y=df['z_centr'][i], height=df['thickness'][i], width=5,
                 color=df['colour'][i], label=layer)
    plot_classify.set_xlabel('-')
    plot_classify.set_ylabel('Z (m)')
    plot_classify.set_title(f'{title_group} classification')
    plt.ylim(depth_max, depth_min)
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='best', fontsize='xx-small')
    return fig


def plot_merged_cpt_bore(df, figsize=(11, 8), show=True):
    fig = plt.figure(figsize=figsize)
    subplot_val = 131
    plt.subplot(subplot_val)
    plt.plot(df['qc'], -df['depth'])

    subplot_val += 1
    plt.subplot(subplot_val)
    plt.plot(df['friction_number'], -df['depth'])

    subplot_val += 1
    plt.subplot(subplot_val)
    if 'SI' in df.columns:
        df = df.copy()
        df['L'] += df['SI']
    v = df[['G', 'S', 'L', 'C', 'P']].values

    c = ['#578E57', '#a76b29', '#0078C1', '#DBAD4B', '#708090']
    for i in range(5):
        plt.fill_betweenx(-df['depth'], np.zeros(v.shape[0]), np.cumsum(v, axis=1)[:, -(i + 1)], color=c[i])

    if show:
        plt.show()
    return fig


def plot_bore(df, figsize=(11, 8), show=True):
    fig = plt.figure(figsize=figsize)

    v = df[['G', 'S', 'L', 'C', 'P']].values
    v[:, 2] += df['SI'].values
    c = ['#578E57', '#a76b29', '#0078C1', '#DBAD4B', '#708090']

    for i in range(5):
        plt.fill_betweenx(-np.repeat(df['depth_top'], 2), np.zeros(v.shape[0] * 2),
                          np.roll(np.repeat(np.cumsum(v, axis=1)[:, -(i + 1)], 2), 1), color=c[i])
    if show:
        plt.show()
    return fig


