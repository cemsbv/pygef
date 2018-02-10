# PYGEF

Simple parser for *.gef files. These are ASCII based files used for soil measurements.

```python
for pygef import ParseCPT, ParseBRO

gef = ParseCPT("./my-gef-file.cpt")
print(gef.df)


# save to excel
gef.df.to_excel("my-excel-file.xlsx")
```