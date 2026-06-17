# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is pygef

pygef is a Python library that parses soil measurement data from two file formats:
- **GEF files** (`.gef`) — a Dutch legacy human-readable data format
- **BRO XML files** (`.xml`) — the modern Dutch BRO (Basisregistratie Ondergrond) format

It exposes two public functions: `read_cpt()` for cone penetration test data and `read_bore()` for borehole data. Both return frozen dataclasses (`CPTData`, `BoreData`) with measurement data stored as Polars DataFrames.

## Commands

Install for development:
```bash
pip install -r requirements.txt
pip install -e .[test,plot,map]
```

Run tests:
```bash
coverage run -m pytest
pytest tests/gef/test_gef.py  # single test file
pytest -k "test_name"         # single test by name
```

Format code:
```bash
black --config "pyproject.toml" .
isort --settings-path "pyproject.toml" .
```

Type check:
```bash
mypy src/pygef
```

Build docs:
```bash
sphinx-build -b html docs public
```

## Architecture

```
src/pygef/
  shim.py          # Entry point: read_cpt() and read_bore() dispatch to gef or xml parsers
  cpt.py           # CPTData frozen dataclass + post-processing (frictionRatio, depthOffset)
  bore.py          # BoreData frozen dataclass
  common.py        # Shared: Location, VerticalDatumClass enum, coordinate helpers
  plotting.py      # Optional: plot_cpt() and plot_bore() (requires matplotlib)
  gef/             # GEF file parser
    gef.py         # Low-level GEF header/column parsing
    parse_cpt.py   # _GefCpt: maps GEF columns to internal representation
    parse_bore.py  # _GefBore: maps GEF columns to internal representation
    mapping.py     # Column name mappings from GEF MEASUREMENTVAR codes
  broxml/          # BRO XML parser
    xml_parser.py  # lxml-based XML parsing
    parse_cpt.py   # read_cpt() returns list of CPTData
    parse_bore.py  # read_bore() returns list of BoreData
    mapping.py     # Maps BRO XML parameter names to DataFrame column names
    resolvers.py   # Value resolvers (unit conversions, void handling)
```

**Data flow:** `shim.read_cpt(file)` → `_classify_input()` returns `(kind, format, payload)` → dispatches to `_GefCpt` (GEF) or `read_cpt_xml` (XML). GEF parser `ValueError`s are wrapped into `ParseGefError`.

**Input classification** (`_classify_input` in `shim.py`): `io.BytesIO` and `pathlib.Path` are routed by sniffing the first ~128 bytes (`#KEY=` → GEF, `<` → XML). A `str` is GEF content if it starts with `#KEY=`, XML content if it starts with `<`, an existing filesystem path if `os.path.exists()` returns True, and otherwise unparseable (`ValueError`). A missing `pathlib.Path` raises `FileNotFoundError`; a missing `str` does not — it falls through to the same `ValueError`. When `engine` is `"gef"` or `"xml"`, it must match the detected format or `ValueError` is raised.

**Key design notes:**
- `CPTData.__post_init__` runs post-processing on the DataFrame (computes `frictionRatioComputed`, `depthOffset`, sorts by `penetrationLength`). Because the dataclass is frozen, it uses `object.__setattr__` to replace `data`.
- XML files can contain multiple measurements; `index` parameter selects which one.
- `replace_column_voids` and `remove_pre_excavated_rows` are GEF-only options passed through `read_cpt()`.
- Coordinates use Dutch RD New (EPSG:28992) for GEF files; BRO XML may include WGS84 standardized locations.
- The `src/` layout requires `pythonpath = ["src"]` in pytest config (already set in `pyproject.toml`).

## Test structure

- `tests/gef/` — GEF file parsing tests
- `tests/xml/` — BRO XML parsing tests  
- `tests/test_files/` — sample `.gef` files; XML fixtures in subdirectories
- `tests/test_shim.py` — integration tests for the public API
