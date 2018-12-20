import unittest
import pygef.utils as utils
from datetime import datetime
from pygef.gef import MAP_QUANTITY_NUMBER_COLUMN_NAME_CPT
from pygef.gef import ParseCPT as gef
from pygef.gef import ParseBORE as bore
import pandas as pd
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














