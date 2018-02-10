# PYGEF

Simple parser for *.gef files. These are ASCII based files used for soil measurements.
gita
```
for pygef import ParseCPT, ParseBRO

gef = ParseCPT("./my-gef-file.cpt")
print(gef.df)
```