# PYGEF

Simple parser for *.gef files. These are ASCII based files used for soil properties measurements. 

## Installation
`$ pip install pygef`

`$ pip install git+https://github.com/ritchie46/pygef.git`

## Usage
```python
from pygef.gef import ParseGEF

# Read *.gef file
gef = ParseGEF("./my-gef-file.gef")
print(gef)

# Pandas dataframe is accessible via the `df` attribute
print(gef.df)

# Save to csv
gef.df.to_csv("my-file.csv")

# Some important attributes are the follows:

attributes= [
gef.zid, # height with respect to NAP
gef.type, # type of the gef file (borehole or cpt)
gef.x, # x coordinate with respect to the reference system
gef.y # y coordinate with respect to the reference system
]

# Plot cpt file and get soil classification
gef.plot(classification='robertson', water_level_NAP= -1, min_thickness= 0.2, show=True) # the plot in figure

classification = ['robertson',been_jefferies]

# Type the name of the classification exactly as specified in the list classification, the inputs of plot_cpt are:
kwargs = [classification='robertson', been_jefferies
          water_level_NAP= -1, # insert water level respect to NAP
          min_thickness = 0.2, # minimun accepted thickness for filtered layers
          p_a=0.1, # atmospheric pressure, used in the new Robertson, default: 0.1 Mpa
          new=True, # set new to use the new Robertson classification, default: New
          show=False, # set show=True to shown the plot, default: False
          figsize=(12, 30), # set the desired figure size, default: (12, 30)
          df_group=None, # if you want to plot a different filtered dataframe use this key argument
          do_gouping=True]  
          
# Save the complete dataframe with classification to csv file
classified = gef.classify_robertson(water_level_NAP, new=True, p_a=0.1)

# or Been&Jeffrey
classified = gef.classify_been_jeffrey(water_level_NAP)    
                       
classified.df.to_csv("my_classified_cpt.csv")   

# Save the filtered Dataframe 

filtered = gef.group_classification(0.2, 'robertson', -1, True, 0.1)

args = [
min_thickness, # min thickness accepted for the layers, it is suggested not use a value bigger than 0.2 m.
classification, # Chosen soil classification
water_level_NAP # Water level with respect to NAP (my field)

]

filtered.df.to_csv("my_filtered_cpt.csv")   

# Plot only qc and Fr:
gef.plot(classification=None, water_level_NAP=None, min_thickness=None, p_a=0.1, new=True, show=True,
                 figsize=(8, 30), df_group=None, do_grouping=True)
                 
# Plot qc, Fr and classification
gef.plot(classification='robertson', water_level_NAP=-1, min_thickness=None, p_a=0.1, new=True, show=True,
         figsize=(12, 30), df_group=None, do_grouping=False)
         
# Plot qc, Fr, classification and filtered classification 
gef.plot(classification='robertson', water_level_NAP=-1, min_thickness=0.2, p_a=0.1, new=True, show=True,
                 figsize=(16, 30), df_group=None, do_grouping=True)                          
       
```

![](img/gef_classified_grouped.png)

