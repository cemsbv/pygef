from pygef.group_classification import GroupClassification
from pygef.gef import ParseCPT
import os
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Button, Slider, ColorBar, LinearColorMapper
from bokeh.io import show
import pandas as pd
from bokeh.layouts import column, row


path = "/home/martina/Documents/gef_files/2016/16428/16428_S-WEG-038A-P_000.GEF"
classification = GroupClassification("/home/martina/Documents/gef_files/2016/16428/16428_S-WEG-038A-P_000.GEF")
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

group['colour'] = group.apply(lambda row: colours[row.layer], axis=1)
cpt['colour'] = cpt.apply(lambda row: colours[row.soil_type_Robertson], axis=1)

s1 = ColumnDataSource(group)
s2 = ColumnDataSource(cpt)

number_layers = len(group['z_in'])
height = cpt['depth'][1]-cpt['depth'][0]
depth_max = cpt['depth'].max()
depth_min = cpt['depth'].min()

qc = figure(x_axis_label='qc (MPa)', y_axis_label='Z(m)', title="qc",
           tools='pan,wheel_zoom,box_zoom,reset,box_select,xwheel_zoom,undo,redo', active_scroll='xwheel_zoom',
           plot_width=500, plot_height=1000, y_range=(depth_max, depth_min))
fs = figure(x_axis_label='fs (MPa)', y_axis_label='Z(m)', title="fs",
           tools='pan,wheel_zoom,box_zoom,reset,box_select,xwheel_zoom,undo,redo', active_scroll='xwheel_zoom',
           plot_width=500, plot_height=1000, y_range=(depth_max, depth_min))
robertson_classification = figure(x_axis_label='-', y_axis_label='Z(m)', title="Robertson classification",
           tools='pan,wheel_zoom,box_zoom,reset,box_select,xwheel_zoom,undo,redo', active_scroll='xwheel_zoom',
           plot_width=500, plot_height=1000, y_range=(depth_max, depth_min))
qc.line(x='qc', y='depth', source=s2)
fs.line(x='fs', y='depth', source=s2)

robertson_classification.hbar(y=cpt['depth'], height=height, left=0, right=50, color=cpt['colour'])
color_mapper = LinearColorMapper(palette=['darkred', 'indianred', 'peru', 'goldenrod', 'sandybrown', 'navajowhite'],
                                tags=['Peat', 'Clays - silty clay to clay', 'Silt mixtures - clayey silt to silty clay',
                                                'Sand mixtures - silty sand to sandy silt', 'Sands - clean sand to silty sand', 'Gravelly sand to dense sand'])
color_bar = ColorBar(color_mapper=color_mapper)
robertson_classification.add_layout(color_bar, 'right')
layout = row(qc, fs, robertson_classification)

show(layout)
