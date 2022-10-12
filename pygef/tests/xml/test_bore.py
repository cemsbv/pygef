import pytest

from pygef import broxml
from pygef.broxml import Location
from datetime import date
import polars as pl


def test_bore_attributes(bore_xml_v2: str) -> None:
    parsed = broxml.read_bore(bore_xml_v2)
    assert len(parsed) == 1

    bore_data = parsed[0]
    assert bore_data.research_report_date == date(2021, 10, 19)
    assert bore_data.delivered_location == Location(
        "urn:ogc:def:crs:EPSG::28992", x=158322.139, y=444864.706
    )
    assert bore_data.description_procedure == "ISO14688d1v2019c2020"
    assert bore_data.delivered_vertical_position_offset == 10.773
    assert bore_data.delivered_vertical_position_datum == "nap"
    assert bore_data.delivered_vertical_position_reference_point == "maaiveld"
    assert not bore_data.bore_rock_reached
    assert bore_data.final_bore_depth == 12.0
    assert bore_data.final_sample_depth == 12.0
    assert bore_data.bore_hole_completed

    expected = pl.DataFrame(
        {
            "upper_boundary": [
                0.0,
                1.0,
                1.1,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
            ],
            "lower_boundary": [
                1.0,
                1.1,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
            ],
            "geotechnical_soil_name": [
                "zwakGrindigZand",
                "zwakGrindigZand",
                "zwakZandigeKleiMetGrind",
                "zwakZandigeKlei",
                "zwakZandigeKlei",
                "zwakZandigeKlei",
                "zwakZandigeKlei",
                "zwakZandigeKlei",
                "siltigZand",
                "siltigZand",
                "siltigZand",
                "siltigZandMetGrind",
                "siltigZandMetGrind",
            ],
            "color": [
                "donkergrijs",
                "donkergrijs",
                "standaardBruin",
                "standaardGrijs",
                "donkergrijs",
                "standaardBruin",
                "standaardBruin",
                "lichtbruin",
                "lichtgrijs",
                "standaardGrijs",
                "standaardGrijs",
                "standaardGrijs",
                "standaardGrijs",
            ],
            "dispersed_inhomogenity": [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "organic_matter_content_class": [
                "nietOrganisch",
                "nietOrganisch",
                "nietOrganisch",
                "nietOrganisch",
                "nietOrganisch",
                "nietOrganisch",
                "nietOrganisch",
                "nietOrganisch",
                "zwakOrganisch",
                "nietOrganisch",
                "nietOrganisch",
                "nietOrganisch",
                "nietOrganisch",
            ],
            "sand_median_class": [
                "middelgrof420tot630um",
                "middelgrof420tot630um",
                None,
                None,
                None,
                None,
                None,
                None,
                "fijn150tot200um",
                "fijn150tot200um",
                "fijn150tot200um",
                "middelgrof200tot300um",
                "middelgrof300tot420um",
            ],
        }
    )
    assert bore_data.data.frame_equal(expected, null_equal=True)


def test_bore_version(bore_xml_v1) -> None:
    with pytest.raises(ValueError, match="only bhrgtcom/2.x is supported"):
        broxml.read_bore(bore_xml_v1)
