# pylint: disable=E1136
import os
import unittest
from datetime import datetime

import numpy as np
import polars as pl

import pygef.geo as geo
import pygef.grouping as grouping
import pygef.utils as utils
from pygef.bore import Bore
from pygef.cpt import Cpt
from pygef.gef import (
    MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT,
    _GefBore,
    _GefCpt,
    calculate_friction_number,
    correct_depth_with_inclination,
    correct_pre_excavated_depth,
    replace_column_void,
)
from pygef.grouping import GroupClassification


class GefTest(unittest.TestCase):
    def test_measurement_var_with_minus_sign(self):
        s = r"#MEASUREMENTVAR= 41, -15.000000, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, -15)

        h = {"MEASUREMENTVAR": [["41", "-15.000000"]]}
        v = utils.parse_measurement_var_as_float(h, 41)
        self.assertAlmostEqual(v, -15)

    def test_measurement_var_without_minus_sign(self):
        s = r"#MEASUREMENTVAR= 41, 15.000000, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 15)

        h = {"MEASUREMENTVAR": [["41", "15.000000", ""]]}
        v = utils.parse_measurement_var_as_float(h, 41)
        self.assertAlmostEqual(v, 15)

    def test_measurement_var_integer(self):
        s = r"#MEASUREMENTVAR= 41, 0, deg, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0.0)

        h = {"MEASUREMENTVAR": [["41", "0", "deg", ""]]}
        v = utils.parse_measurement_var_as_float(h, 41)
        self.assertAlmostEqual(v, 0.0)

    def test_measurement_var_big_integer(self):
        s = r"#MEASUREMENTVAR= 41, 10000, deg, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 10000)

        h = {"MEASUREMENTVAR": [["41", "10000", "deg", ""]]}
        v = utils.parse_measurement_var_as_float(h, 41)
        self.assertAlmostEqual(v, 10000)

    def test_measurement_var_different_space(self):
        s = r"#MEASUREMENTVAR = 41, 0, deg, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0.0)

        h = {"MEASUREMENTVAR": [["41", "0", "deg", ""]]}
        v = utils.parse_measurement_var_as_float(h, 41)
        self.assertAlmostEqual(v, 0.0)

    def test_measurement_var_different_comma(self):
        s = r"#MEASUREMENTVAR= 41 , 0, deg, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0.0)

        h = {"MEASUREMENTVAR": [["41", "0", "deg", ""]]}
        v = utils.parse_measurement_var_as_float(h, 41)
        self.assertAlmostEqual(v, 0.0)

    def test_parse_cpt_class(self):
        s = r"#MEASUREMENTTEXT= 6, NEN 5140 / klasse onbekend, sondeernorm en kwaliteitsklasse"
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, None)

        h = {
            "MEASUREMENTTEXT": [
                ["6", "NEN 5140 / klasse onbekend", "sondeernorm en kwaliteitsklasse"]
            ]
        }
        v = utils.parse_cpt_class(h)
        self.assertEqual(v, None)

        s = r"#MEASUREMENTTEXT= 6, NEN-EN-ISO22476-1 / klasse 2 / TE2, gehanteerde norm en klasse en type sondering"
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, 2.0)

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
        self.assertEqual(v, 2.0)

        s = r"#MEASUREMENTTEXT= 6, Norm : NEN 5140; Klasse : 2, De norm waaraan deze sondering moet voldoen."
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, 2.0)

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
        self.assertEqual(v, 2.0)

        s = r"#MEASUREMENTTEXT= 6, Norm : NEN 5140; class : 2, De norm waaraan deze sondering moet voldoen."
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, 2.0)

        h = {
            "MEASUREMENTTEXT": [
                [
                    "6",
                    "Norm : NEN 5140; class : 2",
                    "De norm waaraan deze sondering moet voldoen.",
                ]
            ]
        }
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, 2.0)

    def test_file_date(self):
        s = r"#FILEDATE= 2004, 1, 14"
        v = utils.parse_file_date(s)
        self.assertTrue(v == datetime(2004, 1, 14).date())

        h = {"FILEDATE": [["2004", "1", "14"]]}
        v = utils.parse_file_date(h)
        self.assertTrue(v == datetime(2004, 1, 14).date())

    def test_project_id(self):
        s = r"#PROJECTID= CPT, 146203"
        v = utils.parse_project_type(s, "cpt")
        self.assertEqual(v, "146203")

        h = {"PROJECTID": [["CPT", "146203"]]}
        v = utils.parse_project_type(h, "cpt")
        self.assertEqual(v, "146203")

        s = r"#PROJECTID = DINO-BOR"
        v = utils.parse_project_type(s, "bore")
        self.assertEqual(v, "DINO-BOR")

        h = {"PROJECTID": [["DINO-BOR"]]}
        v = utils.parse_project_type(h, "bore")
        self.assertEqual(v, "DINO-BOR")

        s = r"#PROJECTID = CPT, 1018-0347-000, -"
        v = utils.parse_project_type(s, "cpt")
        self.assertEqual(v, "1018-0347-000")

        h = {"PROJECTID": [["CPT", "1018-0347-000", "-"]]}
        v = utils.parse_project_type(h, "cpt")
        self.assertEqual(v, "1018-0347-000")

    def test_zid(self):
        s = r"#ZID= 31000, 1.3, 0.0"
        v = utils.parse_zid_as_float(s)
        self.assertEqual(v, 1.3)

        h = {"ZID": [["31000", "1.3", "0.0"]]}
        v = utils.parse_zid_as_float(h)
        self.assertEqual(v, 1.3)

        s = r"""#TESTID = B38C2094
            #XYID = 31000,108025,432470
            #ZID = 31000,-1.5
            #MEASUREMENTTEXT = 9, maaiveld, vast horizontaal niveau"""
        v = utils.parse_zid_as_float(s)
        self.assertEqual(v, -1.5)

        h = {
            "TESTID": [["B38C2094"]],
            "XYID": [["31000", "108025", "432470"]],
            "ZID": [["31000", "-1.5"]],
            "MEASUREMENTTEXT": [["9", "maaiveld", "vast horizontaal niveau"]],
        }
        v = utils.parse_zid_as_float(h)
        self.assertEqual(v, -1.5)

    def test_cone_id(self):
        s = "#MEASUREMENTTEXT= 4, CFI, conus type"
        v = utils.parse_cone_id(s)
        self.assertEqual("CFI", v)

        h = {"MEASUREMENTTEXT": [["4", "CFI", "conus type"]]}
        v = utils.parse_cone_id(h)
        self.assertEqual("CFI", v)

        s = "#MEASUREMENTTEXT = 4, C10CFIIP.C18469, cone type and serial number"
        v = utils.parse_cone_id(s)
        self.assertEqual("C10CFIIP.C18469", v)

        h = {
            "MEASUREMENTTEXT": [["4", "C10CFIIP.C18469", "cone type and serial number"]]
        }
        v = utils.parse_cone_id(h)
        self.assertEqual("C10CFIIP.C18469", v)

        s = "#MEASUREMENTTEXT=4, S15CFII.d82, Cone Type"
        v = utils.parse_cone_id(s)
        self.assertEqual("S15CFII.d82", v)

        h = {"MEASUREMENTTEXT": [["4", "S15CFII.d82", "Cone Type"]]}
        v = utils.parse_cone_id(h)
        self.assertEqual("S15CFII.d82", v)

    def test_parse_test_id(self):
        # Test ID without spaces on a single line
        s = "#TESTID= CPT-01"
        v = utils.parse_test_id(s)
        self.assertEqual("CPT-01", v)

        h = {"TESTID": [["CPT-01"]]}
        v = utils.parse_test_id(h)
        self.assertEqual("CPT-01", v)

        # Test ID without spaces on a single line and trailing white space
        s = "#TESTID= CPT-02   "
        v = utils.parse_test_id(s)
        self.assertEqual("CPT-02", v)

        h = {"TESTID": [["CPT-02"]]}
        v = utils.parse_test_id(h)
        self.assertEqual("CPT-02", v)

        # Test ID with a space on a single line
        s = "#TESTID= CPT 03"
        v = utils.parse_test_id(s)
        self.assertEqual("CPT 03", v)

        h = {"TESTID": [["CPT 03"]]}
        v = utils.parse_test_id(h)
        self.assertEqual("CPT 03", v)

        # Test ID with a space and trailing whitespace
        s = "#TESTID= CPT 03   "
        v = utils.parse_test_id(s)
        self.assertEqual("CPT 03", v)

        h = {"TESTID": [["CPT 03"]]}
        v = utils.parse_test_id(h)
        self.assertEqual("CPT 03", v)

        # Test ID with 2 spaces in the name
        s = "#TESTID= CPTU17.7 + 83BITE"
        v = utils.parse_test_id(s)
        self.assertEqual("CPTU17.7 + 83BITE", v)

        h = {"TESTID": [["CPTU17.7 + 83BITE"]]}
        v = utils.parse_test_id(h)
        self.assertEqual("CPTU17.7 + 83BITE", v)

    def test_parse_gef_type(self):
        s = r"#PROCEDURECODE= GEF-CPT-Report"
        v = utils.parse_gef_type(s)
        self.assertEqual(v, "cpt")

        h = {"PROCEDURECODE": [["GEF-CPT-Report"]]}
        v = utils.parse_gef_type(h)
        self.assertEqual(v, "cpt")

    def test_xyid(self):
        s = r"#XYID= 31000, 132127.181, 458102.351, 0.000, 0.000"
        x = utils.parse_xid_as_float(s)
        y = utils.parse_yid_as_float(s)
        self.assertEqual(x, 132127.181)
        self.assertEqual(y, 458102.351)

        h = {"XYID": [["31000", "132127.181", "458102.351", "0.000", "0.000"]]}
        x = utils.parse_xid_as_float(h)
        y = utils.parse_yid_as_float(h)
        self.assertEqual(x, 132127.181)
        self.assertEqual(y, 458102.351)

    def test_columns_number(self):
        s = (
            r"#COLUMNINFO = 1, m, Diepte bovenkant laag, 1 #COLUMNINFO = 2, m, Diepte onderkant laag, 2"
            r"#COLUMNINFO = 3, mm, Zandmediaan, 8"
            r"#COLUMNINFO = 4, mm, Grindmediaan, 9"
        )
        v = utils.parse_columns_number(s)
        self.assertEqual(v, 4)

    def test_quantity_number(self):
        s = r"#COLUMNINFO= 1, m, Sondeerlengte, 1"
        v = utils.parse_quantity_number(s, 1)
        self.assertEqual(v, 1)

        h = {"COLUMNINFO": [["1", "m", "Sondeerlengte", "1"]]}
        v = utils.parse_quantity_number(h, 1)
        self.assertEqual(v, 1)

        s = r"#COLUMNINFO= 7, m, Gecorrigeerde diepte, 11"
        v = utils.parse_quantity_number(s, 7)
        self.assertEqual(v, 11)

        h = {"COLUMNINFO": [["7", "m", "Gecorrigeerde diepte", "11"]]}
        v = utils.parse_quantity_number(h, 7)
        self.assertEqual(v, 11)

        s = r"#COLUMNINFO= 4, %, Wrijvingsgetal Rf, 4"
        v = utils.parse_quantity_number(s, 4)
        self.assertEqual(v, 4)

        h = {"COLUMNINFO": [["4", "%", "Wrijvingsgetal Rf", "4"]]}
        v = utils.parse_quantity_number(h, 4)
        self.assertEqual(v, 4)

        s = r"#COLUMNINFO= 4, Graden(deg), Helling, 8"
        v = utils.parse_quantity_number(s, 4)
        self.assertEqual(v, 8)

        h = {"COLUMNINFO": [["4", "Graden(deg)", "Helling", "8"]]}
        v = utils.parse_quantity_number(h, 4)
        self.assertEqual(v, 8)

    def test_column_info(self):
        s = r"#COLUMNINFO= 1, m, Sondeerlengte, 1"
        v = utils.parse_column_info(s, 1, MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT)
        self.assertEqual(v, "penetration_length")

        h = {"COLUMNINFO": [["1", "m", "Sondeerlengte", "1"]]}
        v = utils.parse_column_info(h, 1, MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT)
        self.assertEqual(v, "penetration_length")

    def test_end_of_the_header(self):
        s = r"#EOH="
        v = utils.parse_end_of_header(s)
        self.assertEqual(v, "#EOH=")

    def test_parse_data(self):
        header_s = "This is an header"
        df = pl.DataFrame({"col1": [1, 2, 3], "col2": [1, 2, 3], "col3": [1, 2, 3]})
        data_s = "\n1,1,1\n2,2,2\n3,3,3\n".replace(",", " ")
        df_parsed = _GefCpt.parse_data(
            header_s, data_s, column_names=["col1", "col2", "col3"]
        )
        assert df_parsed.frame_equal(df, null_equal=True)

        # Test terribly formatted columns
        data_s = "\n 1  1 1 \n2 2 2  \n3 3 3\n"
        df_parsed = _GefCpt.parse_data(
            header_s, data_s, column_names=["col1", "col2", "col3"]
        )
        assert df_parsed.frame_equal(df, null_equal=True)

    def test_parse_column_separator(self):
        s = r"#COLUMNSEPARATOR = ;"
        v = utils.parse_column_separator(s)
        self.assertEqual(v, ";")

        h = {"COLUMNSEPARATOR": [[";"]]}
        v = utils.parse_column_separator(h)
        self.assertEqual(v, ";")

    def test_parse_record_separator(self):
        s = r"#RECORDSEPARATOR = !"
        v = utils.parse_record_separator(s)
        self.assertEqual(v, "!")

        h = {"RECORDSEPARATOR": [["!"]]}
        v = utils.parse_record_separator(h)
        self.assertEqual(v, "!")

    def test_find_separator(self):
        s = r"#COLUMNSEPARATOR = ;"
        v = utils.find_separator(s)
        self.assertEqual(v, ";")

        h = {"COLUMNSEPARATOR": [[";"]]}
        v = utils.find_separator(h)
        self.assertEqual(v, ";")

        s = r"I'm sorry the column separator is not in this gef file, even if he wanted to be there."
        v = utils.find_separator(s)
        self.assertEqual(v, r" ")

    def test_create_soil_type(self):
        s = "'Kz'"
        v = utils.create_soil_type(s)
        self.assertEqual(v, "clay 100% with sand")

    def test_parse_data_column_info(self):
        header_s = "This is an header"
        df = pl.DataFrame({"col1": [1, 2, 3], "col2": [1, 2, 3], "col3": [1, 2, 3]})
        data_s = "\n1;1;1\n2;2;2\n3;3;3\n"
        sep = ";"
        df_parsed = _GefBore.parse_data_column_info(
            header_s, data_s, sep, 3, columns_info=["col1", "col2", "col3"]
        )
        assert df_parsed.frame_equal(df, null_equal=True)

    def test_parse_data_soil_type(self):
        df = pl.DataFrame(
            {
                "Soil_type": [
                    "clay 100% with sand",
                    "clay 95% with sand 5%",
                    "clay 90% with sand 10%",
                ]
            }
        )
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"], ["'Kz2'", "''"]]
        df_parsed = _GefBore.parse_data_soil_type(pl.DataFrame({}), data_s)
        assert df_parsed.frame_equal(df, null_equal=True)

    def test_parse_add_info(self):
        s = "'SCH1'"
        v = utils.parse_add_info(s)
        self.assertEqual(v, "1) spoor schelpmateriaal <1% ")

        s = "'DO TOL RO'"
        v = utils.parse_add_info(s)
        self.assertEqual(v, "1) dark olive-red ")

        s = "'BIO'"
        v = utils.parse_add_info(s)
        self.assertEqual(v, "1) bioturbatie ")

        s = "'KEL DR'"
        v = utils.parse_add_info(s)
        self.assertEqual(v, "1) keileem Formatie van Drente ")

    def test_parse_add_info_as_string(self):
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
        assert df_parsed.frame_equal(df, null_equal=True)

    def test_soil_quantification(self):
        s = "'Kz'"
        v = utils.soil_quantification(s)
        self.assertTrue(np.all(np.isclose(v, [0, 0.05, 0.95, 0.0, 0.0, 0.0])))

        s = "'Kz1'"
        v = utils.soil_quantification(s)
        self.assertTrue(np.all(np.isclose(v, [0.0, 0.05, 0.95, 0.0, 0.0, 0.0])))

        s = "'Kz1s1'"
        v = utils.soil_quantification(s)
        self.assertTrue(np.all(np.isclose(v, [0.0, 0.05, 0.9, 0.0, 0.0, 0.05])))

    def test_parse_data_soil_code(self):
        df = pl.DataFrame({"Soil_code": ["Kz", "Kz1", "Kz2"]})
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"], ["'Kz2'", "''"]]
        df_parsed = _GefBore.parse_data_soil_code(pl.DataFrame({}), data_s)
        assert df_parsed.frame_equal(df, null_equal=True)

    def test_data_soil_quantified(self):
        lst = [[0.0, 0.05, 0.95, 0.0, 0.0, 0.0], [0.0, 0.05, 0.95, 0.0, 0.0, 0.0]]
        df = pl.DataFrame(
            lst, columns=["Gravel", "Sand", "Clay", "Loam", "Peat", "Silt"]
        )
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"]]
        df_parsed = _GefBore.parse_soil_quantification(pl.DataFrame({}), data_s)
        assert df_parsed.frame_equal(df, null_equal=True)

    def test_calculate_elevation_respect_to_NAP(self):
        df1 = pl.DataFrame({"depth": [0.0, 1.0, 2.0, 3.0, 4.0]})
        zid = -3
        df_calculated = df1.with_column(
            _GefCpt.calculate_elevation_with_respect_to_nap(zid, 31000)
        )
        df = pl.DataFrame(
            {
                "depth": [0.0, 1.0, 2.0, 3.0, 4.0],
                "elevation_with_respect_to_nap": [-3.0, -4.0, -5.0, -6.0, -7.0],
            }
        )
        assert df_calculated.frame_equal(df, null_equal=True)

    def test_correct_depth_with_inclination(self):
        df1 = pl.DataFrame({"penetration_length": [0.0, 0.2, 0.4, 0.6, 0.8]})
        df_calculated = df1.with_column(correct_depth_with_inclination(df1.columns))
        df = pl.DataFrame(
            {
                "penetration_length": [0.0, 0.2, 0.4, 0.6, 0.8],
                "depth": [0.0, 0.2, 0.4, 0.6, 0.8],
            }
        )
        assert df_calculated.frame_equal(df, null_equal=True)

        df2 = pl.DataFrame(
            {
                "penetration_length": [0.0, 0.2, 0.4, 0.6, 0.8],
                "inclination": [45, 45, 45, 45, 45],
            }
        )
        df_calculated = df2.with_column(correct_depth_with_inclination(df2.columns))
        df = pl.DataFrame(
            {
                "penetration_length": [0.0, 0.2, 0.4, 0.6, 0.8],
                "inclination": [45, 45, 45, 45, 45],
                "depth": [
                    0.0,
                    0.14142135623730953,
                    0.28284271247461906,
                    0.42426406871192857,
                    0.5656854249492381,
                ],
            }
        )
        assert np.isclose(df_calculated["depth"], df["depth"]).all()

        df2 = pl.DataFrame(
            {
                "penetration_length": [0.0, 0.2, 0.4, 0.6, 0.8],
                "corrected_depth": [0.0, 0.10, 0.25, 0.40, 0.60],
                "inclination": [45, 45, 45, 45, 45],
            }
        )
        df_calculated = df2.with_column(correct_depth_with_inclination(df2.columns))
        df = pl.DataFrame(
            {
                "penetration_length": [0.0, 0.2, 0.4, 0.6, 0.8],
                "depth": [0.0, 0.10, 0.25, 0.40, 0.60],
                "inclination": [45, 45, 45, 45, 45],
            }
        )
        assert np.isclose(df_calculated["depth"], df["depth"]).all()

    def test_pre_excavated_depth(self):
        df1 = pl.DataFrame(
            {
                "penetration_length": [0.0, 1.0, 2.0, 3.0, 4.0],
                "qc": [0.5, 0.5, 0.6, 0.7, 0.8],
            }
        )
        pre_excavated_depth = 2
        df_calculated = correct_pre_excavated_depth(df1, pre_excavated_depth)
        df = pl.DataFrame(
            {"penetration_length": [2.0, 3.0, 4.0], "qc": [0.6, 0.7, 0.8]}
        )
        assert df_calculated.frame_equal(df, null_equal=True)

    def test_replace_column_void(self):
        column_void = 999.0
        df1 = pl.DataFrame(
            {
                "penetration_length": [0.0, 1.0, 2.0, 3.0, 4.0],
                "qc": [column_void, 0.5, 0.6, 0.7, 0.8],
            }
        )
        df_calculated = replace_column_void(df1, column_void)
        df = pl.DataFrame(
            {
                "penetration_length": [1.0, 2.0, 3.0, 4.0],
                "qc": [0.5, 0.6, 0.7, 0.8],
            }
        )
        assert df_calculated.frame_equal(df, null_equal=True)

        df1 = pl.DataFrame(
            {
                "penetration_length": [1.0, 2.0, 3.0, 4.0],
                "qc": [0.5, 0.6, column_void, 0.8],
            }
        )

        df_calculated = replace_column_void(df1, column_void)
        assert df_calculated.frame_equal(df, null_equal=True)

    def test_calculate_friction_number(self):
        df1 = pl.DataFrame(
            {"qc": [0.5, 0.5, 0.6, 0.7, 0.8], "fs": [0.0, 0.05, 0.06, 0.07, 0.08]}
        )
        df_calculated = df1.with_column(calculate_friction_number(df1.columns))
        df = pl.DataFrame(
            {
                "qc": [0.5, 0.5, 0.6, 0.7, 0.8],
                "fs": [0.0, 0.05, 0.06, 0.07, 0.08],
                "friction_number": [0.0, 10.0, 10.0, 10.000000000000002, 10.0],
            }
        )
        assert df_calculated.frame_equal(df, null_equal=True)

    def test_parse_cpt(self):
        cpt = Cpt(
            content=dict(
                string="""
#GEFID= 1, 1, 0
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
""",
                file_type="gef",
            )
        )
        df_calculated = cpt.df
        df = pl.DataFrame(
            {
                "penetration_length": [0.0000e000, 1.0200e000, 1.0400e000, 1.0600e000],
                "qc": [0.0000e000, 7.1000e-001, 7.3000e-001, 6.9000e-001],
                "fs": [0.0000e000, 4.6500e-002, 4.2750e-002, 3.9000e-002],
                "depth": [0.0000e000, 1.0200e000, 1.0400e000, 1.0600e000],
                "elevation_with_respect_to_nap": [1.3, 0.28, 0.26, 0.24],
                "friction_number": [np.nan, 6.54929577, 5.85616438, 5.65217391],
            }
        )

        # TODO: replace with frame_equal when rounding is supported
        # assert df_calculated.frame_equal(df, null_equal=True)
        for column in df.columns:
            assert df_calculated[column].round(6) == df[column]

    def test_parse_bore(self):
        cpt = Bore(
            content=dict(
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
""",
                file_type="gef",
            )
        )
        df_calculated = cpt.df
        df = pl.DataFrame(
            {
                "depth_top": [0.0, 1.2, 3.1],
                "depth_bottom": [1.2, 3.1, 5.0],
                "soil_code": ["Zgh2", "Zg", "Vz"],
                "remarks": [
                    "1) gray-yellow 2) ZMFO 3) kalkrijk ",
                    "1) ON 2) ZMGO 3) weinig fijn grind (1-25%) 4) kalkarm ",
                    "1) brown-black 2) ZMO 3) kalkloos ",
                ],
                "g": [0.05, 0.05, 0.00],
                "s": [0.85, 0.95, 0.05],
                "c": [0.0, 0.0, 0.0],
                "l": [0.0, 0.0, 0.0],
                "p": [0.10, 0.00, 0.95],
                "si": [0.0, 0.0, 0.0],
            }
        )
        assert df_calculated.frame_equal(df, null_equal=True)

    def test_parse_pre_excavated_dept_with_void_inclination(self):
        cpt = Cpt(
            content=dict(
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
""",
                file_type="gef",
            )
        )
        expected = pl.DataFrame(
            {
                "penetration_length": [1.51, 1.53],
                "qc": [9.1800, 9.3044],
                "fs": [0.053238, 0.053803],
                "inclination": [0.58398, 0.82007],
                "friction_number": [0.579935, 0.578253],
                "u1": [0.003011, 0.003336],
                "depth": [1.510000, 1.529999],
                "elevation_with_respect_to_nap": [-1.90, -1.919999],
            }
        )
        # TODO: replace with frame_equal when rounding is supported
        # assert cpt.df.frame_equal(expected, null_equal=True)
        for column in cpt.df.columns:
            assert expected[column].round(6) == cpt.df[column]

    def test_delta_depth(self):
        df1 = pl.DataFrame({"depth": [0.0, 0.5, 1.0]})
        v = geo.delta_depth(df1)
        df = pl.DataFrame({"depth": [0.0, 0.5, 1.0], "delta_depth": [0.0, 0.5, 0.5]})
        assert v.frame_equal(df, null_equal=True)

    def test_soil_pressure(self):
        v = pl.DataFrame({"gamma": [0.0, 0.5, 1.0], "delta_depth": [0.0, 0.5, 0.5]})
        geo.soil_pressure(v)
        df = pl.DataFrame(
            {
                "gamma": [0.0, 0.5, 1.0],
                "delta_depth": [0.0, 0.5, 0.5],
                "soil_pressure": [0.0, 0.25, 0.75],
            }
        )
        assert v.frame_equal(df, null_equal=True)

    def test_water_pressure(self):
        water_level = 0.5
        v = pl.DataFrame({"depth": [0.0, 0.5, 1.0]})
        geo.water_pressure(v, water_level)
        df = pl.DataFrame(
            {"depth": [0.0, 0.5, 1.0], "water_pressure": [0.0, 0.0, 4.905]}
        )

        assert v.frame_equal(df, null_equal=True)

    def test_effective_soil_pressure(self):
        df1 = pl.DataFrame(
            {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
        )
        v = geo.effective_soil_pressure(df1)
        df = pl.DataFrame(
            {
                "soil_pressure": [0.0, 0.25, 0.75],
                "water_pressure": [0.0, 0.0, 4.905],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
            }
        )
        assert v.frame_equal(df, null_equal=True)

    def test_assign_multiple_columns(self):
        df1 = pl.DataFrame(
            {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
        )
        v = utils.assign_multiple_columns(df1, ["soil_pressure", "water_pressure"], df1)
        df = pl.DataFrame(
            {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
        )
        assert v.frame_equal(df, null_equal=True)

    def test_kpa_to_mpa(self):
        df1 = pl.DataFrame(
            {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
        )
        v = utils.kpa_to_mpa(df1, ["soil_pressure", "water_pressure"])
        df = pl.DataFrame(
            {
                "soil_pressure": [0.0, 0.00025, 0.00075],
                "water_pressure": [0.0, 0.0, 0.004905],
            }
        )
        # TODO: replace with frame_equal when rounding is supported
        # assert df_calculated.frame_equal(df, null_equal=True)
        for column in df.columns:
            assert v[column].round(6) == df[column]

    def test_qt(self):
        df1 = pl.DataFrame({"qc": [0.0, 1.0, 2.0], "u2": [0.0, 1.0, 1.0]})
        v = geo.qt(df1, area_quotient_cone_tip=0.5)
        df = pl.DataFrame(
            {"qc": [0.0, 1.0, 2.0], "u2": [0.0, 1.0, 1.0], "qt": [0.0, 1.5, 2.5]}
        )
        assert v.frame_equal(df, null_equal=True)

    def test_normalized_cone_resistance(self):
        df1 = pl.DataFrame(
            {
                "qt": [0.0, 1.5, 2.5],
                "soil_pressure": [0.0, 0.25, 0.75],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
            }
        )
        v = geo.normalized_cone_resistance(df1)
        df = pl.DataFrame(
            {
                "qt": [0.0, 1.5, 2.5],
                "soil_pressure": [0.0, 0.25, 0.75],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
                "normalized_cone_resistance": [-np.nan, 5.0, 1.0],
            }
        )
        # TODO: why aren't these equal with df.frame_equal?
        assert v.to_csv() == df.to_csv()

    def test_normalized_friction_ratio(self):
        df1 = pl.DataFrame(
            {
                "qt": [0.0, 1.5, 2.5],
                "fs": [0.5, 0.5, 0.5],
                "soil_pressure": [0.0, 0.25, 0.75],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
            }
        )
        v = geo.normalized_friction_ratio(df1)
        df = pl.DataFrame(
            {
                "qt": [0.0, 1.5, 2.5],
                "fs": [0.5, 0.5, 0.5],
                "soil_pressure": [0.0, 0.25, 0.75],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
                "normalized_friction_ratio": [np.inf, 40.0, 28.57142857142857],
            }
        )
        assert v.frame_equal(df, null_equal=True)

    def test_nan_to_zero(self):
        df1 = pl.DataFrame({"type_index": [None, 1.0, 2.0]})
        v = utils.none_to_zero(df1)
        df = pl.DataFrame({"type_index": [0.0, 1.0, 2.0]})
        assert v.frame_equal(df, null_equal=True)

    def test_group_equal_layers(self):
        df_group = pl.DataFrame(
            {
                "depth": [0, 1, 2, 3, 4, 5, 6],
                "soil_type": [
                    "Peat",
                    "Peat",
                    "Peat",
                    "Silt mixtures - clayey silt to silty clay",
                    "Silt mixtures - clayey silt to silty clay",
                    "Silt mixtures - clayey silt to silty clay",
                    "Sand",
                ],
                "elevation_with_respect_to_nap": [2, 1, 0, -1, -2, -3, -4],
            }
        )
        group = GroupClassification(2, df_group, 0.2)
        v = group.group_equal_layers(df_group, "soil_type", "depth", 0)
        df = pl.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 2.0, 5.0],
                "zf": [2, 5, 6],
                "thickness": [2.0, 3.0, 1.0],
                "z_centr": [1.0, 3.5, 5.5],
                "z_in_NAP": [2.0, 0.0, -3.0],
                "zf_NAP": [0, -3, -4],
                "z_centr_NAP": [1.0, -1.5, -3.5],
            }
        )
        # todo: grouping functionality should be fixed
        # assert v.layer == df.layer
        # assert v.z_in == df.z_in
        # assert v.zf == df.zf
        # assert v.thickness == df.thickness
        # assert v.z_centr == df.z_centr
        # assert v.z_in_NAP == df.z_in_NAP
        # assert v.zf_NAP == df.zf_NAP
        # assert v.z_centr_NAP == df.z_centr_NAP

    def test_group_significant_layers(self):
        df_group = pl.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 0.4, 5.0],
                "zf": [0.4, 5, 6],
                "thickness": [0.4, 4.6, 1.0],
            }
        )

        v = grouping.group_significant_layers(df_group, 0.5, 0.0)

        df = pl.DataFrame(
            {
                "layer": ["Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 5.0],
                "zf": [5.0, 6.0],
                "thickness": [5.0, 1.0],
                "z_centr": [2.5, 5.5],
            }
        )

        # TODO: use a better comparison method
        assert v.zf == df.zf
        assert v.layer == df.layer
        assert v.z_in == df.z_in
        assert v.thickness == df.thickness
        assert v.z_centr == df.z_centr

    def test_calculate_thickness(self):
        df_group = pl.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 0.4, 5.0],
                "zf": [0.4, 5, 6],
            }
        )
        v = grouping.calculate_thickness(df_group)
        df = pl.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 0.4, 5.0],
                "zf": [0.4, 5, 6],
                "thickness": [0.4, 4.6, 1.0],
            }
        )
        assert v.frame_equal(df, null_equal=True)

    def test_calculate_z_centr(self):
        df_group = pl.DataFrame(
            {
                "layer": ["Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 5.0],
                "zf": [5.0, 6.0],
            }
        )
        v = grouping.calculate_z_centr(df_group)
        df = pl.DataFrame(
            {
                "layer": ["Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 5.0],
                "zf": [5.0, 6.0],
                "z_centr": [2.5, 5.5],
            }
        )
        assert v.frame_equal(df, null_equal=True)

    def test_calculate_zf_NAP(self):
        df_group = pl.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 2.0, 5.0],
                "zf": [2, 5, 6],
                "thickness": [2.0, 3.0, 1.0],
                "z_centr": [1.0, 3.5, 5.5],
            }
        )

        v = grouping.calculate_zf_NAP(df_group, 2)

        df = pl.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 2.0, 5.0],
                "zf": [2, 5, 6],
                "thickness": [2.0, 3.0, 1.0],
                "z_centr": [1.0, 3.5, 5.5],
                "zf_NAP": [0, -3, -4],
            }
        )
        assert v.frame_equal(df, null_equal=True)

    def test_bug_depth(self):
        cpt = """
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
        cpt = Cpt(content=dict(string=cpt, file_type="gef"))
        assert np.isclose(cpt.df[0, "depth"], 1.51)

    def test_bore_with_reduced_columns(self):
        Bore(
            content=dict(
                string="""
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
""",
                file_type="gef",
            )
        )


class BoreTest(unittest.TestCase):
    def setUp(self):
        self.bore = Bore(
            content=dict(
                string="""
#GEFID = 1,1,0
#COLUMNTEXT = 1, aan
#COLUMNSEPARATOR = ;
#RECORDSEPARATOR = !
#FILEOWNER = DINO
#COMPANYID = Wiertsema & Partners
#FILEDATE = 2015,7,15
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
#LASTSCAN = 29
#REPORTCODE = GEF-BORE-Report,1,0,0
#MEASUREMENTCODE = Volgens GEF-BORE-Report 1.0.0,-,-,-
#TESTID = B43F1303
#XYID = 31000,99046.00,424271.00
#ZID = 31000,1.96,5.0000002E-5
#MEASUREMENTTEXT = 3, Puttershoek, plaatsnaam
#MEASUREMENTTEXT = 5, 2014-05-07, datum boorbeschrijving
#MEASUREMENTTEXT = 6, Jan Palsma, beschrijver lagen
#MEASUREMENTTEXT = 13, Wiertsema & Partners, boorbedrijf
#MEASUREMENTTEXT = 16, 2014-05-07, datum boring
#MEASUREMENTVAR = 31, 28.00, m, diepte onderkant boortraject
#MEASUREMENTVAR = 32, 168, mm, boorbuisdiameter
#MEASUREMENTTEXT = 31, PUM, boormethode
#MEASUREMENTTEXT = 11, MONB, maaiveldhoogtebepaling
#MEASUREMENTTEXT = 12, LONB, plaatsbepalingmethode
#MEASUREMENTTEXT = 7, Rijksdriehoeksmeting, locaal coördinatensysteem
#MEASUREMENTTEXT = 8, Normaal Amsterdams Peil, locaal referentiesysteem
#MEASUREMENTVAR = 16, 28.00, m, einddiepte
#MEASUREMENTTEXT = 1, Antea Group, opdrachtgever
#MEASUREMENTTEXT = 14, Nee, openbaar
#MEASUREMENTTEXT = 18, Nee, peilbuis afwezig
#MEASUREMENTVAR = 18, 1.00, m, grondwaterstand direct na boring
#EOH =
0.00;0.07;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'NBE';'NBE';'betontegel geen monster';!
0.07;0.50;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs2';'LI BR';'ZMG';'zeer veel baksteenresten';!
0.50;2.00;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs1g1';'LI BR';'ZZG';'GFN';'SCH1';'uiterst grof zandhoudend plaatselijk weinig schelprestjes opgebracht';!
2.00;3.20;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs1';'LI TGR GR';'ZMG';'SCH1';'grof zandhoudend opgebracht';!
3.20;5.10;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs2';'LI TGR GR';'ZMG';'SCH1';'plaatselijk weinig kleibrokjes grof zandhoudend opgebracht';!
5.10;6.00;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Kz1';'GR';'KSTV';'SCH1';!
6.00;8.40;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Kz3h1';'GR';'KMST';'zandgelaagd plaatselijk weinig plantenresten rietresten';!
8.40;8.50;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs1';'LI GR';'ZMG';!
8.50;8.55;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Kz3';'KMST';'weinig plantenresten houtresten';!
8.55;8.80;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs2';'LI TGR GR';'ZMG';'plaatselijk weinig plantenresten houtresten weinig kleibrokjes';!
8.80;9.00;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Ks1h3';'TGR BR';'KSTV';'plaatselijk plantenresten rietresten houtresten';!
9.00;9.90;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Vk1';'DO TBR BR';'VSTV';'houtresten';!
9.90;12.50;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Ks2h1';'TBR GR';'KSTV';'plaatselijk plantenresten rietresten veel houtresten';!
12.50;13.00;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Ks2h1';'TBR GR';'KSTV';'plaatselijk plantenresten rietresten houtresten plaatselijk grove houtresten';!
13.00;13.50;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Ks1h2';'TGR BR';'KSTV';'plaatselijk plantenresten rietresten houtresten';!
13.50;13.90;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Vk3';'DO TBR GR';'VSTV';!
13.90;15.90;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Ks2h1';'GR';'KSTV';'plaatselijk weinig plantenresten rietresten houtresten';!
15.90;16.30;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Vk3';'TGR BR';'VSTV';!
16.30;16.55;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Ks2';'GR';'KSTV';'houtresten';!
16.55;17.45;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs2';'LI TGR GR';'ZMG';'plaatselijk plantenresten houtresten rietresten';!
17.45;19.60;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs1g1';'LI TGR GR';'ZUG';'GFN';'grof zandhoudend plaatselijk weinig plantenresten rietresten houtresten';!
19.60;22.10;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs1g2';'LI TGR GR';'ZUG';'GFN';'uiterst grof/grof zandhoudend';!
22.10;23.20;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Kz2';'TGN GR';'KSTV';!
23.20;23.70;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Kz1';'TGN GR';'KZST';!
23.70;24.20;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Kz3';'GR';'KSTV';!
24.20;24.35;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs4';'GR';'ZZF';!
24.35;26.00;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Kz3';'TGN GR';'KSTV';!
26.00;26.80;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Zs3';'LI TGR GR';'ZZF';'plaatselijk kleirestje fijn zandhoudend';!
26.80;28.00;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;-9999.99;'Kz1';'TGN GR';'KZST';!
""",
                file_type="gef",
            )
        )

    def test_sum_to_one(self):
        cols = [
            "gravel_component",
            "sand_component",
            "clay_component",
            "loam_component",
            "peat_component",
            "silt_component",
        ]
        s = self.bore.df.select(
            [
                pl.fold(
                    pl.lit(0),
                    lambda a, b: a + b,
                    [
                        pl.when(pl.col(a) < 0).then(1 / len(cols)).otherwise(pl.col(a))
                        for a in cols
                    ],
                ).alias("sum")
            ]
        )
        self.assertTrue(np.all(np.isclose(s, 1)))


class PlotTest(unittest.TestCase):
    def test_plot_cpt(self):
        gef = Cpt("./pygef/test_files/example.gef")
        gef.plot(show=False)

    def test_plot_bore(self):
        gef = Bore("./pygef/test_files/example_bore.gef")
        gef.plot(show=False, figsize=(4, 12))

    def test_plot_classification(self):
        gef = Cpt("./pygef/test_files/example.gef")
        gef.plot(show=False, classification="robertson", water_level_wrt_depth=-1)

    def test_plot_classification_grouped(self):
        gef = Cpt("./pygef/test_files/cpt.gef")
        gef.plot(
            show=False,
            classification="robertson",
            do_grouping=True,
            min_thickness=0.2,
            water_level_NAP=-10,
        )


class TestRobertson(unittest.TestCase):
    def setUp(self):
        self.gef = Cpt("./pygef/test_files/example.gef")

    def test_nan_dropped(self):
        self.assertAlmostEqual(self.gef.df["qc"][0], 16.72)

    def test_water_pressure(self):
        """
        depth starts at 6 meters, So -7 should lead to water pressure of 0
        """
        df = self.gef.classify(
            "robertson", water_level_NAP=None, water_level_wrt_depth=-7
        )
        self.assertEqual(df["water_pressure"][0], 0)


class TestBoreXml(unittest.TestCase):
    def setUp(self):
        self.bore = Bore("./pygef/test_files/bore_xml/bore.xml")

    def test_bore_main_attributes(self):
        assert type(self.bore.s) == str
        assert np.isclose(self.bore.zid, 12.34)
        assert np.isclose(self.bore.x, 155197.16)
        assert np.isclose(self.bore.y, 443108.25)
        assert self.bore.file_date == datetime(2021, 9, 14).date()
        assert self.bore.test_id == "78379_HB335"

    def test_df_bore(self):

        assert self.bore.df.columns == [
            "depth_top",
            "depth_bottom",
            "soil_name",
            "gravel_component",
            "sand_component",
            "clay_component",
            "loam_component",
            "peat_component",
            "silt_component",
        ]

    def test_all_xml(self):
        path_folder = "./pygef/test_files/bore_xml/"
        for file in os.listdir(path_folder):
            if file.lower().endswith("xml"):
                bore = Bore(f"{path_folder}/{file}")
                assert {
                    "gravel_component",
                    "sand_component",
                    "clay_component",
                    "loam_component",
                    "peat_component",
                    "silt_component",
                }.issubset(set(bore.df.columns))
                bore.plot()
