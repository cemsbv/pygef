from pygef.group_classification import GroupClassification
import os

gef = GroupClassification("/home/martina/Documents/gef_files/2016/16428/16428_S-WEG-038A-P_000.GEF")
group = gef.df_soil_grouped
colours = {'Peat': 1,
           'Clays - silty clay to clay': 2,
           'Silt mixtures - clayey silt to silty clay': 3,
           'Sand mixtures - silty sand to sandy silt': 4,
           'Sands - clean sand to silty sand': 5,
           'Gravelly sand to dense sand': 6
           }
print(group)