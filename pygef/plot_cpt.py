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


class PlotCPT:
    def __init__(self, df, df_group, classification):
        self.classification = classification
        self.df, self.title = self.assign_color(df, classification)
        df_group = df_group.copy()
        df_group = df_group.rename(columns={'layer': 'soil_type'})
        self.df_group, self.title_group = self.assign_color(df_group, classification)
        self.title_group = 'Filtered'

    def plot_cpt(self, show=True, figsize=(16, 30)):
        """
        Main fuction to plot qc, Fr and soil classification.
        :param show: If show is True the figure is shown.
        :param figsize: Figure size (x, y) , x i the width y is the height.
        :return:
        """
        depth_max = self.df['depth'].max()
        depth_min = self.df['depth'].min()
        fig = plt.figure(figsize=figsize)
        n = 0
        for c, unit in zip(['qc', 'Fr'], ['[MPa]', '[%]']):
            n += 1
            fig_i = fig.add_subplot(1, 4, n)
            plt.plot(self.df[c], self.df['depth'], 'b')
            fig_i.set_xlabel(f'{c} {unit}')
            fig_i.set_ylabel('Z [m]')
            plt.grid()
            fig_i.set_xticks(np.arange(0, self.df[c].max() + 2, 2))
            fig_i.xaxis.set_tick_params(labeltop='on')
            plt.ylim(depth_max, depth_min)

        fig = self.add_plot_classification(fig, depth_max, depth_min)
        fig = self.add_grouped_classification(fig, depth_max, depth_min)

        if show:
            plt.show()
        else:
            return fig

    @staticmethod
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

    def add_plot_classification(self, fig, depth_max, depth_min):
        """
        Add to the plot the selected classification.
        :param fig: Original figure.
        :param depth_max: Maximum depth.
        :param depth_min: Minimum depth.
        :return:
        """

        plot_classify = fig.add_subplot(1, 4, 3)
        df = self.df.copy()
        df['soil_type'].loc[df['soil_type'].isna()] = 'UNKNOWN'
        for st in np.unique(df['soil_type']):
            partial_df = df[df['soil_type'] == st]
            plt.hlines(y=partial_df['depth'], xmin=0, xmax=1, colors=partial_df['colour'], label=st)

        plot_classify.set_xlabel('-')
        plot_classify.set_ylabel('Z (m)')
        plot_classify.set_title(f'{self.title} classification')
        plt.ylim(depth_max, depth_min)
        plt.legend(loc='best', fontsize='xx-small')
        return fig

    def add_grouped_classification(self, fig, depth_max, depth_min):
        """
        Add to the plot the selected classification.
        :param fig: Original figure.
        :param depth_max: Maximum depth.
        :param depth_min: Minimum depth.
        :return: Complete figure.
        """

        plot_classify = fig.add_subplot(1, 4, 4)
        df = self.df_group
        for i, layer in enumerate(df['soil_type']):
            plt.barh(y=df['z_centr'][i], height=df['thickness'][i], width=5,
                     color=df['colour'][i], label=layer)

        plot_classify.set_xlabel('-')
        plot_classify.set_ylabel('Z (m)')
        plot_classify.set_title(f'{self.title_group} classification')
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



