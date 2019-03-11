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
gef.plot_cpt('robertson', -1, 0.2, show=True) # the plot in figure

classification = ['robertson','been_jeffrey']

#type the name of the classification exactly as specified in the list classification, the inputs of plot_cpt are:
args = ['classification name', water_level_NAP, min_thickness] 
kwargs = [p_a=0.1, # atmosferic pressure, used in the new Robertson, default: 0.1 Mpa
          new=True, # set new to use the new Robertson classification, default: New
          show=False, # set show=True to shown the plot, default: False
          figsize=(12, 30)] # set the desired figure size, default: (12, 30)
          
# Save the complete dataframe with classification to csv file
classified = gef.classify_robertson(water_level_NAP, new=True, p_a=0.1)
# or Been&Jeffrey
classified = gef.classify_been_jeffrey(water_level_NAP)    
                       
classified.df.to_csv("my_classified_cpt.csv")   

# Save the filtered Dataframe 

filtered = gef.group_classification(0.2, 'robertson', -1, True, 0.1)

args = [
min_thickness, # min thickness accepted for the layers, it is suggested to not use a value bigger the 0.2 m.
classification, # Chosen soil classification
water_level_NAP # Water level respect to NAP (my field)
]

filtered.df.to_csv("my_filtered_cpt.csv")   
       
```

![](img/gef_classified_grouped.png)

