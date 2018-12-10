import unittest
import pygef.utils as utils
from datetime import datetime


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



