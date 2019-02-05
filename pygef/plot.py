from pygef.group_classification import GroupClassification
from pygef.gef import ParseCPT
import os
import matplotlib.pyplot as plt
from collections import OrderedDict


class Plot:
    def __init__(self, path):
        self.path = path

    def read_plot(self, num_folder):
        if num_folder == 2:
            for folder in os.listdir(self.path):
                for file_name in os.listdir(self.path + folder + '/'):
                    if file_name.endswith((".GEF", ".gef")):
                        path = self.path + folder + '/' + file_name
                        self.plot_cpt(path)
        else:
            self.plot_cpt(self.path)

    @staticmethod
    def plot_cpt(path):
        classification = GroupClassification(path)
        gef = ParseCPT(path)
        cpt = gef.classify_robertson().df_complete
        group = classification.df_soil_grouped
        filter_group = classification.df_soil_grouped_final
        colours = {'Peat': '#578E57',
                   'Clays - silty clay to clay': '#a76b29',
                   'Silt mixtures - clayey silt to silty clay': '#0078C1',
                   'Sand mixtures - silty sand to sandy silt': '#DBAD4B',
                   'Sands - clean sand to silty sand': 'gold',
                   'Gravelly sand to dense sand': '#708090'
                   }
        cpt['colour'] = cpt.apply(lambda row: colours[row.soil_type_Robertson], axis=1)
        group['colour'] = group.apply(lambda row: colours[row.layer], axis=1)
        filter_group['colour'] = filter_group.apply(lambda row: colours[row.final_layers], axis=1)
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

        rob = fig.add_subplot(1, 4, 3)
        for i in range(len(group['z_centr'])):
            plt.barh(y=group['z_centr'][i], height=group['layer_thickness'][i], width=5,
                     color=group['colour'][i], label=group['layer'][i])
        rob.set_xlabel('-')
        rob.set_ylabel('Z (m)')
        rob.set_title("Robertson classification")
        plt.ylim(depth_max, depth_min)
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc='best', fontsize='xx-small')

        rob2 = fig.add_subplot(1, 4, 4)
        for i in range(len(filter_group['z_centr'])):
            plt.barh(y=filter_group['z_centr'][i], height=filter_group['final_layer_thickness'][i], width=5,
                     color=filter_group['colour'][i], label=filter_group['final_layers'][i])
        rob2.set_xlabel('-')
        rob2.set_ylabel('Z (m)')
        rob2.set_title("Filtered")
        plt.ylim(depth_max, depth_min)
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc='best', fontsize='xx-small')
        return plt.show()




