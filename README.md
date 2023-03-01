# PYGEF

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPi Version](https://img.shields.io/pypi/v/pygef.svg)](https://pypi.org/project/pygef)
[![GitHub stars](https://img.shields.io/github/stars/ritchie46/pygef.svg?logo=github&label=Stars&logoColor=white)](https://github.com/ritchie46/pygef)
[![Coverage Status](https://coveralls.io/repos/github/ritchie46/pygef/badge.svg?branch=master)](https://coveralls.io/github/ritchie46/pygef?branch=code-coverage)

Simple parser for \*.gef files. These are ASCII based files used for soil properties measurements.
Compatible with Python 3.9.

Recently added the parsing of xml boreholes file, the xml parsing is still in a preliminary phase,
not all the files are supported. If you find a file that doesn't work with pygef, please make an issue about it or PR :)

## Installation

Latest stable version:

`$ pip install pygef`

Cutting-edge version (might break):

`$ pip install git+https://github.com/cemsbv/pygef.git`

## CPT files

```python
>> > from pygef import read_cpt
>> >  # read gef and xml files
>> > cpt_data = read_cpt("./my-cpt.xml")
>> > cpt_data
CPTData: {'bro_id': 'CPT000000099543',
          'cone_diameter': 44,
          'cone_surface_area': 1500,
          'cone_surface_quotient': 0.67,
          'cone_to_friction_sleeve_distance': 100,
          'cone_to_friction_sleeve_surface_area': 22530,
          'cone_to_friction_sleeve_surface_quotient': 1.0,
          ...
              'zlm_pore_pressure_u3_after': None,
'zlm_pore_pressure_u3_before': None}
>> >  # access the underlying polars DataFrame under the `data` attribute
>> > cpt_data.data.head()
shape: (5, 9)
┌────────────┬───────┬───────────┬────────────┬─────┬────────────┬────────────┬────────────┬────────────┐
│ penetratio ┆ depth ┆ elapsedTi ┆ coneResist ┆ ... ┆ inclinatio ┆ inclinatio ┆ localFrict ┆ frictionRa │
│ nLength    ┆ ---   ┆ me        ┆ ance       ┆     ┆ nNS        ┆ nResultant ┆ ion        ┆ tio        │
│ ---        ┆ f64   ┆ ---       ┆ ---        ┆     ┆ ---        ┆ ---        ┆ ---        ┆ ---        │
│ f64        ┆       ┆ f64       ┆ f64        ┆     ┆ i64        ┆ i64        ┆ f64        ┆ f64        │
╞════════════╪═══════╪═══════════╪════════════╪═════╪════════════╪════════════╪════════════╪════════════╡
│ 0.0        ┆ 0.0   ┆ -9.99999
e ┆ -9.99999e5 ┆ ... ┆ -999999    ┆ -999999    ┆ -9.99999e5 ┆ -9.99999e5 │
│            ┆       ┆ 5         ┆            ┆     ┆            ┆            ┆            ┆            │
├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 0.02       ┆ 0.02  ┆ 11.0      ┆ 2.708      ┆ ... ┆ 0          ┆ 0          ┆ 0.03       ┆ 0.6        │
├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 0.04       ┆ 0.039 ┆ 13.0      ┆ 4.29       ┆ ... ┆ 0          ┆ 0          ┆ 0.039      ┆ 0.8        │
├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 0.06       ┆ 0.059 ┆ 15.0      ┆ 5.124      ┆ ... ┆ 0          ┆ 0          ┆ 0.045      ┆ 0.9        │
├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 0.08       ┆ 0.079 ┆ 17.0      ┆ 5.45       ┆ ... ┆ 0          ┆ 0          ┆ 0.049      ┆ 1.0        │
└────────────┴───────┴───────────┴────────────┴─────┴────────────┴────────────┴────────────┴────────────┘
```

## Bore files

```python
>> > from pygef import read_bore
>> >  # read gef and xml files
>> > bore_data = read_bore("./my-bore.xml")
>> > bore_data
BoreData: {'bore_hole_completed': True,
           'bore_rock_reached': False,
           'data': (13, 8),
           'delivered_location': Location(srs_name='urn:ogc:def:crs:EPSG::28992', x=158322.139, y=444864.706),
           'delivered_vertical_position_datum': 'nap',
           'delivered_vertical_position_offset': 10.773,
           'delivered_vertical_position_reference_point': 'maaiveld',
           'description_procedure': 'ISO14688d1v2019c2020',
           'final_bore_depth': 12.0,
           'final_sample_depth': 12.0,
           'research_report_date': datetime.date(2021, 10, 19)}
>> >  # access the underlying polars DataFrame under the `data` attribute
>> > bore_data.data.head()
shape: (5, 8)
┌────────────┬────────────┬────────────┬──────────┬────────────┬────────────┬────────────┬─────────┐
│ upper_boun ┆ lower_boun ┆ geotechnic ┆ color    ┆ dispersed_ ┆ organic_ma ┆ sand_media ┆ soil_di │
│ dary       ┆ dary       ┆ al_soil_na ┆ ---      ┆ inhomogeni ┆ tter_conte ┆ n_class    ┆ st      │
│ ---        ┆ ---        ┆ me         ┆ str      ┆ ty         ┆ nt_class   ┆ ---        ┆ ---     │
│ f64        ┆ f64        ┆ ---        ┆          ┆ ---        ┆ ---        ┆ str        ┆ list[f6 │
│            ┆            ┆ str        ┆          ┆ bool       ┆ str        ┆            ┆ 4]      │
╞════════════╪════════════╪════════════╪══════════╪════════════╪════════════╪════════════╪═════════╡
│ 0.0        ┆ 1.0        ┆ zwakGrindi ┆ donkergr ┆ false      ┆ nietOrgani ┆ middelgrof ┆ [0.2,   │
│            ┆            ┆ gZand      ┆ ijs      ┆            ┆ sch        ┆ 420
tot630u ┆ 0.0,    │
│            ┆            ┆            ┆          ┆            ┆            ┆ m          ┆ ...     │
│            ┆            ┆            ┆          ┆            ┆            ┆            ┆ 0.0]    │
├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌┤
│ 1.0        ┆ 1.1        ┆ zwakGrindi ┆ donkergr ┆ false      ┆ nietOrgani ┆ middelgrof ┆ [0.2,   │
│            ┆            ┆ gZand      ┆ ijs      ┆            ┆ sch        ┆ 420
tot630u ┆ 0.0,    │
│            ┆            ┆            ┆          ┆            ┆            ┆ m          ┆ ...     │
│            ┆            ┆            ┆          ┆            ┆            ┆            ┆ 0.0]    │
├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌┤
│ 1.1        ┆ 2.0        ┆ zwakZandig ┆ standaar ┆ false      ┆ nietOrgani ┆ null       ┆ [0.0,   │
│            ┆            ┆ eKleiMetGr ┆ dBruin   ┆            ┆ sch        ┆            ┆ 0.1,    │
│            ┆            ┆ ind        ┆          ┆            ┆            ┆            ┆ ...     │
│            ┆            ┆            ┆          ┆            ┆            ┆            ┆ 0.0]    │
├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌┤
│ 2.0        ┆ 3.0        ┆ zwakZandig ┆ standaar ┆ false      ┆ nietOrgani ┆ null       ┆ [0.0,   │
│            ┆            ┆ eKlei      ┆ dGrijs   ┆            ┆ sch        ┆            ┆ 0.0,    │
│            ┆            ┆            ┆          ┆            ┆            ┆            ┆ ...     │
│            ┆            ┆            ┆          ┆            ┆            ┆            ┆ 0.0]    │
├╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌┤
│ 3.0        ┆ 4.0        ┆ zwakZandig ┆ donkergr ┆ false      ┆ nietOrgani ┆ null       ┆ [0.0,   │
│            ┆            ┆ eKlei      ┆ ijs      ┆            ┆ sch        ┆            ┆ 0.0,    │
│            ┆            ┆            ┆          ┆            ┆            ┆            ┆ ...     │
│            ┆            ┆            ┆          ┆            ┆            ┆            ┆ 0.0]    │
└────────────┴────────────┴────────────┴──────────┴────────────┴────────────┴────────────┴─────────┘

```

## Plotting

```python
from pygef import read_cpt, read_bore
from pygef.plotting import plot_cpt, plot_bore

# plot cpt file
plot_cpt(read_cpt("myfile.xml"))

# plot a bore file
plot_bore(read_bore("myfile.xml"))
```

## Documentation

Build the docs:

```bash
python -m pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install .

sphinx-build -b html docs public
```

## Format

We format our code with black and isort.

```bash
black --config "pyproject.toml" .
isort --settings-path "pyproject.toml" .
```

## Lint

To maintain code quality we use the GitHub super-linter.

To run the linters locally, run the following bash script from the root directory:

```bash
docker run \
--env RUN_LOCAL=true \
--env VALIDATE_JSCPD=false \
--env VALIDATE_CSS=false \
--env VALIDATE_BASH=false \
--env VALIDATE_YAML=false \
--env VALIDATE_PYTHON_PYLINT=false \
--env VALIDATE_NATURAL_LANGUAGE=false \
--env VALIDATE_MARKDOWN=false \
--env LINTER_RULES_PATH=/ \
--env PYTHON_BLACK_CONFIG_FILE=pyproject.toml \
--env PYTHON_ISORT_CONFIG_FILE=pyproject.toml \
--env PYTHON_MYPY_CONFIG_FILE=pyproject.toml \
--env PYTHON_FLAKE8_CONFIG_FILE=.flake8 \
-v $(pwd):/tmp/lint github/super-linter:v4
```

## UnitTest

Test the software with the use of coverage:

```bash
python -m pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install .

coverage run -m unittest
```

## Requirements

Requirements are autogenerated by `pip-compile` with python 3.9

```bash
pip-compile --extra=test --extra=docs --extra=lint --output-file=requirements.txt pyproject.toml
```