from pygef.group_classification import GroupClassification
from pygef.gef import ParseCPT
import os
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper
from bokeh.io import show
from bokeh.layouts import row
import matplotlib.pyplot as plt
import numpy as np

def scan_folder(parent):
    # iterate over all the files and directories in the directory 'parent'
    for folder in os.listdir(parent):
        for file_name in os.listdir(parent + folder + '/'):
            if file_name.endswith((".GEF", ".gef")):
                path = parent + folder + '/' + file_name
                classification = GroupClassification(path)
                gef = ParseCPT(path)
                print(file_name)
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
                s1 = ColumnDataSource(group)
                s2 = ColumnDataSource(cpt)


                depth_max = cpt['depth'].max()
                depth_min = cpt['depth'].min()

                qc = figure(x_axis_label='qc (MPa)', y_axis_label='Z(m)', title="qc",
                           tools='pan,wheel_zoom,box_zoom,reset,box_select,xwheel_zoom,undo,redo', active_scroll='xwheel_zoom',
                           plot_width=500, plot_height=1000, y_range=(depth_max, depth_min))
                fs = figure(x_axis_label='fs (MPa)', y_axis_label='Z(m)', title="fs",
                           tools='pan,wheel_zoom,box_zoom,reset,box_select,xwheel_zoom,undo,redo', active_scroll='xwheel_zoom',
                           plot_width=500, plot_height=1000, y_range=(depth_max, depth_min))
                robertson_classification = figure(x_axis_label='-', y_axis_label='Z(m)', title="Robertson classification: {0}".format(file_name),
                           tools='pan,wheel_zoom,box_zoom,reset,box_select,xwheel_zoom,undo,redo', active_scroll='xwheel_zoom',
                           plot_width=500, plot_height=1000, y_range=(depth_max, depth_min))
                qc.line(x='qc', y='depth', source=s2)
                fs.line(x='fs', y='depth', source=s2)

                robertson_classification.hbar(y=group['z_centr'], height=group['layer_thickness'], left=0, right=50, color=group['colour'])
                color_mapper = LinearColorMapper(palette=['darkred', 'indianred', 'peru', 'goldenrod', 'sandybrown', 'navajowhite'])
                color_bar = ColorBar(color_mapper=color_mapper, location=(0,0), title='Legend', label_standoff=12)
                robertson_classification.add_layout(color_bar, 'right')
                layout = row(qc, fs, robertson_classification)

                show(layout)

#scan_folder("/home/martina/Documents/gef_files/2016/")
path = "/home/martina/Documents/gef_files/2016/16428/16428_S-WEG-038A-P_000.GEF"

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
fs.set_xlabel('-')
fs.set_ylabel('Z (m)')
plt.ylim(depth_max, depth_min)

plt.show()


