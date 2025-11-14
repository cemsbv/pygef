# Changelog

All notable changes to this project will be documented in this file.

## [0.14.0] - 2025-11-14

### Bug Fixes

- *Deps*:
    - Pin test dependencies
    - Update all dependencies

### Documentation
- *Readme*: Remove incorrect information

### Features
- *Excavation*: Option to discard or retain "pre excavated" range measurements (#451)
- *Gef*: Surface all headers into CPTData structure (#449)
- *Python*: Support Python 3.14

### Miscellaneous Tasks
- *Lint*: Disable zizmor GitHub actions check

- *Python*:
    - Use 3.13 Python consistently
    -  [**BREAKING**]Drop support for Python 3.9 & 3.10
- *Repo*: Delete empty file

### Testing
- Drop test where basemap is added to figure

## [0.13.0] - 2025-10-13

### Bug Fixes
- *Linter*: Disable many unused / conflicting linters
- *Parsing*: Add missing height_system values

### Features
- *Parsing*: Make replace columnvoids optional (#441)

### Styling
- *Super-linter*: Exclude VALIDATE_MARKDOWN_PRETTIER

## [0.12.1] - 2025-07-22

### Features
- *Parser*: Parse coordinate system code to gml (#433)

## [0.12.0] - 2025-07-22

### Bug Fixes

- *Deps*:
    - Apply fix from gef-file-to-map not parsing empty array values in headers (#432)
    - Update all non-major dependencies (#412)

### Miscellaneous Tasks
- *Ci*: Move from dependabot to renovate

### Refactor
- *Plot*:  [**BREAKING**]Put `[plot]` behind a feature flag (#406)

## [0.11.1] - 2025-04-08

### Bug Fixes

- *Deps*:
    - Pin dependencies and update linting dependencies
    - Update all dependencies (#405)

### Documentation
- *Readme*: Use correct test command in README.md

## [0.11.0] - 2024-09-23

### Features
- *Cpt_class*: Remove cpt-class validation

### Miscellaneous Tasks
- *Lint*: Fix linting

## [0.10.2] - 2024-08-16

### Performance
- Resolve polars performance warning

## [0.10.1] - 2024-01-03

### Bug Fixes
- *Ci*: Use proper authentication in release pipeline
- Resolve pkg_resources deprecation warning
- Resolve polars deprecation warning

### Features
- *Xml*: Dont resolve entities when parsing xml

### Miscellaneous Tasks
- Use coveralls github-action

### Build
- Create binary wheel and a source tarball

## [0.10.0] - 2023-10-19

### Bug Fixes
- [**BREAKING**] Make sure that penetrationLength is positive (#357)

### Miscellaneous Tasks
- [**BREAKING**] Update xpath and add exception (#358)

## [0.9.0] - 2023-10-09

### Bug Fixes
- Resolve #354 update xpath

### Miscellaneous Tasks
- Release 0.9.0

## [0.8.4] - 2023-10-02

### Features
- Add class zero to QualityClass (#355)

### Miscellaneous Tasks
- Release 0.8.4

## [0.8.3] - 2023-09-15

### Miscellaneous Tasks
- Release 0.8.3
- Add datetime from gef to shim
- Update typing offset_to_depth and depth_to_offset (#339)

## [0.8.2] - 2023-06-08

### Bug Fixes
- Overwrite dtypes to Float64 (#330)

### Miscellaneous Tasks
- *Ci*: Add python version matrix in test job (#331)
- Release 0.8.2 (#332)

## [0.8.1] - 2023-06-02

### Bug Fixes
- *Ci*: Use trusted publishing for PyPi
- *Deps*: Add upper-bounds to dependency specifications (#304)
- Use separator in polars.read_csv (#310)
- Sort dataframe (#307)
- Update plotting (#309)

### Features
- *Plot*: Set the locator of the major ticker (#311)

## [0.8.0] - 2023-03-15

### Bug Fixes
- *Naming*: Standardize casing (#297)
- *Parsing*: Provide parsing engine (#298)

### Documentation
- Add attributes to docstring (#295)

### Features
- Update soil distribution (#300)
- Add groundwater level property to cpt (#296)

### Miscellaneous Tasks
- Release 0.8.0

## [0.8.0-alpha.5] - 2023-03-07

### Bug Fixes

- *CI*:
    - Install pytest
    - Install pygef

- *Ci*:
    - Trigger release on every tag (#293)
    - Release to pypi trigger

### Chore
- Add linting, rm old GEF functions, update docs
- Add linting, rm old GEF functions, update docs

### Features
- Support for NEN5104, update GEF properties (#294)

### Miscellaneous Tasks
- *Dependencies*: Update dependencies

- *Pytest*:
    - Use pytest for all test, omit tests in cov report
    - Use pytest for all test, omit tests in cov report

## [0.8.0-alpha.4] - 2023-03-02

### Bug Fixes
- *Doc*: Sphinx documentation references

### Miscellaneous Tasks
- Add linting, rm old GEF functions, update docs (#290)

## [0.8.0-alpha.3] - 2023-02-27

### Refactor
- Move to a src-based file structure

## [0.8.0-alpha.2] - 2023-02-27

### Bug Fixes
- *Build*: Setuptools was missing packages

## [0.8.0-alpha] - 2023-02-24

### Bug Fixes

- *Ci*:
    - License fix & description in pyproject.toml
    - Upload to pypi step
    - Release to pypi

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
