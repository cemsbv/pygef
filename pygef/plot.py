from pygef.group_classification import GroupClassification
from pygef.gef import ParseCPT
import os
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Button, Slider
from bokeh.io import show
import pandas as pd

path = "/home/martina/Documents/gef_files/2016/16428/16428_S-WEG-038A-P_000.GEF"
classification = GroupClassification("/home/martina/Documents/gef_files/2016/16428/16428_S-WEG-038A-P_000.GEF")
gef = ParseCPT(path)
cpt = gef.df
group = classification.df_soil_grouped
colours = {'Peat': 'darkred',
           'Clays - silty clay to clay': 'indianred',
           'Silt mixtures - clayey silt to silty clay': 'peru',
           'Sand mixtures - silty sand to sandy silt': 'goldenrod',
           'Sands - clean sand to silty sand': 'sandybrown',
           'Gravelly sand to dense sand': 'navajowhite'
           }

group['colour'] = group.apply(lambda row: colours[row.layer], axis=1)

s1 = ColumnDataSource(group)
s2 = ColumnDataSource(cpt)
p = figure(x_axis_label='qc / fs (kPa)', y_axis_label='Z(m)', title="title",
           tools='pan,wheel_zoom,box_zoom,reset,box_select, xwheel_zoom,undo,redo', active_scroll='xwheel_zoom',
           plot_width=1000, plot_height=1000)
#p.line(x='qc', y='depth', source=s2)
p.line(x='fs', y='depth', source=s2)

show(p)
