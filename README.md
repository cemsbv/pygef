# PYGEF

Simple parser for *.gef files. These are ASCII based files used for soil measurements.

## Installation
`$ pip install git+https://github.com/ritchie46/pygef.git`

```python
for pygef import ParseCPT, ParseBRO

gef = ParseCPT("./my-gef-file.cpt")
print(gef.df)


# save to csv
gef.df.to_csv("my-file.csv")
```
