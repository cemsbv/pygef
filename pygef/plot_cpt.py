from pygef.gef import ParseCPT
import matplotlib.pyplot as plt
from collections import OrderedDict


class PlotCPT:
    def __init__(self, path):
        self.path = path

    @staticmethod
    def plot_cpt(path):
        gef = ParseCPT(path)
        cpt = gef.classify_robertson().df_complete

        depth_max = cpt['depth'].max()
        depth_min = cpt['depth'].min()
        fig = plt.figure(path, figsize=(15, 30))

        qc = fig.add_subplot(1, 4, 1)
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




