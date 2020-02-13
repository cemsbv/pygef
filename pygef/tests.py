import unittest
import pygef.utils as utils
import pygef.geo as geo
from datetime import datetime
from pygef.gef import MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT
from pygef.gef import ParseGEF, ParseCPT, ParseBORE
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal
import pygef.grouping as grouping
from pygef.grouping import GroupClassification


class GefTest(unittest.TestCase):
    def test_measurement_var_with_minus_sign(self):
        s = r"#MEASUREMENTVAR= 41, -15.000000, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, -15)

    def test_measurement_var_without_minus_sign(self):
        s = r"#MEASUREMENTVAR= 41, 15.000000, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 15)

    def test_measurement_var_integer(self):
        s = r"#MEASUREMENTVAR= 41, 0, deg, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0)

    def test_measurement_var_big_integer(self):
        s = r"#MEASUREMENTVAR= 41, 10000, deg, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 10000)

    def test_measurement_var_different_space(self):
        s = r"#MEASUREMENTVAR = 41, 0, deg, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0)

    def test_measurement_var_different_comma(self):
        s = r"#MEASUREMENTVAR= 41 , 0, deg, "
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0)

    def test_parse_cpt_class(self):
        s = r"#MEASUREMENTTEXT= 6, NEN 5140 / klasse onbekend, sondeernorm en kwaliteitsklasse"
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, None)

        s = r"#MEASUREMENTTEXT= 6, NEN-EN-ISO22476-1 / klasse 2 / TE2, gehanteerde norm en klasse en type sondering"
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, 2)

        s = r"#MEASUREMENTTEXT= 6, Norm : NEN 5140; Klasse : 2, De norm waaraan deze sondering moet voldoen."
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, 2)

        s = r"#MEASUREMENTTEXT= 6, Norm : NEN 5140; class : 2, De norm waaraan deze sondering moet voldoen."
        v = utils.parse_cpt_class(s)
        self.assertEqual(v, 2)

    def test_file_date(self):
        s = r"#FILEDATE= 2004, 1, 14"
        v = utils.parse_file_date(s)
        self.assertTrue(v.date() == datetime(2004, 1, 14).date())

    def test_project_id(self):
        s = r"#PROJECTID= CPT, 146203"
        v = utils.parse_project_type(s, "cpt")
        self.assertEqual(v, 146203)

        s = r"#PROJECTID = DINO-BOR"
        v = utils.parse_project_type(s, "bore")
        self.assertEqual(v, "DINO-BOR")

    def test_zid(self):
        s = r"#ZID= 31000, 1.3, 0.0"
        v = utils.parse_zid_as_float(s)
        self.assertEqual(v, 1.3)

    def test_parse_gef_type(self):
        s = r"#PROCEDURECODE= GEF-CPT-Report"
        v = utils.parse_gef_type(s)
        self.assertEqual(v, "cpt")

    def test_xyid(self):
        s = r"#XYID= 31000, 132127.181, 458102.351, 0.000, 0.000"
        x = utils.parse_xid_as_float(s)
        y = utils.parse_yid_as_float(s)
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

        s = r"#COLUMNINFO= 7, m, Gecorrigeerde diepte, 11"
        v = utils.parse_quantity_number(s, 7)
        self.assertEqual(v, 11)

        s = r"#COLUMNINFO= 4, %, Wrijvingsgetal Rf, 4"
        v = utils.parse_quantity_number(s, 4)
        self.assertEqual(v, 4)

        s = r"#COLUMNINFO= 4, Graden(deg), Helling, 8"
        v = utils.parse_quantity_number(s, 4)
        self.assertEqual(v, 8)

    def test_column_info(self):
        s = r"#COLUMNINFO= 1, m, Sondeerlengte, 1"
        v = utils.parse_column_info(s, 1, MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT)
        self.assertEqual(v, "penetration_length")

    def test_end_of_the_header(self):
        s = r"#EOH="
        v = utils.parse_end_of_header(s)
        self.assertEqual(v, "#EOH=")

    def test_parse_data(self):
        header_s = "This is an header"
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [1, 2, 3], "col3": [1, 2, 3]})
        data_s = "\n1,1,1\n2,2,2\n3,3,3".replace(",", " ")
        df_parsed = ParseCPT.parse_data(
            header_s, data_s, columns_number=3, columns_info=["col1", "col2", "col3"]
        )
        assert_frame_equal(df_parsed, df)

    def test_parse_column_separator(self):
        s = r"#COLUMNSEPARATOR = ;"
        v = utils.parse_column_separator(s)
        self.assertEqual(v, ";")

    def test_parse_record_separator(self):
        s = r"#RECORDSEPARATOR = !"
        v = utils.parse_record_separator(s)
        self.assertEqual(v, "!")

    def test_find_separator(self):
        s = r"#COLUMNSEPARATOR = ;"
        v = utils.find_separator(s)
        self.assertEqual(v, ";")
        s = r"I'm sorry the column separator is not in this gef file, even if he wanted to be there."
        v = utils.find_separator(s)
        self.assertEqual(v, r";|\s+|,|\|\s*")

    def test_create_soil_type(self):
        s = "'Kz'"
        v = utils.create_soil_type(s)
        self.assertEqual(v, "clay 100% with sand")

    def test_parse_data_column_info(self):
        header_s = "This is an header"
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [1, 2, 3], "col3": [1, 2, 3]})
        data_s = "\n1;1;1\n2;2;2\n3;3;3"
        sep = ";"
        df_parsed = ParseBORE.parse_data_column_info(
            header_s, data_s, sep, 3, columns_info=["col1", "col2", "col3"]
        )
        assert_frame_equal(df_parsed, df)

    def test_parse_data_soil_type(self):
        df = pd.DataFrame(
            {
                "Soil_type": [
                    "clay 100% with sand",
                    "clay 95% with sand 5%",
                    "clay 90% with sand 10%",
                ]
            }
        )
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"], ["'Kz2'", "''"]]
        df_parsed = ParseBORE.parse_data_soil_type(pd.DataFrame({}), data_s)
        assert_frame_equal(df_parsed, df)

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
        df = pd.DataFrame(
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

        df_parsed = ParseBORE.parse_add_info_as_string(pd.DataFrame({}), data_s)
        assert_frame_equal(df_parsed, df)

    def test_soil_quantification(self):
        s = "'Kz'"
        v = utils.soil_quantification(s)
        self.assertTrue(np.all(np.isclose(v, [0, 0.05, 0.95, 0, 0, 0])))

        s = "'Kz1'"
        v = utils.soil_quantification(s)
        self.assertTrue(np.all(np.isclose(v, [0, 0.05, 0.95, 0, 0, 0])))

        s = "'Kz1s1'"
        v = utils.soil_quantification(s)
        self.assertTrue(np.all(np.isclose(v, [0, 0.05, 0.9, 0, 0, 0.05])))

    def test_parse_data_soil_code(self):
        df = pd.DataFrame({"Soil_code": ["Kz", "Kz1", "Kz2"]})
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"], ["'Kz2'", "''"]]
        df_parsed = ParseBORE.parse_data_soil_code(pd.DataFrame({}), data_s)
        assert_frame_equal(df_parsed, df)

    def test_data_soil_quantified(self):
        lst = [[0, 0.05, 0.95, 0, 0, 0], [0, 0.05, 0.95, 0, 0, 0]]
        df = pd.DataFrame(
            lst, columns=["Gravel", "Sand", "Clay", "Loam", "Peat", "Silt"], dtype=float
        )
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"]]
        df_parsed = ParseBORE.data_soil_quantified(data_s)
        assert_frame_equal(df_parsed, df)

    def test_calculate_elevation_respect_to_NAP(self):
        df1 = pd.DataFrame({"depth": [0, 1, 2, 3, 4]})
        zid = -3
        df_calculated = ParseCPT.calculate_elevation_with_respect_to_nap(
            df1, zid, 31000
        )
        df = pd.DataFrame(
            {
                "depth": [0, 1, 2, 3, 4],
                "elevation_with_respect_to_NAP": [-3, -4, -5, -6, -7],
            }
        )
        assert_frame_equal(df_calculated, df)

    def test_correct_depth_with_inclination(self):
        df1 = pd.DataFrame({"penetration_length": [0, 0.2, 0.4, 0.6, 0.8]})
        df_calculated = ParseCPT.correct_depth_with_inclination(df1)
        df = pd.DataFrame(
            {
                "penetration_length": [0, 0.2, 0.4, 0.6, 0.8],
                "depth": [0, 0.2, 0.4, 0.6, 0.8],
            }
        )
        assert_frame_equal(df_calculated, df)

        df2 = pd.DataFrame(
            {
                "penetration_length": [0, 0.2, 0.4, 0.6, 0.8],
                "inclination": [45, 45, 45, 45, 45],
            }
        )
        df_calculated = ParseCPT.correct_depth_with_inclination(df2)
        df = pd.DataFrame(
            {
                "penetration_length": [0, 0.2, 0.4, 0.6, 0.8],
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
        assert_frame_equal(df_calculated, df)

        df2 = pd.DataFrame(
            {
                "penetration_length": [0, 0.2, 0.4, 0.6, 0.8],
                "corrected_depth": [0, 0.10, 0.25, 0.40, 0.60],
                "inclination": [45, 45, 45, 45, 45],
            }
        )
        df_calculated = ParseCPT.correct_depth_with_inclination(df2)
        df = pd.DataFrame(
            {
                "penetration_length": [0, 0.2, 0.4, 0.6, 0.8],
                "depth": [0, 0.10, 0.25, 0.40, 0.60],
                "inclination": [45, 45, 45, 45, 45],
            }
        )
        assert_frame_equal(df_calculated, df)

    def test_pre_excavated_depth(self):
        df1 = pd.DataFrame(
            {"penetration_length": [0, 1, 2, 3, 4], "qc": [0.5, 0.5, 0.6, 0.7, 0.8]}
        )
        pre_excavated_depth = 2
        df_calculated = ParseCPT.correct_pre_excavated_depth(df1, pre_excavated_depth)
        df = pd.DataFrame({"penetration_length": [2, 3, 4], "qc": [0.6, 0.7, 0.8]})
        assert_frame_equal(df_calculated, df)

    def test_replace_column_void(self):
        df1 = pd.DataFrame(
            {"penetration_length": [999, 1, 2, 3, 4], "qc": [999, 0.5, 0.6, 0.7, 0.8]}
        )
        column_void = 999
        df_calculated = ParseCPT.replace_column_void(df1, column_void)
        df = pd.DataFrame(
            {
                "penetration_length": [np.nan, 1, 2, 3, 4],
                "qc": [np.nan, 0.5, 0.6, 0.7, 0.8],
            }
        )
        assert_frame_equal(df_calculated, df)

    def test_calculate_friction_number(self):
        df1 = pd.DataFrame(
            {"qc": [0.5, 0.5, 0.6, 0.7, 0.8], "fs": [0, 0.05, 0.06, 0.07, 0.08]}
        )
        df_calculated = ParseCPT.calculate_friction_number(df1)
        df = pd.DataFrame(
            {
                "qc": [0.5, 0.5, 0.6, 0.7, 0.8],
                "fs": [0, 0.05, 0.06, 0.07, 0.08],
                "friction_number": [0.0, 10.0, 10.0, 10.0, 10.0],
            }
        )
        assert_frame_equal(df_calculated, df)

    def test_parse_cpt(self):
        cpt = ParseGEF(
            string="""#GEFID= 1, 1, 0
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
        df_calculated = cpt.df
        df = pd.DataFrame(
            {
                "penetration_length": [1.0200e000, 1.0400e000, 1.0600e000],
                "qc": [7.1000e-001, 7.3000e-001, 6.9000e-001],
                "fs": [4.6500e-002, 4.2750e-002, 3.9000e-002],
                "depth": [1.0200e000, 1.0400e000, 1.0600e000],
                "elevation_with_respect_to_NAP": [0.28, 0.26, 0.24],
                "friction_number": [6.54929577, 5.85616438, 5.65217391],
            }
        )
        assert_frame_equal(df_calculated, df)

    def test_parse_bore(self):
        cpt = ParseGEF(
            string="""#GEFID = 1,1,0
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
        df_calculated = cpt.df
        df = pd.DataFrame(
            {
                "depth_top": [0.0, 1.2, 3.1],
                "depth_bottom": [1.2, 3.1, 5.0],
                "soil_code": ["Zgh2", "Zg", "Vz"],
                "G": [0.05, 0.05, 0.00],
                "S": [0.85, 0.95, 0.05],
                "C": [0, 0, 0],
                "L": [0, 0, 0],
                "P": [0.10, 0.00, 0.95],
                "SI": [0, 0, 0],
                "Remarks": [
                    "1) gray-yellow 2) ZMFO 3) kalkrijk ",
                    "1) ON 2) ZMGO 3) weinig fijn grind (1-25%) 4) kalkarm ",
                    "1) brown-black 2) ZMO 3) kalkloos ",
                ],
            },
            dtype=float,
        )
        assert_frame_equal(df_calculated, df)

    def test_delta_depth(self):
        df1 = pd.DataFrame({"depth": [0, 0.5, 1]})
        v = geo.delta_depth(df1)
        df = pd.DataFrame({"depth": [0, 0.5, 1], "delta_depth": [0, 0.5, 0.5]})
        assert_frame_equal(v, df)

    def test_soil_pressure(self):
        df1 = pd.DataFrame({"gamma": [0, 0.5, 1], "delta_depth": [0, 0.5, 0.5]})
        v = geo.soil_pressure(df1)
        df = pd.DataFrame(
            {
                "gamma": [0, 0.5, 1],
                "delta_depth": [0, 0.5, 0.5],
                "soil_pressure": [0.0, 0.25, 0.75],
            }
        )
        assert_frame_equal(v, df)

    def test_water_pressure(self):
        water_level = 0.5
        df1 = pd.DataFrame({"depth": [0, 0.5, 1]})
        v = geo.water_pressure(df1, water_level)
        df = pd.DataFrame({"depth": [0, 0.5, 1], "water_pressure": [0.0, 0.0, 4.905]})
        assert_frame_equal(v, df)

    def test_effective_soil_pressure(self):
        df1 = pd.DataFrame(
            {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
        )
        v = geo.effective_soil_pressure(df1)
        df = pd.DataFrame(
            {
                "soil_pressure": [0.0, 0.25, 0.75],
                "water_pressure": [0.0, 0.0, 4.905],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
            }
        )
        assert_frame_equal(v, df)

    def test_assign_multiple_columns(self):
        df1 = pd.DataFrame(
            {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
        )
        v = utils.assign_multiple_columns(df1, ["soil_pressure", "water_pressure"], df1)
        df = pd.DataFrame(
            {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
        )
        assert_frame_equal(v, df)

    def test_kpa_to_mpa(self):
        df1 = pd.DataFrame(
            {"soil_pressure": [0.0, 0.25, 0.75], "water_pressure": [0.0, 0.0, 4.905]}
        )
        v = utils.kpa_to_mpa(df1, ["soil_pressure", "water_pressure"])
        df = pd.DataFrame(
            {
                "soil_pressure": [0.0, 0.00025, 0.00075],
                "water_pressure": [0.0, 0.0, 0.004905],
            }
        )
        assert_frame_equal(v, df)

    def test_qt(self):
        df1 = pd.DataFrame({"qc": [0.0, 1, 2], "u2": [0, 1, 1]})
        v = geo.qt(df1, area_quotient_cone_tip=0.5)
        df = pd.DataFrame({"qc": [0.0, 1, 2], "u2": [0, 1, 1], "qt": [0.0, 1.5, 2.5]})
        assert_frame_equal(v, df)

    def test_normalized_cone_resistance(self):
        df1 = pd.DataFrame(
            {
                "qt": [0.0, 1.5, 2.5],
                "soil_pressure": [0.0, 0.25, 0.75],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
            }
        )
        v = geo.normalized_cone_resistance(df1)
        df = pd.DataFrame(
            {
                "qt": [0.0, 1.5, 2.5],
                "soil_pressure": [0.0, 0.25, 0.75],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
                "normalized_cone_resistance": [np.nan, 5.0, 1.0],
            }
        )
        assert_frame_equal(v, df)

    def test_normalized_friction_ratio(self):
        df1 = pd.DataFrame(
            {
                "qt": [0.0, 1.5, 2.5],
                "fs": [0.5, 0.5, 0.5],
                "soil_pressure": [0.0, 0.25, 0.75],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
            }
        )
        v = geo.normalized_friction_ratio(df1)
        df = pd.DataFrame(
            {
                "qt": [0.0, 1.5, 2.5],
                "fs": [0.5, 0.5, 0.5],
                "soil_pressure": [0.0, 0.25, 0.75],
                "effective_soil_pressure": [0.0, 0.25, -4.155],
                "normalized_friction_ratio": [np.inf, 40.0, 28.57142857142857],
            }
        )
        assert_frame_equal(v, df)

    def test_nan_to_zero(self):
        df1 = pd.DataFrame({"type_index": [np.nan]})
        v = utils.nan_to_zero(df1)
        df = pd.DataFrame({"type_index": [0.0]})
        assert_frame_equal(v, df)

    def test_group_equal_layers(self):
        df_group = pd.DataFrame(
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
                "elevation_with_respect_to_NAP": [2, 1, 0, -1, -2, -3, -4],
            }
        )
        group = GroupClassification(2, df_group, 0.2)
        v = group.group_equal_layers(df_group, "soil_type", "depth", 0)
        df = pd.DataFrame(
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
        assert_frame_equal(v, df)

    def test_group_significant_layers(self):
        df_group = pd.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 0.4, 5.0],
                "zf": [0.4, 5, 6],
                "thickness": [0.4, 4.6, 1.0],
            }
        )

        v = grouping.group_significant_layers(df_group, 0.5, 0.0)

        df = pd.DataFrame(
            {
                "layer": ["Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 5.0],
                "zf": [5.0, 6.0],
                "thickness": [5.0, 1.0],
                "z_centr": [2.5, 5.5],
            }
        )
        assert_frame_equal(v, df)

    def test_calculate_thickness(self):
        df_group = pd.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 0.4, 5.0],
                "zf": [0.4, 5, 6],
            }
        )
        v = grouping.calculate_thickness(df_group)
        df = pd.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 0.4, 5.0],
                "zf": [0.4, 5, 6],
                "thickness": [0.4, 4.6, 1.0],
            }
        )
        assert_frame_equal(v, df)

    def test_calculate_z_centr(self):
        df_group = pd.DataFrame(
            {
                "layer": ["Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 5.0],
                "zf": [5.0, 6.0],
            }
        )
        v = grouping.calculate_z_centr(df_group)
        df = pd.DataFrame(
            {
                "layer": ["Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 5.0],
                "zf": [5.0, 6.0],
                "z_centr": [2.5, 5.5],
            }
        )
        assert_frame_equal(v, df)

    def test_calculate_zf_NAP(self):
        df_group = pd.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 2.0, 5.0],
                "zf": [2, 5, 6],
                "thickness": [2.0, 3.0, 1.0],
                "z_centr": [1.0, 3.5, 5.5],
            }
        )

        v = grouping.calculate_zf_NAP(df_group, 2)

        df = pd.DataFrame(
            {
                "layer": ["Peat", "Silt mixtures - clayey silt to silty clay", "Sand"],
                "z_in": [0.0, 2.0, 5.0],
                "zf": [2, 5, 6],
                "thickness": [2.0, 3.0, 1.0],
                "z_centr": [1.0, 3.5, 5.5],
                "zf_NAP": [0, -3, -4],
            }
        )
        assert_frame_equal(v, df)


class BoreTest(unittest.TestCase):
    def setUp(self):
        self.bore = ParseGEF(
            string="""#GEFID = 1,1,0
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
"""
        )

    def test_sum_to_one(self):
        df = self.bore.df[["G", "S", "C", "L", "P", "SI"]].sum(1)
        df[df < 0] = 1.0
        self.assertTrue(np.all(np.isclose(df.values, 1)))


class PlotTest(unittest.TestCase):
    def test_plot_cpt(self):
        gef = ParseGEF("./pygef/files/example.gef")
        gef.plot(show=False)

    def test_plot_bore(self):
        gef = ParseGEF("./pygef/files/example_bore.gef")
        gef.plot(show=False, figsize=(4, 12))

    def test_plot_classification(self):
        gef = ParseGEF("./pygef/files/example.gef")
        gef.plot(show=False, classification="robertson", water_level_wrt_depth=-1)


class TestRobertson(unittest.TestCase):
    def setUp(self):
        self.gef = ParseGEF("./pygef/files/example.gef")

    def test_nan_dropped(self):
        self.assertAlmostEqual(self.gef.df["qc"].iloc[0], 16.72)

    def test_water_pressure(self):
        """
        depth starts at 6 meters, So -7 should lead to water pressure of 0
        """
        df = self.gef.classify(
            "robertson", water_level_NAP=None, water_level_wrt_depth=-7
        )
        self.assertEqual(df["water_pressure"][0], 0)
