import matplotlib.pyplot as plt


class PlotCPT:
    def __init__(self, df):
        self.df = df

    def plot_cpt(self, show=True):
        depth_max = self.df['depth'].max()
        depth_min = self.df['depth'].min()
        fig = plt.figure(figsize=(15, 30))

        qc = fig.add_subplot(1, 4, 1)  # Plot qc
        plt.plot(self.df['qc'], self.df['depth'], 'b')
        qc.set_xlabel('qc (MPa)')
        qc.set_ylabel('Z (m)')
        plt.ylim(depth_max, depth_min)

        Fr = fig.add_subplot(1, 4, 2)
        plt.plot(self.df['Fr'], self.df['depth'], 'b')
        Fr.set_xlabel('Fr (%)')
        Fr.set_ylabel('Z (m)')
        plt.ylim(depth_max, depth_min)
        if show:
            return plt.show()
        return fig




