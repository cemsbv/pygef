from io import BytesIO
from pathlib import Path

import polars as pl
import pytest
from lxml import etree

from pygef import read_cpt

TEST_FILES = Path(__file__).parent / "test_files"


@pytest.fixture
def cpt_xml_removed_layers() -> str:
    return str(TEST_FILES / "cpt_xml" / "CPT000000123320.xml")


def test_gef_removed_layers():
    cpt = read_cpt(TEST_FILES / "cpt_pre_excavated.gef")

    assert cpt.predrilled_depth == 1.5
    assert cpt.removed_layers.to_dicts() == [
        {
            "sequence_number": 1,
            "upper_boundary": 0.0,
            "vertical_unit": "m",
            "description": "Klei",
        },
        {
            "sequence_number": 2,
            "upper_boundary": 1.1,
            "vertical_unit": "m",
            "description": "Zand",
        },
    ]
    assert "lower_boundary" not in cpt.removed_layers.columns


def test_gef_removed_layers_variable_fields(cpt_gef_1, caplog):
    source = Path(cpt_gef_1).read_text(encoding="utf-8", errors="ignore")
    source = source.replace(
        "#EOH=",
        "#SPECIMENVAR= 1, 0, m, Klei\\, zandig\\, puin\n"
        "#SPECIMENVAR= 2, 1.2, m, Zand, extra, kleur\n"
        "#SPECIMENVAR= 3, 1.5, m\n"
        "#EOH=",
        1,
    )

    cpt = read_cpt(source, engine="gef")

    assert cpt.removed_layers["description"].to_list() == [
        "Klei, zandig, puin",
        "Zand",
        None,
    ]
    assert cpt.removed_layers["extra_1"].to_list() == [None, "extra", None]
    assert cpt.removed_layers["extra_2"].to_list() == [None, "kleur", None]
    assert "SPECIMENVAR" in caplog.text


def test_gef_removed_layers_invalid_values_are_preserved(cpt_gef_1, caplog):
    source = Path(cpt_gef_1).read_text(encoding="utf-8", errors="ignore")
    source = source.replace(
        "#EOH=",
        "#SPECIMENVAR= ongeldig, niet-een-getal, cm, Klei\n#EOH=",
        1,
    )

    cpt = read_cpt(source, engine="gef")

    assert cpt.removed_layers.to_dicts() == [
        {
            "sequence_number": None,
            "sequence_number_raw": "ongeldig",
            "upper_boundary": None,
            "upper_boundary_raw": "niet-een-getal",
            "vertical_unit": "cm",
            "description": "Klei",
        }
    ]
    assert "SPECIMENVAR" in caplog.text


def test_gef_removed_layers_incomplete_and_inconsistent(cpt_gef_1, caplog):
    source = Path(cpt_gef_1).read_text(encoding="utf-8", errors="ignore")
    source = source.replace(
        "#EOH=",
        "#SPECIMENVAR= 1, 0, m, Klei\n"
        "#SPECIMENVAR= 2, 0, m, Zand\n"
        "#SPECIMENVAR= 3\n"
        "#EOH=",
        1,
    )

    cpt = read_cpt(source, engine="gef")

    assert cpt.removed_layers.shape == (3, 4)
    assert cpt.removed_layers["upper_boundary"].to_list() == [0.0, 0.0, None]
    assert "Incomplete SPECIMENVAR" in caplog.text
    assert "Inconsistent SPECIMENVAR" in caplog.text
    assert "missing or invalid predrilled depth" in caplog.text


@pytest.mark.parametrize(
    "path",
    sorted(
        path
        for path in TEST_FILES.glob("cpt*.gef")
        if path.name != "cpt_pre_excavated.gef"
    ),
    ids=lambda path: path.name,
)
def test_gef_without_removed_layers(path):
    cpt = read_cpt(path)

    assert cpt.removed_layers.is_empty()


def test_xml_removed_layers():
    cpt = read_cpt(TEST_FILES / "cpt_xml" / "CPT000000123320.xml")

    assert isinstance(cpt.removed_layers, pl.DataFrame)
    assert cpt.removed_layers.to_dicts() == [
        {
            "sequence_number": 1,
            "upper_boundary": 0.0,
            "lower_boundary": 0.12,
            "description": "Verharding Asfalt",
        },
        {
            "sequence_number": 2,
            "upper_boundary": 0.12,
            "lower_boundary": 0.35,
            "description": "Verharding Stabilisatielaag",
        },
        {
            "sequence_number": 3,
            "upper_boundary": 0.35,
            "lower_boundary": 1.7,
            "description": "Zand",
        },
        {
            "sequence_number": 4,
            "upper_boundary": 1.7,
            "lower_boundary": 2.0,
            "description": "Klei",
        },
    ]


@pytest.mark.parametrize(
    "path",
    sorted(
        path
        for path in (TEST_FILES / "cpt_xml").glob("*.xml")
        if path.name != "CPT000000123320.xml"
    ),
    ids=lambda path: path.name,
)
def test_xml_without_removed_layers(path):
    cpt = read_cpt(path)

    assert cpt.removed_layers.is_empty()


@pytest.mark.parametrize(
    ("xml_name", "field"),
    [
        ("sequenceNumber", "sequence_number"),
        ("upperBoundary", "upper_boundary"),
        ("lowerBoundary", "lower_boundary"),
        ("description", "description"),
    ],
)
def test_cpt_removed_layer_without_field_is_preserved(
    cpt_xml_removed_layers: str, xml_name: str, field: str
) -> None:
    tree = etree.parse(cpt_xml_removed_layers)
    namespaces = {"cptcommon": "http://www.broservices.nl/xsd/cptcommon/1.1"}
    layer = tree.find(".//cptcommon:removedLayer", namespaces=namespaces)
    assert layer is not None
    element = layer.find(f"cptcommon:{xml_name}", namespaces=namespaces)
    assert element is not None
    layer.remove(element)

    parsed = read_cpt(BytesIO(etree.tostring(tree)))

    assert parsed.removed_layers.shape == (4, 4)
    assert parsed.removed_layers[field][0] is None
    assert parsed.removed_layers[field][1] is not None


def test_cpt_removed_layer_without_any_fields(cpt_xml_removed_layers: str) -> None:
    tree = etree.parse(cpt_xml_removed_layers)
    namespaces = {"cptcommon": "http://www.broservices.nl/xsd/cptcommon/1.1"}
    layer = tree.find(".//cptcommon:removedLayer", namespaces=namespaces)
    assert layer is not None
    for element in list(layer):
        layer.remove(element)

    parsed = read_cpt(BytesIO(etree.tostring(tree)))

    assert parsed.removed_layers.row(0) == (None, None, None, None)


def test_cpt_removed_layer_with_empty_field(cpt_xml_removed_layers: str) -> None:
    tree = etree.parse(cpt_xml_removed_layers)
    namespaces = {"cptcommon": "http://www.broservices.nl/xsd/cptcommon/1.1"}
    upper = tree.find(
        ".//cptcommon:removedLayer/cptcommon:upperBoundary", namespaces=namespaces
    )
    assert upper is not None
    upper.text = None

    parsed = read_cpt(BytesIO(etree.tostring(tree)))

    assert "upper_boundary" in parsed.removed_layers.columns
    assert parsed.removed_layers["upper_boundary"][0] is None
    assert parsed.removed_layers.schema["upper_boundary"] == pl.Float64


def test_cpt_removed_layer_field_absent_from_all_layers(
    cpt_xml_removed_layers: str,
) -> None:
    tree = etree.parse(cpt_xml_removed_layers)
    namespaces = {"cptcommon": "http://www.broservices.nl/xsd/cptcommon/1.1"}
    for layer in tree.findall(".//cptcommon:removedLayer", namespaces=namespaces):
        description = layer.find("cptcommon:description", namespaces=namespaces)
        assert description is not None
        layer.remove(description)

    parsed = read_cpt(BytesIO(etree.tostring(tree)))

    assert parsed.removed_layers.shape == (4, 3)
    assert "description" not in parsed.removed_layers.columns


def test_cpt_removed_layers_without_any_fields(cpt_xml_removed_layers: str) -> None:
    tree = etree.parse(cpt_xml_removed_layers)
    namespaces = {"cptcommon": "http://www.broservices.nl/xsd/cptcommon/1.1"}
    for layer in tree.findall(".//cptcommon:removedLayer", namespaces=namespaces):
        for element in list(layer):
            layer.remove(element)

    parsed = read_cpt(BytesIO(etree.tostring(tree)))

    assert parsed.removed_layers.shape == (4, 0)
