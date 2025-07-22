# flake8: noqa: E501 line too long (182 > 180 characters)
from __future__ import annotations

import os.path
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import polars.testing as pl_test
import pytest

import pygef.gef.utils as utils
from pygef import common, exceptions, plotting, read_bore, read_cpt
from pygef.gef.gef import parse_all_columns_info, replace_column_void
from pygef.gef.mapping import MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT
from pygef.gef.parse_bore import _GefBore
from pygef.gef.parse_cpt import _GefCpt, correct_pre_excavated_depth

BasePath = os.path.dirname(__file__)


@pytest.mark.parametrize(
    "filename",
    [
        "example.gef",
        "cpt.gef",
        "cpt.gef",
        "cpt2.gef",
        "cpt3.gef",
        "cpt4.gef",
        "cpt_class_high.gef",
    ],
)
def test_cpt_smoke(filename):
    """
    Smoke test to see if no errors occur during creation of the Cpt object for valid
    CPTs.
    """

    gef = read_cpt(os.path.join(BasePath, "../test_files/", filename))

    axes = plotting.plot_cpt(gef)
    assert isinstance(axes[0], plt.Axes)

    pl_test.assert_series_equal(
        gef.data.get_column("penetrationLength"),
        gef.data.get_column("penetrationLength").abs(),
    )


def test_bore_smoke():
    """
    Smoke test to see if no errors occur during creation of the Bore object for valid
    Bore files.
    """
    gef = read_bore(os.path.join(BasePath, "../test_files/example_bore.gef"))
    axes = plotting.plot_bore(gef)
    assert isinstance(axes, plt.Axes)


def test_bore_cpt_smoke():
    """
    Smoke test to see if no errors occur during creation of the Bore object for valid
    Bore files.
    """
    gef1 = read_bore(os.path.join(BasePath, "../test_files/example_bore.gef"))
    gef2 = read_cpt(os.path.join(BasePath, "../test_files/cpt.gef"))
    fig, axes = plotting.plot_merge(gef1, gef2)
    assert isinstance(axes[0], plt.Axes)


def test_xy():
    cpt3 = read_cpt(os.path.join(BasePath, "../test_files/cpt3.gef"))
    np.testing.assert_almost_equal(cpt3.delivered_location.x, 110885)
    np.testing.assert_almost_equal(cpt3.delivered_location.y, 493345)
    assert cpt3.delivered_location.srs_name == "urn:ogc:def:crs:EPSG::28992"


def test_measurement_var_with_minus_sign():
    s = r"#MEASUREMENTVAR= 41, -15.000000, "
    v = utils.parse_measurement_var_as_float(s, 41)
    np.testing.assert_almost_equal(v, -15)

    h = {"MEASUREMENTVAR": [["41", "-15.000000"]]}
    v = utils.parse_measurement_var_as_float(h, 41)
    np.testing.assert_almost_equal(v, -15)


def test_measurement_var_without_minus_sign():
    s = r"#MEASUREMENTVAR= 41, 15.000000, "
    v = utils.parse_measurement_var_as_float(s, 41)
    np.testing.assert_almost_equal(v, 15)

    h = {"MEASUREMENTVAR": [["41", "15.000000", ""]]}
    v = utils.parse_measurement_var_as_float(h, 41)
    np.testing.assert_almost_equal(v, 15)


def test_measurement_var_integer():
    s = r"#MEASUREMENTVAR= 41, 0, deg, "
    v = utils.parse_measurement_var_as_float(s, 41)
    np.testing.assert_almost_equal(v, 0.0)

    h = {"MEASUREMENTVAR": [["41", "0", "deg", ""]]}
    v = utils.parse_measurement_var_as_float(h, 41)
    np.testing.assert_almost_equal(v, 0.0)


def test_measurement_var_big_integer():
    s = r"#MEASUREMENTVAR= 41, 10000, deg, "
    v = utils.parse_measurement_var_as_float(s, 41)
    np.testing.assert_almost_equal(v, 10000)

    h = {"MEASUREMENTVAR": [["41", "10000", "deg", ""]]}
    v = utils.parse_measurement_var_as_float(h, 41)
    np.testing.assert_almost_equal(v, 10000)


def test_measurement_var_different_space():
    s = r"#MEASUREMENTVAR = 41, 0, deg, "
    v = utils.parse_measurement_var_as_float(s, 41)
    np.testing.assert_almost_equal(v, 0.0)

    h = {"MEASUREMENTVAR": [["41", "0", "deg", ""]]}
    v = utils.parse_measurement_var_as_float(h, 41)
    np.testing.assert_almost_equal(v, 0.0)


def test_measurement_var_different_comma():
    s = r"#MEASUREMENTVAR= 41 , 0, deg, "
    v = utils.parse_measurement_var_as_float(s, 41)
    np.testing.assert_almost_equal(v, 0.0)

    h = {"MEASUREMENTVAR": [["41", "0", "deg", ""]]}
    v = utils.parse_measurement_var_as_float(h, 41)
    np.testing.assert_almost_equal(v, 0.0)


def test_parse_cpt_class():
    s = r"#MEASUREMENTTEXT= 6, NEN 5140 / klasse onbekend, sondeernorm en kwaliteitsklasse"
    v = utils.parse_cpt_class(s)
    assert v is None

    h = {
        "MEASUREMENTTEXT": [
            ["6", "NEN 5140 / klasse onbekend", "sondeernorm en kwaliteitsklasse"]
        ]
    }
    v = utils.parse_cpt_class(h)
    assert v is None

    s = r"#MEASUREMENTTEXT= 6, NEN-EN-ISO22476-1 / klasse 2 / TE2, gehanteerde norm en klasse en type sondering"
    v = utils.parse_cpt_class(s)
    np.testing.assert_almost_equal(v, 2.0)

    h = {
        "MEASUREMENTTEXT": [
            [
                "6",
                "NEN-EN-ISO22476-1 / klasse 2 / TE2",
                "gehanteerde norm en klasse en type sondering",
            ]
        ]
    }
    v = utils.parse_cpt_class(h)
    np.testing.assert_almost_equal(v, 2.0)

    s = r"#MEASUREMENTTEXT= 6, Norm : NEN 5140; Klasse : 2, De norm waaraan deze sondering moet voldoen."
    v = utils.parse_cpt_class(s)
    np.testing.assert_almost_equal(v, 2.0)

    h = {
        "MEASUREMENTTEXT": [
            [
                "6",
                "Norm : NEN 5140; Klasse : 2",
                "De norm waaraan deze sondering moet voldoen.",
            ]
        ]
    }
    v = utils.parse_cpt_class(h)
    np.testing.assert_almost_equal(v, 2.0)

    s = r"#MEASUREMENTTEXT= 6, Norm : NEN 5140; class : 2, De norm waaraan deze sondering moet voldoen."
    v = utils.parse_cpt_class(s)
    np.testing.assert_almost_equal(v, 2.0)

    h = {
        "MEASUREMENTTEXT": [
            [
                "6",
                "Norm : NEN 5140; class : 2",
                "De norm waaraan deze sondering moet voldoen.",
            ]
        ]
    }
    v = utils.parse_cpt_class(h)
    np.testing.assert_almost_equal(v, 2.0)


def test_file_date():
    s = r"#FILEDATE= 2004, 1, 14"
    v = utils.parse_file_date(s)
    assert v == datetime(2004, 1, 14).date()

    h = {"FILEDATE": [["2004", "1", "14"]]}
    v = utils.parse_file_date(h)
    assert v == datetime(2004, 1, 14).date()


def test_project_id():
    s = r"#PROJECTID= CPT, 146203"
    v = utils.parse_project_type(s, "cpt")
    assert v == "146203"

    h = {"PROJECTID": [["CPT", "146203"]]}
    v = utils.parse_project_type(h, "cpt")
    assert v == "146203"

    s = r"#PROJECTID = DINO-BOR"
    v = utils.parse_project_type(s, "bore")
    assert v == "DINO-BOR"

    h = {"PROJECTID": [["DINO-BOR"]]}
    v = utils.parse_project_type(h, "bore")
    assert v == "DINO-BOR"

    s = r"#PROJECTID = CPT, 1018-0347-000, -"
    v = utils.parse_project_type(s, "cpt")
    assert v == "1018-0347-000"

    h = {"PROJECTID": [["CPT", "1018-0347-000", "-"]]}
    v = utils.parse_project_type(h, "cpt")
    assert v == "1018-0347-000"


def test_zid():
    s = r"#ZID= 31000, 1.3, 0.0"
    v = utils.parse_zid_as_float(s)
    np.testing.assert_almost_equal(v, 1.3)

    h = {"ZID": [["31000", "1.3", "0.0"]]}
    v = utils.parse_zid_as_float(h)
    np.testing.assert_almost_equal(v, 1.3)

    s = r"""#TESTID = B38C2094
        #XYID = 31000,108025,432470
        #ZID = 31000,-1.5
        #MEASUREMENTTEXT = 9, maaiveld, vast horizontaal niveau"""
    v = utils.parse_zid_as_float(s)
    np.testing.assert_almost_equal(v, -1.5)

    h = {
        "TESTID": [["B38C2094"]],
        "XYID": [["31000", "108025", "432470"]],
        "ZID": [["31000", "-1.5"]],
        "MEASUREMENTTEXT": [["9", "maaiveld", "vast horizontaal niveau"]],
    }
    v = utils.parse_zid_as_float(h)
    np.testing.assert_almost_equal(v, -1.5)


def test_cone_id():
    s = "#MEASUREMENTTEXT= 4, CFI, conus type"
    v = utils.parse_cone_id(s)
    assert v == "CFI"

    h = {"MEASUREMENTTEXT": [["4", "CFI", "conus type"]]}
    v = utils.parse_cone_id(h)
    assert v == "CFI"

    s = "#MEASUREMENTTEXT = 4, C10CFIIP.C18469, cone type and serial number"
    v = utils.parse_cone_id(s)
    assert v == "C10CFIIP.C18469"

    h = {"MEASUREMENTTEXT": [["4", "C10CFIIP.C18469", "cone type and serial number"]]}
    v = utils.parse_cone_id(h)
    assert v == "C10CFIIP.C18469"

    s = "#MEASUREMENTTEXT=4, S15CFII.d82, Cone Type"
    v = utils.parse_cone_id(s)
    assert v == "S15CFII.d82"

    h = {"MEASUREMENTTEXT": [["4", "S15CFII.d82", "Cone Type"]]}
    v = utils.parse_cone_id(h)
    assert v == "S15CFII.d82"


def test_parse_test_id():
    # Test ID without spaces on a single line
    s = "#TESTID= CPT-01"
    v = utils.parse_test_id(s)
    assert v == "CPT-01"

    h = {"TESTID": [["CPT-01"]]}
    v = utils.parse_test_id(h)
    assert v == "CPT-01"

    # Test ID without spaces on a single line and trailing white space
    s = "#TESTID= CPT-02   "
    v = utils.parse_test_id(s)
    assert v == "CPT-02"

    h = {"TESTID": [["CPT-02"]]}
    v = utils.parse_test_id(h)
    assert v == "CPT-02"

    # Test ID with a space on a single line
    s = "#TESTID= CPT 03"
    v = utils.parse_test_id(s)
    assert v == "CPT 03"

    h = {"TESTID": [["CPT 03"]]}
    v = utils.parse_test_id(h)
    assert v == "CPT 03"

    # Test ID with a space and trailing whitespace
    s = "#TESTID= CPT 03   "
    v = utils.parse_test_id(s)
    assert v == "CPT 03"

    h = {"TESTID": [["CPT 03"]]}
    v = utils.parse_test_id(h)
    assert v == "CPT 03"

    # Test ID with 2 spaces in the name
    s = "#TESTID= CPTU17.7 + 83BITE"
    v = utils.parse_test_id(s)
    assert v == "CPTU17.7 + 83BITE"

    h = {"TESTID": [["CPTU17.7 + 83BITE"]]}
    v = utils.parse_test_id(h)
    assert v == "CPTU17.7 + 83BITE"


def test_parse_gef_type():
    s = r"#PROCEDURECODE= GEF-CPT-Report"
    v = utils.parse_gef_type(s)
    assert v == "cpt"

    h = {"PROCEDURECODE": [["GEF-CPT-Report"]]}
    v = utils.parse_gef_type(h)
    assert v == "cpt"


def test_xyid():
    s = r"#XYID= 31000, 132127.181, 458102.351, 0.000, 0.000"
    x = utils.parse_xid_as_float(s)
    y = utils.parse_yid_as_float(s)
    np.testing.assert_almost_equal(x, 132127.181)
    np.testing.assert_almost_equal(y, 458102.351)

    h = {"XYID": [["31000", "132127.181", "458102.351", "0.000", "0.000"]]}
    x = utils.parse_xid_as_float(h)
    y = utils.parse_yid_as_float(h)
    np.testing.assert_almost_equal(x, 132127.181)
    np.testing.assert_almost_equal(y, 458102.351)

    # Belgian Bessel: coordinate system = geographic,
    # date = BD72, projection method = Belgian Lambert
    s = r"#XYID= 32000, 148484.599, 173046.501, 0.011, 0.011"
    v = utils.parse_xid_as_float(s)
    np.testing.assert_almost_equal(v, 148484.599)

    v = utils.parse_yid_as_float(s)
    np.testing.assert_almost_equal(v, 173046.501)

    v = utils.parse_coordinate_code(s)
    assert v == "32000"

    h = {
        "XYID": [["32000", "148484.599", "173046.501"]],
    }
    v = utils.parse_xid_as_float(h)
    np.testing.assert_almost_equal(v, 148484.599)

    v = utils.parse_yid_as_float(h)
    np.testing.assert_almost_equal(v, 173046.501)

    v = utils.parse_coordinate_code(h)
    assert v == "32000"


def test_columns_number():
    s = (
        r"#COLUMNINFO = 1, m, Diepte bovenkant laag, 1 #COLUMNINFO = 2, m, Diepte onderkant laag, 2"
        r"#COLUMNINFO = 3, mm, Zandmediaan, 8"
        r"#COLUMNINFO = 4, mm, Grindmediaan, 9"
    )
    v = utils.parse_columns_number(s)
    np.testing.assert_almost_equal(v, 4)


def test_parse_all_column_info():
    dictionary = MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT

    s = r"#COLUMNINFO= 1, m, Sondeerlengte, 1"
    ans = ([1], ["m"], ["penetrationLength"], [1])
    v = parse_all_columns_info(s, dictionary)
    assert v == ans

    h = {"COLUMNINFO": [["1", "m", "Sondeerlengte", "1"]]}
    v = parse_all_columns_info(h, dictionary)
    assert v == ans

    s = r"#COLUMNINFO= 7, m, Gecorrigeerde diepte, 11"
    ans = ([7], ["m"], ["depth"], [11])
    v = parse_all_columns_info(s, dictionary)
    assert v == ans

    h = {"COLUMNINFO": [["7", "m", "Gecorrigeerde diepte", "11"]]}
    v = parse_all_columns_info(h, dictionary)
    assert v == ans

    s = r"#COLUMNINFO= 4, %, Wrijvingsgetal Rf, 4"
    ans = ([4], ["%"], ["frictionRatio"], [4])
    v = parse_all_columns_info(s, dictionary)
    assert v == ans

    h = {"COLUMNINFO": [["4", "%", "Wrijvingsgetal Rf", "4"]]}
    v = parse_all_columns_info(h, dictionary)
    assert v == ans

    s = r"#COLUMNINFO= 4, Graden(deg), Helling, 8"
    ans = ([4], ["Graden(deg)"], ["inclinationResultant"], [8])
    v = parse_all_columns_info(s, dictionary)
    assert v == ans

    h = {"COLUMNINFO": [["4", "Graden(deg)", "Helling", "8"]]}
    v = parse_all_columns_info(h, dictionary)
    assert v == ans


def test_parse_data():
    df = pl.DataFrame({"col1": [1, 2, 3], "col2": [1, 2, 3], "col3": [1, 2, 3]})
    data_s = "\n1,1,1\n2,2,2\n3,3,3\n"
    df_parsed = _GefCpt.parse_data(
        data_s, ",", "\n", column_names=["col1", "col2", "col3"]
    )
    assert df_parsed.equals(df, null_equal=True)

    # Test terribly formatted columns
    data_s = "\n 1  1 1 \n2 2 2  \n3 3 3\n"
    df_parsed = _GefCpt.parse_data(
        data_s, " ", "\n", column_names=["col1", "col2", "col3"]
    )
    assert df_parsed.equals(df, null_equal=True)

    # Test terribly formatted columns
    data_s = "!\n 1  1 1 !\n2 2 2 ! \n3 3 3\n!"
    df_parsed = _GefCpt.parse_data(
        data_s, " ", "!", column_names=["col1", "col2", "col3"]
    )
    assert df_parsed.equals(df, null_equal=True)


def test_parse_column_separator():
    s = r"#COLUMNSEPARATOR = ;"
    v = utils.parse_column_separator(s)
    assert v == ";"

    h = {"COLUMNSEPARATOR": [[";"]]}
    v = utils.parse_column_separator(h)
    assert v == ";"


def test_parse_record_separator():
    s = r"#RECORDSEPARATOR = !"
    v = utils.parse_record_separator(s)
    assert v == "!"

    h = {"RECORDSEPARATOR": [["!"]]}
    v = utils.parse_record_separator(h)
    assert v == "!"


def test_find_separator():
    s = r"#COLUMNSEPARATOR = ;"
    v = utils.get_column_separator(s)
    assert v == ";"

    h = {"COLUMNSEPARATOR": [[";"]]}
    v = utils.get_column_separator(h)
    assert v == ";"

    s = r"I'm sorry the column separator is not in this gef file, even if he wanted to be there."
    v = utils.get_column_separator(s)
    assert v == r" "


def test_parse_add_info():
    s = "'SCH1'"
    v = utils.parse_add_info(s)
    assert v == "1) spoor schelpmateriaal <1% "

    s = "'DO TOL RO'"
    v = utils.parse_add_info(s)
    assert v == "1) dark olive-red "

    s = "'BIO'"
    v = utils.parse_add_info(s)
    assert v == "1) bioturbatie "

    s = "'KEL DR'"
    v = utils.parse_add_info(s)
    assert v == "1) keileem Formatie van Drente "


def test_parse_add_info_as_string():
    df = pl.DataFrame(
        {
            "remarks": [
                "1) spoor schelpmateriaal <1% ",
                "1) dark olive-red ",
                "1) keileem Formatie van Drente ",
            ]
        }
    )
    data_s = [
        ["'Kz'", "'SCH1'", "''"],
        ["'Kz1'", "'DO TOL RO'", "''"],
        ["'Kz2'", "'KEL DR'", "''"],
    ]

    df_parsed = _GefBore.parse_add_info_as_string(pl.DataFrame({}), data_s)
    assert df_parsed.equals(df, null_equal=True)


def test_parse_data_soil_code():
    df = pl.DataFrame({"geotechnicalSoilCode": ["Kz", "Kz1", "Kz2"]})
    data_s = [["'Kz'", "''"], ["'Kz1'", "''"], ["'Kz2'", "''"]]
    df_parsed = _GefBore.parse_data_soil_code(pl.DataFrame({}), data_s)
    assert df_parsed.equals(df, null_equal=True)


def test_parse_column_void():
    header = "\n#COLUMNVOID=1,-999\n#COLUMNVOID=2,-100.0\n#COLUMNVOID=3,999\n"
    ans = {1: float(-999), 2: -100.0, 3: float(999)}
    assert utils.parse_column_void(header) == ans

    with pytest.raises(exceptions.ParseGefError):
        header = "\n#COLUMNVOID=1,-999\n#COLUMNVOID=2,\n#COLUMNVOID=3,-999\n"
        utils.parse_column_void(header)

    with pytest.raises(exceptions.ParseGefError):
        header = "\n#COLUMNVOID=1,-999\n#COLUMNVOID=2,#COLUMNVOID=3,-999\n"
        utils.parse_column_void(header)


def test_pre_excavated_depth():
    df1 = pl.DataFrame(
        {
            "penetrationLength": [0.0, 1.0, 2.0, 3.0, 4.0],
            "coneResistance": [0.5, 0.5, 0.6, 0.7, 0.8],
        }
    )
    pre_excavated_depth = 2
    df_calculated = correct_pre_excavated_depth(df1, pre_excavated_depth)
    df = pl.DataFrame(
        {"penetrationLength": [2.0, 3.0, 4.0], "coneResistance": [0.6, 0.7, 0.8]}
    )
    assert df_calculated.equals(df, null_equal=True)


def test_replace_column_void():
    void_value = 999.0
    column_void = {"penetrationLength": void_value, "coneResistance": void_value}
    df1 = pl.DataFrame(
        {
            "penetrationLength": [0.0, 1.0, 2.0, 3.0, 4.0],
            "coneResistance": [void_value, 0.5, 0.6, 0.7, 0.8],
        }
    )
    df_calculated = replace_column_void(df1, column_void)
    df = pl.DataFrame(
        {
            "penetrationLength": [0.0, 1.0, 2.0, 3.0, 4.0],
            "coneResistance": [None, 0.5, 0.6, 0.7, 0.8],
        }
    )
    assert df_calculated.equals(df, null_equal=True)

    df1 = pl.DataFrame(
        {
            "penetrationLength": [0.0, 1.0, 2.0, 3.0, 4.0],
            "coneResistance": [None, 0.5, 0.6, None, 0.8],
        }
    )

    df_calculated = replace_column_void(df1, column_void)
    assert df_calculated.equals(df, null_equal=True)


def test_parse_cpt():
    cpt = read_cpt(
        """#GEFID= 1, 1, 0
#FILEOWNER= Wagen 2
#FILEDATE= 2004, 1, 14
#PROJECTID= CPT, 146203
#COLUMN= 3
#COLUMNINFO= 1, m, Sondeerlengte, 1
#COLUMNINFO= 2, MPa, Conuswaarde, 2
#COLUMNINFO= 3, MPa, Wrijvingsweerstand, 3
#XYID= 31000, 132127.181, 458102.351, 0.000, 0.000
#ZID= 31000, 1.3, 0.0
#MEASUREMENTTEXT= 4, 030919, Conusnummer
#MEASUREMENTTEXT= 6, NEN 5140, Norm
#MEASUREMENTTEXT= 9, MV, fixed horizontal level
#MEASUREMENTVAR= 20, 0.000000, MPa, Nulpunt conus voor sondering
#MEASUREMENTVAR= 22, 0.000000, MPa, Nulpunt kleef voor sondering
#MEASUREMENTVAR= 30, 0.000000, deg, Nulpunt helling voor sondering
#PROCEDURECODE= GEF-CPT-Report, 1, 0, 0, -
#TESTID= 4
#PROJECTNAME= Uitbreiding Rijksweg 2
#OS= DOS
#EOH=
0.0000e+000 0.0000e+000 0.0000e+000
1.0200e+000 7.1000e-001 4.6500e-002
1.0400e+000 7.3000e-001 4.2750e-002
1.0600e+000 6.9000e-001 3.9000e-002
"""
    )
    df_calculated = cpt.data

    df = pl.DataFrame(
        {
            "penetrationLength": [0.0000e000, 1.0200e000, 1.0400e000, 1.0600e000],
            "coneResistance": [0.0000e000, 7.1000e-001, 7.3000e-001, 6.9000e-001],
            "localFriction": [0.0000e000, 4.6500e-002, 4.2750e-002, 3.9000e-002],
            "depthOffset": [1.3, 0.28, 0.26, 0.24],
            "frictionRatioComputed": [None, 6.54929577, 5.85616438, 5.65217391],
        }
    )

    for column in df.columns:
        assert (
            df_calculated[column].round(4).equals(df[column].round(4), null_equal=True)
        )


def test_parse_bore():
    cpt = _GefBore(
        string="""
#GEFID = 1,1,0
#COLUMNTEXT = 1, aan
#COLUMNSEPARATOR = ;
#RECORDSEPARATOR = !
#FILEOWNER = DINO
#FILEDATE = 2010,9,1
#PROJECTID = DINO-BOR
#COLUMN = 9
#COLUMNINFO = 1, m, Diepte bovenkant laag, 1
#COLUMNINFO = 2, m, Diepte onderkant laag, 2
#COLUMNINFO = 3, mm, Zandmediaan, 8
#COLUMNINFO = 4, mm, Grindmediaan, 9
#COLUMNINFO = 5, %, Lutum percentage, 3
#COLUMNINFO = 6, %, Silt percentage, 4
#COLUMNINFO = 7, %, Zand percentage, 5
#COLUMNINFO = 8, %, Grind percentage, 6
#COLUMNINFO = 9, %, Organische stof percentage, 7
#COLUMNVOID = 1, -9999.99
#COLUMNVOID = 2, -9999.99
#COLUMNVOID = 3, -9999.99
#COLUMNVOID = 4, -9999.99
#COLUMNVOID = 5, -9999.99
#COLUMNVOID = 6, -9999.99
#COLUMNVOID = 7, -9999.99
#COLUMNVOID = 8, -9999.99
#COLUMNVOID = 9, -9999.99
#LASTSCAN = 44
#REPORTCODE = GEF-BORE-Report,1,0,0
#MEASUREMENTCODE = Onbekend
#TESTID = B25G0304
#XYID = 31000,120870,483400
#ZID = 31000,2.0
#MEASUREMENTVAR = 19, 1, -, aantal peilbuizen
#EOH =
0.00;1.20;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zgh2';'TGR GE';'ZMFO';'CA3';!
1.20;3.10;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zg';'ON';'ZMGO';'FN2';'CA2';!
3.10;5.00;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Vz';'TBR ZW';'ZMO';'CA1';!
"""
    )

    df = cpt.df
    # No need to check beyond parse result
    df.drop_in_place("geotechnicalSoilName")

    expected = pl.DataFrame(
        {
            "upperBoundary": [0.0, 1.2, 3.1],
            "lowerBoundary": [1.2, 3.1, 5.0],
            "sandMedianClass": [None, None, None],
            "gravelMedianClass": [None, None, None],
            "lutumPercentage": [None, None, None],
            "siltPercentage": [None, None, None],
            "sandPercentage": [None, None, None],
            "gravelPercentage": [None, None, None],
            "organicMatterPercentage": [None, None, None],
            "geotechnicalSoilCode": ["Zgh2", "Zg", "Vz"],
            "remarks": [
                "1) gray-yellow 2) ZMFO 3) kalkrijk ",
                "1) ON 2) ZMGO 3) weinig fijn grind (1-25%) 4) kalkarm ",
                "1) brown-black 2) ZMO 3) kalkloos ",
            ],
        },
    )
    assert df.equals(expected, null_equal=True)


def test_parse_pre_excavated_dept_with_void_inclination():
    cpt = _GefCpt(
        string="""
#COLUMN= 6
#COLUMNINFO= 1, m, Sondeerlengte, 1
#COLUMNINFO= 2, MPa, Conuswaarde, 2
#COLUMNINFO= 3, MPa, Wrijvingsweerstand, 3
#COLUMNINFO= 4, Deg, Helling, 8
#COLUMNINFO= 5, %, Wrijvingsgetal, 4
#COLUMNINFO= 6, MPa, Waterspanning, 5
#COLUMNVOID= 2, -9999.000000
#COLUMNVOID= 3, -9999.000000
#COLUMNVOID= 4, -9999.000000
#COLUMNVOID= 5, -9999.000000
#COLUMNVOID= 6, -9999.000000
#LASTSCAN= 3
#ZID= 31000, -0.39, 0.05
#MEASUREMENTVAR= 13, 1.500000, m, voorgeboorde/voorgegraven diepte
#REPORTCODE= GEF-CPT-Report, 1, 1, 0, -
#EOH=
0.0000e+000 -9.9990e+003 -9.9990e+003 -9.9990e+003 -9.9990e+003 -9.9990e+003
1.5100e+000 9.1800e+000 5.3238e-002 5.8398e-001 5.7314e-001 3.0107e-003
1.5300e+000 9.3044e+000 5.3803e-002 8.2007e-001 5.7986e-001 3.3362e-003
"""
    )
    expected = pl.DataFrame(
        {
            "penetrationLength": [1.51, 1.53],
            "coneResistance": [9.1800, 9.3044],
            "localFriction": [0.053238, 0.053803],
            "inclinationResultant": [0.58398, 0.82007],
            "frictionRatio": [0.57314, 0.57986],
            "porePressureU1": [0.003011, 0.003336],
            "depth": [1.510000, 1.529999],
        }
    )

    for column in cpt.df.columns:
        assert (
            expected[column].round(4).equals(cpt.df[column].round(4), null_equal=True)
        )


def test_assign_multiple_columns():
    df1 = pl.DataFrame(
        {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
    )
    v = common.assign_multiple_columns(df1, ["soil_pressure", "water_pressure"], df1)
    df = pl.DataFrame(
        {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
    )
    assert v.equals(df, null_equal=True)


def test_kpa_to_mpa():
    df1 = pl.DataFrame(
        {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
    )
    v = common.kpa_to_mpa(df1, ["soil_pressure", "water_pressure"])
    df = pl.DataFrame(
        {
            "soil_pressure": [0.0, 0.00025, 0.00075],
            "water_pressure": [0.0, 0.0, 0.004905],
        }
    )
    # TODO: replace with frame_equal when rounding is supported
    # assert df_calculated.frame_equal(df, null_equal=True)
    for column in df.columns:
        assert v[column].round(6).equals(df[column])


def test_bug_depth():
    cpt = """#GEFID= 1, 1, 0
#FILEDATE= 2011, 5, 13
#PROJECTID= CPT, 4015110
#COLUMN= 5
#COLUMNINFO= 1, m, Sondeerlengte, 1
#COLUMNINFO= 2, MPa, Conuswaarde, 2
#COLUMNINFO= 3, MPa, Wrijvingsweerstand, 3
#COLUMNINFO= 4, Deg, Helling, 8
#COLUMNINFO= 5, %, Wrijvingsgetal, 4
#XYID= 31000, 116371.70, 514039.34, 0.02, 0.02
#ZID= 31000, -2.21, 0.05
#MEASUREMENTTEXT= 4, S10CFI518, conusnummer
#MEASUREMENTTEXT= 6, NEN 5140 klasse2, gehanteerde norm en klasse sondering
#MEASUREMENTTEXT= 9, maaiveld, vast horizontaal vlak
#MEASUREMENTVAR= 1, 1000.000000, mm2, nom. oppervlak conuspunt
#MEASUREMENTVAR= 12, 0.000000, -, elektrische sondering
#MEASUREMENTVAR= 13, 1.500000, m, voorgeboorde/voorgegraven diepte
#TESTID= 29
#PROJECTNAME= Herinrichting van de N243
#REPORTCODE= GEF-CPT-Report, 1, 1, 0, -
#REPORTTEXT= 201, Mos Grondmechanica B.V.
#REPORTTEXT= 202, Herinrichting van de N243 te Schermer en Beemster
#REPORTTEXT= 203, Sondering 29
#STARTDATE= 2010, 12, 7
#STARTTIME= 9, 0, 21.000000
#OS= DOS
#EOH=
0.0000e+000 -9.9990e+003 -9.9990e+003 -9.9990e+003 -9.9990e+003
1.5100e+000 3.6954e-001 3.7981e-003 9.9502e-002 9.2308e-001
1.5300e+000 4.0370e-001 5.5589e-003 1.1194e-001 1.3260e+000
1.5500e+000 4.2854e-001 7.5360e-003 1.1194e-001 1.8315e+000
1.5700e+000 4.4407e-001 1.0028e-002 1.1194e-001 2.5117e+000
1.5900e+000 4.5028e-001 9.4163e-003 9.9502e-002 2.4202e+000
1.6100e+000 3.7265e-001 8.6356e-003 9.9502e-002 2.3201e+000
1.6300e+000 3.2607e-001 7.9297e-003 1.1194e-001 2.2770e+000
1.6500e+000 2.9812e-001 7.9607e-003 9.9502e-002 2.4315e+000
1.6700e+000 2.8570e-001 7.0938e-003 1.2438e-001 2.2649e+000
1.6900e+000 2.6085e-001 6.4691e-003 1.1194e-001 1.9653e+000
1.7100e+000 2.9812e-001 5.9068e-003 9.9502e-002 1.6748e+000
1.7300e+000 3.5091e-001 5.2480e-003 9.9502e-002 1.4391e+000
1.7500e+000 4.8444e-001 3.8332e-003 9.9502e-002 1.0214e+000
1.7700e+000 4.9065e-001 3.5531e-003 9.9502e-002 9.0498e-001
1.7900e+000 3.8196e-001 3.4469e-003 1.1194e-001 8.5759e-001
1.8100e+000 3.6023e-001 4.1928e-003 9.9502e-002 1.0363e+000
1.8300e+000 3.8196e-001 4.5735e-003 1.1194e-001 1.1782e+000
1.8500e+000 3.6333e-001 5.2490e-003 1.1194e-001 1.4342e+000
1.8700e+000 3.6954e-001 5.2590e-003 9.9502e-002 1.4635e+000
1.8900e+000 3.6954e-001 5.8176e-003 1.1194e-001 1.5781e+000
    """
    cpt = _GefCpt(string=cpt)
    assert np.isclose(cpt.df[0, "depth"], 1.51)


def test_bore_with_reduced_columns():
    _GefBore(
        string="""
#GEFID = 1,1,0
#PROJECTID= redacted, 1234, -
#COLUMN= 2
#COLUMNINFO= 1, m, Laag van, 1
#COLUMNINFO= 2, m, Laag tot, 2
#DATAFORMAT= ASCII
#COLUMNSEPARATOR= ;
#COLUMNTEXT= 1
#PROCEDURECODE= GEF-BORE-Report, 1, 0, 0, -
#REPORTCODE= GEF-BORE-Report, 1, 0, 0, -
#RECORDSEPARATOR= !
#OS= DOS
#LANGUAGE= NL
#EOH=
0.0000e+000;2.0000e-001;'Zs1';'ZUF';'DO TGR BR';;;!
2.0000e-001;4.0000e-001;'Vz3';;'DO BR';;;!
4.0000e-001;6.0000e-001;'Zs1';'ZUF';'DO TBR GR';;;!
6.0000e-001;1.0000e+000;'Zs1';'ZUF';'LI BR';;;!
1.0000e+000;1.4000e+000;'Vk1';;'DO TRO BR';;;!
1.4000e+000;2.2000e+000;'Zs1';'ZUF';'LI BR';'Restante BZB.: PR (zwak)';;!
2.2000e+000;2.6000e+000;'Zs1g1';'ZUF';'LI TBE BR';'Restante BZB.: PR (zwak)';;!
2.6000e+000;3.2000e+000;'Zs1g1';'ZUF';'LI GR';;;!
"""
    )
