import unittest
import pygef.utils as utils
from datetime import datetime
from pygef.gef import MAP_QUANTITY_NUMBER_COLUMN_NAME
from pygef.gef import ParseGEF as gef
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
        v = utils.parse_project_type_as_int(s)
        self.assertEqual(v, 146203)

    def test_zid(self):
        s = r'#ZID= 31000, 1.3, 0.0'
        v = utils.parse_zid_as_float(s)
        self.assertEqual(v, 1.3)

    def test_proc_code(self):
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
        s = r'#COLUMN= 4'
        v = utils.parse_columns_number(s)
        self.assertEqual(v, 4)

    def test_quantity_number(self):
        s = r'#COLUMNINFO= 1, m, Sondeerlengte, 1'
        v = utils.parse_quantity_number(s,1)
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
        v = utils.parse_column_info(s, 1, MAP_QUANTITY_NUMBER_COLUMN_NAME)
        self.assertEqual(v, "penetration length")

    def test_end_of_the_header(self):
        s = r'#EOH='
        v = utils.parse_end_of_header(s)
        self.assertEqual(v, '#EOH=')

    def test_parse_data(self):
        header_s = r'This is an header'
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [1, 2, 3], 'col3': [1, 2, 3]})
        data_s = '\n1,1,1\n2,2,2\n3,3,3'.replace(',', ' ')
        path = 'just/a/path.gef'
        df_parsed = gef.parse_data(header_s, data_s, path, columns_number=3, columns_info=['col1', 'col2', 'col3'])
        assert_frame_equal(df_parsed, df)








