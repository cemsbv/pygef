import matplotlib.pyplot as plt


class PlotCPT:
    def __init__(self, df):
        self.df = df

    def plot_cpt(self, show=True, figsize=(8, 30)):
        depth_max = self.df['depth'].max()
        depth_min = self.df['depth'].min()
        fig = plt.figure(figsize=figsize)

        n = 0
        for c, unit in zip(['qc', 'Fr'], ['[MPa]', '[%]']):
            n += 1
            qc = fig.add_subplot(1, 2, n)
            plt.plot(self.df[c], self.df['depth'], 'b')
            qc.set_xlabel(f'{c} {unit}')
            qc.set_ylabel('Z [m]')
            plt.grid()
            plt.ylim(depth_max, depth_min)

        if show:
            return plt.show()
        return fig




