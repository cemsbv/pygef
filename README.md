# PYGEF

Simple parser for *.gef files. These are ASCII based files used for soil properties measurements. 

## Installation
`$ pip install pygef`

`$ pip install git+https://github.com/ritchie46/pygef.git`

## Usage
```python
from pygef.gef import ParseGEF

# read *.gef file
gef = ParseGEF("./my-gef-file.gef")
print(gef)

# Pandas dataframe is accessible via the `df` attribute
print(gef.df)

# save to csv
gef.df.to_csv("my-file.csv")

# plot cpt file
gef.plot_cpt()

# Some important attributes are the following:
attributes= [
gef.zid, # height with respect to NAP
gef.type, # type of the gef file (borehole or cpt)
gef.x, # x coordinate with respect to the reference system
gef.y # y coordinate with respect to the reference system
]

```

![](img/gef-only_.png)

