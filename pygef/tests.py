import unittest
import pygef.utils as utils
from datetime import datetime
from pygef.gef import MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT
from pygef.gef import ParseCPT as gef
from pygef.gef import ParseBORE as bore
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal


class GefTest(unittest.TestCase):

    def test_measurement_var_with_minus_sign(self):
        s = r'#MEASUREMENTVAR= 41, -15.000000, '
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, -15)

    def test_measurement_var_without_minus_sign(self):
        s = r'#MEASUREMENTVAR= 41, 15.000000, '
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 15)

    def test_measurement_var_integer(self):
        s = r'#MEASUREMENTVAR= 41, 0, deg, '
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0)

    def test_measurement_var_big_integer(self):
        s = r'#MEASUREMENTVAR= 41, 10000, deg, '
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 10000)

    def test_measurement_var_different_space(self):
        s = r'#MEASUREMENTVAR = 41, 0, deg, '
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0)

    def test_measurement_var_different_comma(self):
        s = r'#MEASUREMENTVAR= 41 , 0, deg, '
        v = utils.parse_measurement_var_as_float(s, 41)
        self.assertAlmostEqual(v, 0)

    def test_file_date(self):
        s = r'#FILEDATE= 2004, 1, 14'
        v = utils.parse_file_date(s)
        self.assertTrue(v.date() == datetime(2004, 1, 14).date())

    def test_project_id(self):
        s = r'#PROJECTID= CPT, 146203'
        v = utils.parse_project_type(s, "cpt")
        self.assertEqual(v, 146203)

        s = r'#PROJECTID = DINO-BOR'
        v = utils.parse_project_type(s, "bore")
        self.assertEqual(v, "DINO-BOR")

    def test_zid(self):
        s = r'#ZID= 31000, 1.3, 0.0'
        v = utils.parse_zid_as_float(s)
        self.assertEqual(v, 1.3)

    def test_parse_gef_type(self):
        s = r"#PROCEDURECODE= GEF-CPT-Report"
        v = utils.parse_gef_type(s)
        self.assertEqual(v, 'cpt')

    def test_xyid(self):
        s = r'#XYID= 31000, 132127.181, 458102.351, 0.000, 0.000'
        x = utils.parse_xid_as_float(s)
        y = utils.parse_yid_as_float(s)
        self.assertEqual(x, 132127.181)
        self.assertEqual(y, 458102.351)

    def test_columns_number(self):
        s = r"#COLUMNINFO = 1, m, Diepte bovenkant laag, 1 #COLUMNINFO = 2, m, Diepte onderkant laag, 2" \
            r"#COLUMNINFO = 3, mm, Zandmediaan, 8" \
            r"#COLUMNINFO = 4, mm, Grindmediaan, 9"
        v = utils.parse_columns_number(s)
        self.assertEqual(v, 4)

    def test_quantity_number(self):
        s = r'#COLUMNINFO= 1, m, Sondeerlengte, 1'
        v = utils.parse_quantity_number(s, 1)
        self.assertEqual(v, 1)

        s = r'#COLUMNINFO= 7, m, Gecorrigeerde diepte, 11'
        v = utils.parse_quantity_number(s, 7)
        self.assertEqual(v, 11)

        s = r'#COLUMNINFO= 4, %, Wrijvingsgetal Rf, 4'
        v = utils.parse_quantity_number(s, 4)
        self.assertEqual(v, 4)

        s = r'#COLUMNINFO= 4, Graden(deg), Helling, 8'
        v = utils.parse_quantity_number(s, 4)
        self.assertEqual(v, 8)

    def test_column_info(self):
        s = r'#COLUMNINFO= 1, m, Sondeerlengte, 1'
        v = utils.parse_column_info(s, 1, MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT)
        self.assertEqual(v, "penetration_length")

    def test_end_of_the_header(self):
        s = r'#EOH='
        v = utils.parse_end_of_header(s)
        self.assertEqual(v, '#EOH=')

    def test_parse_data(self):
        header_s = 'This is an header'
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [1, 2, 3], 'col3': [1, 2, 3]})
        data_s = '\n1,1,1\n2,2,2\n3,3,3'.replace(',', ' ')
        df_parsed = gef.parse_data(header_s, data_s, columns_number=3,
                                   columns_info=['col1', 'col2', 'col3'])
        assert_frame_equal(df_parsed, df)

    def test_parse_column_separator(self):
        s = r'#COLUMNSEPARATOR = ;'
        v = utils.parse_column_separator(s)
        self.assertEqual(v, ";")

    def test_parse_record_separator(self):
        s = r'#RECORDSEPARATOR = !'
        v = utils.parse_record_separator(s)
        self.assertEqual(v, "!")

    def test_find_separator(self):
        s = r'#COLUMNSEPARATOR = ;'
        v = utils.find_separator(s)
        self.assertEqual(v, ";")
        s = r"I'm sorry the column separator is not in this gef file, even if he wanted to be there."
        v = utils.find_separator(s)
        self.assertEqual(v, r';|\s+|,|\|\s*')

    def test_create_soil_type(self):
        s = "'Kz'"
        v = utils.create_soil_type(s)
        self.assertEqual(v, "clay 100% with sand")

    def test_parse_data_column_info(self):
        header_s = 'This is an header'
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [1, 2, 3], 'col3': [1, 2, 3]})
        data_s = '\n1;1;1\n2;2;2\n3;3;3'
        sep = ';'
        df_parsed = bore.parse_data_column_info(header_s, data_s, sep, 3,
                                                columns_info=['col1', 'col2', 'col3'])
        assert_frame_equal(df_parsed, df)

    def test_parse_data_soil_type(self):
        df = pd.DataFrame({'Soil_type': ['clay 100% with sand', 'clay 95% with sand 5%', 'clay 90% with sand 10%']})
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"], ["'Kz2'", "''"]]
        df_parsed = bore.parse_data_soil_type(data_s)
        assert_frame_equal(df_parsed, df)

    def test_parse_add_info(self):
        s = "'SCH1'"
        v = utils.parse_add_info(s)
        self.assertEqual(v, "spoor schelpmateriaal <1%|")

        s = "'DO TOL RO'"
        v = utils.parse_add_info(s)
        self.assertEqual(v, "dark olive-red|")

        s = "'BIO'"
        v = utils.parse_add_info(s)
        self.assertEqual(v, "bioturbatie|")

        s = "'KEL DR'"
        v = utils.parse_add_info(s)
        self.assertEqual(v, "keileem|Formatie van Drente|")

    def test_parse_add_info_as_string(self):
        df = pd.DataFrame({'additional_info': ['spoor schelpmateriaal <1%|', 'dark olive-red|',
                                               'keileem|Formatie van Drente|']})
        data_s = [["'Kz'", "'SCH1'", "''"], ["'Kz1'", "'DO TOL RO'", "''"], ["'Kz2'", "'KEL DR'", "''"]]
        df_parsed = bore.parse_add_info_as_string(data_s)
        assert_frame_equal(df_parsed, df)

    def test_soil_quantification(self):
        s = "'Kz'"
        v = utils.soil_quantification(s)
        self.assertEqual(v, [0, 0.05, 0.95, 0, 0, 0])

        s = "'Kz1'"
        v = utils.soil_quantification(s)
        self.assertEqual(v, [0, 0.05, 0.95, 0, 0, 0])

        s = "'Kz1s1'"
        v = utils.soil_quantification(s)
        self.assertEqual(v, [0, 0.05, 0.9, 0, 0, 0.05])

    def test_parse_data_soil_code(self):
        df = pd.DataFrame({'Soil_code': ['Kz', 'Kz1', 'Kz2']})
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"], ["'Kz2'", "''"]]
        df_parsed = bore.parse_data_soil_code(data_s)
        assert_frame_equal(df_parsed, df)

    def test_data_soil_quantified(self):
        lst = [[0, 0.05, 0.95, 0, 0, 0], [0, 0.05, 0.95, 0, 0, 0]]
        df = pd.DataFrame(lst, columns=['Gravel', 'Sand', 'Clay', 'Loam', 'Peat', 'Silt'])
        data_s = [["'Kz'", "''"], ["'Kz1'", "''"]]
        df_parsed = bore.data_soil_quantified(data_s)
        assert_frame_equal(df_parsed, df)

    def test_calculate_elevation_respect_to_NAP(self):
        df1 = pd.DataFrame({'depth': [0, 1, 2, 3, 4]})
        zid = -3
        df_calculated = gef.calculate_elevation_respect_to_nap(df1, zid)
        df = pd.DataFrame({'depth': [0, 1, 2, 3, 4], 'elevation_respect_to_NAP': [-3, -4, -5, -6, -7]})
        assert_frame_equal(df_calculated, df)

    def test_correct_depth_with_inclination(self):
        df1 = pd.DataFrame({'penetration_length': [0, 0.2, 0.4, 0.6, 0.8]})
        df_calculated = gef.correct_depth_with_inclination(df1)
        df = pd.DataFrame({'penetration_length': [0, 0.2, 0.4, 0.6, 0.8], 'depth': [0, 0.2, 0.4, 0.6, 0.8]})
        assert_frame_equal(df_calculated, df)

        df2 = pd.DataFrame({'penetration_length': [0, 0.2, 0.4, 0.6, 0.8], 'inclination': [45, 45, 45, 45, 45]})
        df_calculated = gef.correct_depth_with_inclination(df2)
        df = pd.DataFrame({'penetration_length': [0, 0.2, 0.4, 0.6, 0.8], 'inclination': [45, 45, 45, 45, 45],
                           'depth': [0.0, 0.14142135623730953, 0.28284271247461906, 0.42426406871192857, 0.5656854249492381]})
        assert_frame_equal(df_calculated, df)

        df2 = pd.DataFrame({'penetration_length': [0, 0.2, 0.4, 0.6, 0.8], 'corrected_depth':
            [0, 0.10, 0.25, 0.40, 0.60], 'inclination': [45, 45, 45, 45, 45]})
        df_calculated = gef.correct_depth_with_inclination(df2)
        df = pd.DataFrame({'penetration_length': [0, 0.2, 0.4, 0.6, 0.8], 'corrected_depth': [0, 0.10, 0.25, 0.40, 0.60],
                           'inclination': [45, 45, 45, 45, 45], 'depth': [0, 0.10, 0.25, 0.40, 0.60]})
        assert_frame_equal(df_calculated, df)

    def test_pre_excavated_depth(self):
        df1 = pd.DataFrame({'penetration_length': [0, 1, 2, 3, 4], 'qc': [0.5, 0.5, 0.6, 0.7, 0.8]})
        pre_excavated_depth = 2
        df_calculated = gef.correct_pre_excavated_depth(df1, pre_excavated_depth)
        df = pd.DataFrame({'penetration_length': [2, 3, 4], 'qc': [0.6, 0.7, 0.8]})
        assert_frame_equal(df_calculated, df)

    def test_replace_column_void(self):
        df1 = pd.DataFrame({'penetration_length': [999, 1, 2, 3, 4], 'qc': [999, 0.5, 0.6, 0.7, 0.8]})
        column_void = 999
        df_calculated = gef.replace_column_void(df1, column_void)
        df = pd.DataFrame({'penetration_length': [np.nan, 1, 2, 3, 4], 'qc': [np.nan, 0.5, 0.6, 0.7, 0.8]})
        assert_frame_equal(df_calculated, df)

    def test_calculate_friction_number(self):
        df1 = pd.DataFrame({'qc': [0.5, 0.5, 0.6, 0.7, 0.8], 'fs': [0, 0.05, 0.06, 0.07, 0.08]})
        df_calculated = gef.calculate_friction_number(df1)
        df = pd.DataFrame({'qc': [0.5, 0.5, 0.6, 0.7, 0.8], 'fs': [0, 0.05, 0.06, 0.07, 0.08], 'Fr': [0., 10., 10., 10., 10.]})
        assert_frame_equal(df_calculated, df)

    def test_parse_cpt(self):
        cpt = gef(string="""#GEFID= 1, 1, 0
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
                                 """)
        df_calculated = cpt.df
        df = pd.DataFrame({"penetration_length": [0.0000e+000, 1.0200e+000, 1.0400e+000, 1.0600e+000],
                           "qc": [0.0000e+000, 7.1000e-001, 7.3000e-001, 6.9000e-001],
                           "fs": [0.0000e+000, 4.6500e-002, 4.2750e-002, 3.9000e-002],
                           "depth": [0.0000e+000, 1.0200e+000, 1.0400e+000, 1.0600e+000],
                           'elevation_respect_to_NAP': [1.3 , 0.28, 0.26, 0.24],
                           'Fr': [np.nan, 6.54929577, 5.85616438, 5.65217391]} )
        assert_frame_equal(df_calculated, df)













