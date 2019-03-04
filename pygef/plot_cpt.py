import matplotlib.pyplot as plt
from pygef.gef import ParseGEF


class PlotCPT:
    def __init__(self, df, classification, water_level_NAP, p_a, new=True):
        area_quotient_cone_tip = ParseGEF.area_quotient_cone_tip
        pre_excavated_depth = ParseGEF.pre_excavated_depth

        self.df = df.assign(self.classify_soil, classification, water_level_NAP,
                            area_quotient_cone_tip, pre_excavated_depth, p_a, new=new)
    @staticmethod
    def classify_soil(classification, water_level_NAP, area_quotient_cone_tip, pre_excavated_depth, p_a,
                      new=True):
        if classification == 'robertson':
            return ParseGEF.classify_robertson(water_level_NAP, new, area_quotient_cone_tip=area_quotient_cone_tip,
                                               pre_excavated_depth=pre_excavated_depth, p_a=p_a)
        elif classification == 'been_jeffrey':
            return ParseGEF.classify_been_jeffrey(water_level_NAP, area_quotient_cone_tip=area_quotient_cone_tip,
                                               pre_excavated_depth=pre_excavated_depth)

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


