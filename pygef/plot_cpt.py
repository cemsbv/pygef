import matplotlib.pyplot as plt
from collections import OrderedDict

colours_robertson = {'Peat': '#578E57',
                     'Clays - silty clay to clay': '#a76b29',
                     'Silt mixtures - clayey silt to silty clay': '#0078C1',
                     'Sand mixtures - silty sand to sandy silt': '#DBAD4B',
                     'Sands - clean sand to silty sand': 'gold',
                     'Gravelly sand to dense sand': '#708090',
                     None: 'black'
                     }

colours_been_jeffrey = {'Peat': '#578E57',
                        'Clays': '#a76b29',
                        'Clayey silt to silty clay': '#0078C1',
                        'Silty sand to sandy silt': '#DBAD4B',
                        'Sands: clean sand to silty': 'gold',
                        'Gravelly sands': '#708090',
                        None: 'black'
                        }


class PlotCPT:
    def __init__(self, df, classification):
        self.classification = classification
        self.df = self.assign_color(df, classification)

    def plot_cpt(self, show=True, figsize=(12, 30)):
        depth_max = self.df['depth'].max()
        depth_min = self.df['depth'].min()
        fig = plt.figure(figsize=figsize)
        n = 0
        for c, unit in zip(['qc', 'Fr'], ['[MPa]', '[%]']):
            n += 1
            fig_i = fig.add_subplot(1, 3, n)
            plt.plot(self.df[c], self.df['depth'], 'b')
            fig_i.set_xlabel(f'{c} {unit}')
            fig_i.set_ylabel('Z [m]')
            plt.grid()
            plt.ylim(depth_max, depth_min)

        plot_classify = fig.add_subplot(1, 3, 3)
        for i in range(len(self.df['depth'])):
            plt.barh(y=self.df['depth'][i], height=-self.df['delta_depth'][i], width=5,
                     color=self.df['colour'][i], label=self.df['soil_type'][i], align='edge')
        plot_classify.set_xlabel('-')
        plot_classify.set_ylabel('Z (m)')
        plot_classify.set_title(f'{self.classification} classification')
        plt.ylim(depth_max, depth_min)
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc='best', fontsize='xx-small')

        if show:
            return plt.show()
        return fig

    @staticmethod
    def assign_color(df, classification):
        if classification == 'robertson':
            return df.assign(colour=df.apply(lambda row: colours_robertson[row['soil_type']], axis=1))
        elif classification == 'been_jeffrey':
            return df.assign(colour=df.apply(lambda row: colours_been_jeffrey[row['soil_type']], axis=1))


