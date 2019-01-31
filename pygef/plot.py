from pygef.gef import ParseCPT
import os

gef = ParseCPT("/home/martina/Documents/gef_files/2016/16428/16428_S-WEG-038A-P_000.GEF")
rob = gef.classify_robertson().df_complete
print(rob)