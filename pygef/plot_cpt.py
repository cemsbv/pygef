import matplotlib.pyplot as plt


class PlotCPT:
    def __init__(self, gef):
        self.gef = gef

    def plot_cpt(self):
        cpt = self.gef.classify_robertson().df_complete

        depth_max = cpt['depth'].max()
        depth_min = cpt['depth'].min()
        fig = plt.figure(figsize=(15, 30))

        qc = fig.add_subplot(1, 4, 1)  # Plot qc
        plt.plot(cpt['qc'], cpt['depth'], 'b')
        qc.set_xlabel('qc (MPa)')
        qc.set_ylabel('Z (m)')
        plt.ylim(depth_max, depth_min)

        fs = fig.add_subplot(1, 4, 2)
        plt.plot(cpt['fs'], cpt['depth'], 'b')
        fs.set_xlabel('fs (MPa)')
        fs.set_ylabel('Z (m)')
        plt.ylim(depth_max, depth_min)
        return plt.show()




