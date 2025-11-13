from datetime import datetime

import pytest
from lxml.etree import XMLSyntaxError

from pygef import read_cpt
from pygef.common import Location, VerticalDatumClass
from pygef.cpt import CPTData


def test_engine(cpt_gef_1) -> None:
    # read test with force incorrect engine
    with pytest.raises(XMLSyntaxError):
        read_cpt(cpt_gef_1, engine="xml")
    # read test with force engine
    gef = read_cpt(cpt_gef_1, engine="gef")
    isinstance(gef, CPTData)
    # read test with auto engine
    gef = read_cpt(cpt_gef_1, engine="auto")
    isinstance(gef, CPTData)


@pytest.mark.parametrize("_type", ["string", "path", "byte"])
def test_gef_to_cpt_data(_type, cpt_gef_1, cpt_gef_1_bytes, cpt_gef_1_string) -> None:
    _format = {
        "string": cpt_gef_1_string,
        "path": cpt_gef_1,
        "byte": cpt_gef_1_bytes,
    }

    cpt_data = read_cpt(_format[_type])

    assert cpt_data.attributes() == {
        "bro_id": None,
        "alias": "CPTU17.8 + 83BITE",
        "cone_diameter": None,
        "cone_surface_area": 1000.0,
        "cone_surface_quotient": 0.8,
        "cone_to_friction_sleeve_distance": 80.0,
        "cone_to_friction_sleeve_surface_area": None,
        "cone_to_friction_sleeve_surface_quotient": 1.0,
        "cpt_description": "",
        "cpt_standard": None,
        "groundwater_level": None,
        "cpt_type": 4.0,
        "data": (999, 12),
        "column_void_mapping": {
            "coneResistance": -999999.0,
            "correctedConeResistance": -999999.0,
            "depth": -999999.0,
            "frictionRatio": -999999.0,
            "inclinationEW": -999999.0,
            "inclinationNS": -999999.0,
            "inclinationResultant": -999999.0,
            "localFriction": -999999.0,
            "penetrationLength": -9999.0,
            "porePressureU2": -999999.0,
        },
        "delivered_vertical_position_datum": VerticalDatumClass("31000"),
        "delivered_vertical_position_offset": -0.09,
        "delivered_vertical_position_reference_point": "unknown",
        "dissipationtest_performed": None,
        "final_depth": 20.0,
        "predrilled_depth": 0.0,
        "quality_class": int(2),
        "research_report_date": datetime(2019, 2, 13).date(),
        "standardized_location": None,
        "delivered_location": Location(
            srs_name="urn:ogc:def:crs:EPSG::28992", x=79578.38, y=424838.97
        ),
        "zlm_cone_resistance_after": -0.245,
        "zlm_cone_resistance_before": -0.257,
        "zlm_inclination_ew_after": None,
        "zlm_inclination_ew_before": None,
        "zlm_inclination_ns_after": None,
        "zlm_inclination_ns_before": None,
        "zlm_inclination_resultant_after": None,
        "zlm_inclination_resultant_before": None,
        "zlm_local_friction_after": -0.016,
        "zlm_local_friction_before": -0.015,
        "zlm_pore_pressure_u1_after": None,
        "zlm_pore_pressure_u1_before": None,
        "zlm_pore_pressure_u2_after": -0.013,
        "zlm_pore_pressure_u2_before": -0.028,
        "zlm_pore_pressure_u3_after": None,
        "zlm_pore_pressure_u3_before": None,
        "raw_headers": {
            "COLUMN": [["10"]],
            "COLUMNINFO": [
                ["1", "m", "Sondeerlengte", "1"],
                ["2", "MPa", "Conusweerstand", "2"],
                ["3", "MPa", "Gecorrigeerde conusweerstand", "13"],
                ["4", "MPa", "Plaatselijke wrijving", "3"],
                ["5", "%", "Wrijvingsgetal", "4"],
                ["6", "MPa", "Waterspanning u2", "6"],
                ["7", "Graden", "Helling", "8"],
                ["8", "Graden", "Helling O-W", "10"],
                ["9", "Graden", "Helling N-Z", "9"],
                ["10", "m", "Gecorrigeerde diepte", "11"],
            ],
            "COLUMNSEPARATOR": [[";"]],
            "COLUMNVOID": [
                ["2", "-999999"],
                ["3", "-999999"],
                ["4", "-999999"],
                ["5", "-999999"],
                ["6", "-999999"],
                ["7", "-999999"],
                ["8", "-999999"],
                ["9", "-999999"],
                ["10", "-999999"],
            ],
            "COMMENT": [
                ["================================="],
                ["Geconverteerde sondering uit MRSV"],
                ["Mos Grondmechanica B.V."],
                ["Datum: 13-feb-2019 - 11:21"],
                ["================================="],
            ],
            "COMPANYID": [["Mos Grondmechanica B.V", "24257098", "31"]],
            "DATAFORMAT": [["ASCII"]],
            "EOH": [[]],
            "FILEDATE": [["2019", "02", "13"]],
            "FILEOWNER": [["SR1"]],
            "GEFID": [["1", "1", "0"]],
            "LASTSCAN": [["1004"]],
            "MEASUREMENTTEXT": [
                ["4", "S10-CFIIP.1721", "conus type en serienummer"],
                ["5", "Sondeerrups 1; 12400 kg; geen ankers", "sondeerequipment"],
                [
                    "6",
                    "NEN-EN-ISO22476-1 / klasse 2 / TE2",
                    "gehanteerde norm en klasse en type sondering",
                ],
                ["9", "maaiveld", "vast horizontaal vlak"],
                ["20", "nee", "signaalbewerking uitgevoerd"],
                ["21", "nee", "bewerking onderbrekingen uitgevoerd"],
                ["42", "MRG1", "methode verticale positiebepaling"],
                ["43", "LRG1", "methode locatiebepaling"],
                ["101", "Bronhouder", "52605825", "31"],
                ["102", "opdracht publieke taakuitvoering", "kader aanlevering"],
                ["103", "overig onderzoek", "kader inwinning"],
                ["104", "uitvoerder locatiebepaling", "24257098", "31"],
                ["105", "2019", "01", "29"],
                ["106", "uitvoerder verticale positiebepaling", "24257098", "31"],
                ["107", "2019", "01", "29"],
                ["109", "nee", "dissipatietest uitgevoerd"],
                ["110", "ja", "expertcorrectie uitgevoerd"],
                ["111", "nee", "aanvullend onderzoek uitgevoerd"],
                ["112", "2019", "01", "31"],
                ["113", "2019", "01", "30"],
                ["114", "2019", "01", "29"],
            ],
            "MEASUREMENTVAR": [
                ["1", "1000", "mm2", "nom. oppervlak conuspunt"],
                ["2", "15000", "mm2", "oppervlakte kleefmantel"],
                ["3", "0.80", "-", "netto oppervlakte cofficint van de conuspunt"],
                ["4", "1.0", "-", "oppervlaktequotint kleefmantel"],
                ["5", "80", "mm", "afstand tussen conuspunt en hart kleefmantel"],
                ["8", "1", "-", "Waterspanningsopnemer u2 aanwezig"],
                ["12", "4", "-", "sondeermethode"],
                ["13", "0", "m", "voorgeboorde/voorgegraven diepte"],
                ["16", "20.00", "m", "einddiepte sondering"],
                ["17", "0", "-", "Stopcriterium: Einddiepte bereikt"],
                ["20", "-0.257", "MPa", "Nulpunt conus voor de sondering"],
                ["21", "-0.245", "MPa", "Nulpunt conus na de sondering"],
                ["22", "-0.015", "MPa", "Nulpunt kleef voor de sondering"],
                ["23", "-0.016", "MPa", "Nulpunt kleef na de sondering"],
                ["26", "-0.028", "MPa", "Nulpunt waterspanning voor de sondering"],
                ["27", "-0.013", "MPa", "Nulpunt waterspaning na de sondering"],
            ],
            "PROJECTID": [["CPT", "1801726"]],
            "PROJECTNAME": [["Traject 20-3 Voorne Putten"]],
            "RECORDSEPARATOR": [["!"]],
            "REPORTCODE": [["GEF-CPT-Report", "1", "1", "2", "gefcr112.pdf"]],
            "REPORTTEXT": [
                ["201", "Mos Grondmechanica B.V."],
                ["202", "Traject 20-3 Voorne Putten te Voorne Putten"],
                ["203", "Sondering CPTU17.8 + 83BITE"],
            ],
            "STARTDATE": [["2019", "01", "29"]],
            "STARTTIME": [["10", "43", "50"]],
            "TESTID": [["CPTU17.8 + 83BITE"]],
            "XYID": [["31000", "79578.38", "424838.97", "0.02", "0.02"]],
            "ZID": [["31000", "-0.09", "0.05"]],
        },
    }
