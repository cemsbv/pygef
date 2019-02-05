from pygef.group_classification import GroupClassification
from pygef.gef import ParseCPT
import os
import matplotlib.pyplot as plt
from collections import OrderedDict


def scan_folder(parent):
    # iterate over all the files and directories in the directory 'parent'
    for folder in os.listdir(parent):
        for file_name in os.listdir(parent + folder + '/'):
            if file_name.endswith((".GEF", ".gef")):
                path = parent + folder + '/' + file_name
                classification = GroupClassification(path)
                gef = ParseCPT(path)

                cpt = gef.classify_robertson().df_complete
                group = classification.df_soil_grouped
                colours = {'Peat': 'darkred',
                           'Clays - silty clay to clay': 'indianred',
                           'Silt mixtures - clayey silt to silty clay': 'peru',
                           'Sand mixtures - silty sand to sandy silt': 'goldenrod',
                           'Sands - clean sand to silty sand': 'sandybrown',
                           'Gravelly sand to dense sand': 'navajowhite'
                           }

                cpt['colour'] = cpt.apply(lambda row: colours[row.soil_type_Robertson], axis=1)
                group['colour'] = group.apply(lambda row: colours[row.layer], axis=1)

                depth_max = cpt['depth'].max()
                depth_min = cpt['depth'].min()

                fig = plt.figure(1, figsize=(15, 30))

                qc = fig.add_subplot(1, 3, 1)
                plt.plot(cpt['qc'], cpt['depth'], 'b')
                qc.set_xlabel('qc (MPa)')
                qc.set_ylabel('Z (m)')
                plt.ylim(depth_max, depth_min)

                fs = fig.add_subplot(1, 3, 2)
                plt.plot(cpt['fs'], cpt['depth'], 'b')
                fs.set_xlabel('fs (MPa)')
                fs.set_ylabel('Z (m)')
                plt.ylim(depth_max, depth_min)

                rob = fig.add_subplot(1, 3, 3)
                for i in range(len(group['z_centr'])):
                    plt.barh(y=group['z_centr'][i], height=group['layer_thickness'][i], width=5,
                             color=group['colour'][i], label=group['layer'][i])
                rob.set_xlabel('-')
                rob.set_ylabel('Z (m)')
                plt.ylim(depth_max, depth_min)

                handles, labels = plt.gca().get_legend_handles_labels()
                by_label = OrderedDict(zip(labels, handles))
                plt.legend(by_label.values(), by_label.keys(), loc='upper right')

                plt.show()

#scan_folder("/home/martina/Documents/gef_files/2016/")

path = "/home/martina/Documents/gef_files/2016/16428/16428_S-WEG-038A-P_000.GEF"

classification = GroupClassification(path)
gef = ParseCPT(path)

cpt = gef.classify_robertson().df_complete
group = classification.df_soil_grouped
filter_group = classification.df_soil_grouped_final
colours = {'Peat': 'darkred',
           'Clays - silty clay to clay': 'indianred',
           'Silt mixtures - clayey silt to silty clay': 'peru',
           'Sand mixtures - silty sand to sandy silt': 'goldenrod',
           'Sands - clean sand to silty sand': 'sandybrown',
           'Gravelly sand to dense sand': 'navajowhite'
           }

cpt['colour'] = cpt.apply(lambda row: colours[row.soil_type_Robertson], axis=1)
group['colour'] = group.apply(lambda row: colours[row.layer], axis=1)
filter_group['colour'] = filter_group.apply(lambda row: colours[row.final_layers], axis=1)

depth_max = cpt['depth'].max()
depth_min = cpt['depth'].min()

fig = plt.figure(1, figsize=(15, 30))

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
  plt.barh(y=group['z_centr'][i], height=group['layer_thickness'][i], width=5, color=group['colour'][i], label=group['layer'][i])
rob.set_xlabel('-')
rob.set_ylabel('Z (m)')
plt.ylim(depth_max, depth_min)

handles, labels = plt.gca().get_legend_handles_labels()
by_label = OrderedDict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='upper right')

rob = fig.add_subplot(1, 4, 4)
for i in range(len(filter_group['z_centr'])):
  plt.barh(y=filter_group['z_centr'][i], height=filter_group['final_layer_thickness'][i], width=5, color=filter_group['colour'][i], label=filter_group['final_layers'][i])
rob.set_xlabel('-')
rob.set_ylabel('Z (m)')
plt.ylim(depth_max, depth_min)

handles, labels = plt.gca().get_legend_handles_labels()
by_label = OrderedDict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='upper right')

plt.show()


