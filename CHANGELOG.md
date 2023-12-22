# Changelog

All notable changes to this project will be documented in this file.

## [0.10.1] - 2023-12-22

### Features

- *(xml)* Dont resolve entities when parsing xml

### Bug Fixes

- Resolve pkg_resources deprecation warning
- Resolve polars deprecation warning

### Miscellaneous Tasks

- Use coveralls github-action

### Build

- Create binary wheel and a source tarball

## [0.10.0] - 2023-10-19

### Miscellaneous Tasks

- [**breaking**] Update xpath and add exception (#358)

### Bug Fixes

- [**breaking**] Make sure that penetrationLength is positive (#357)

## [0.9.0] - 2023-10-09

### Miscellaneous Tasks

- Release 0.9.0

### Bug Fixes

- Resolve #354 update xpath

## [0.8.4] - 2023-10-02

### Miscellaneous Tasks

- Release 0.8.4

### Features

- Add class zero to QualityClass (#355)

## [0.8.3] - 2023-09-15

### Miscellaneous Tasks

- Release 0.8.3
- Add datetime from gef to shim
- Update typing offset_to_depth and depth_to_offset (#339)

## [0.8.2] - 2023-06-08

### Miscellaneous Tasks

- Release 0.8.2 (#332)
- *(ci)* Add python version matrix in test job (#331)

### Bug Fixes

- Overwrite dtypes to Float64 (#330)

## [0.8.1] - 2023-06-02

### Bug Fixes

- *(ci)* Use trusted publishing for PyPi
- Use separator in polars.read_csv (#310)
- Sort dataframe (#307)
- Update plotting (#309)
- *(deps)* Add upper-bounds to dependency specifications (#304)

### Features

- *(plot)* Set the locator of the major ticker (#311)

## [0.8.0] - 2023-03-15

### Miscellaneous Tasks

- Release 0.8.0

### Features

- Update soil distribution (#300)
- Add groundwater level property to cpt (#296)

### Bug Fixes

- *(parsing)* Provide parsing engine (#298)
- *(naming)* Standardize casing (#297)

### Documentation

- Add attributes to docstring (#295)

## [0.8.0-alpha.5] - 2023-03-07

### Bug Fixes

- *(ci)* Trigger release on every tag (#293)
- *(ci)* Release to pypi trigger

### Features

- Support for NEN5104, update GEF properties (#294)

### Miscellaneous Tasks

- *(dependencies)* Update dependencies
- *(pytest)* Use pytest for all test, omit tests in cov report
- *(pytest)* Use pytest for all test, omit tests in cov report

### Chore

- Add linting, rm old GEF functions, update docs

## [0.8.0-alpha.4] - 2023-03-02

### Miscellaneous Tasks

- Add linting, rm old GEF functions, update docs (#290)

### Bug Fixes

- *(CI)* Install pytest
- *(CI)* Install pygef
- *(doc)* Sphinx documentation references

### Chore

- Add linting, rm old GEF functions, update docs

## [0.8.0-alpha.3] - 2023-02-27

### Refactor

- Move to a src-based file structure

## [0.8.0-alpha.2] - 2023-02-27

### Bug Fixes

- *(build)* Setuptools was missing packages

## [0.8.0-alpha] - 2023-02-24

### Bug Fixes

- *(ci)* License fix & description in pyproject.toml
- *(ci)* Upload to pypi step
- *(ci)* Release to pypi

### Miscellaneous Tasks

- Release 0.8.0-alpha as 0.8.0a0 on pypi
- Don't automatically release from master (#244)
- Set strict mypy rules (#213)

### Refactor

- Move gef-file-to-map to it's own repo
- Parsing the xml generic (#246)
- Init broxml test and strict mypy (#245)
- Lot's of refactoring (#235)

### Testing

- Move tests to dedicated folder (#243)

## [0.7.4] - 2022-08-01

### Fix

- Find columns_number by counting columns instead of taking maximum value of column numbers

## [0.4.1] - 2021-06-01

### DeprecationWarning

- The 'warn' method is deprecated, use 'warning' instead

<!-- CEMS BV. -->
