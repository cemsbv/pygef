import unittest
from pygef.gef import ParseGEF
import pygef.robertson.util as util
import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np


class RobertsonTest(unittest.TestCase):
    def setUp(self):
        self.gef = ParseGEF(string="""#GEFID= 1, 1, 0
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
                                    1.0800e+000 6.1000e-001 3.6500e-002 
                                    1.1200e+000 6.5000e-001 4.5500e-002                                    
                                    """)

    def test_n_exponent(self):
        df1 = pd.DataFrame({'type_index_n': [1, 1, 1], 'effective_soil_pressure': [0.001, 0.002, 0.003]})
        p_a = 0.1
        v = util.n_exponent(df1, p_a)
        df = pd.DataFrame({'type_index_n': [1, 1, 1], 'effective_soil_pressure': [0.001, 0.002, 0.003],
                           'n': [0.2315, 0.2320, 0.2325]})
        assert_frame_equal(v, df)

    def test_normalized_cone_resistance_n(self):
        df1 = pd.DataFrame({'qt': [1, 1, 1], 'soil_pressure': [0.002, 0.003, 0.004],
                           'effective_soil_pressure': [0.001, 0.002, 0.003], 'n': [0.2315, 0.2320, 0.2325]})
        p_a = 0.1
        v = util.normalized_cone_resistance_n(df1, p_a)
        df = pd.DataFrame({'qt': [1, 1, 1], 'soil_pressure': [0.002, 0.003, 0.004],
                           'effective_soil_pressure': [0.001, 0.002, 0.003],
                           'n': [0.2315, 0.2320, 0.2325],
                           'normalized_cone_resistance': [28.982146, 24.709059, 22.507572]})
        assert_frame_equal(v, df)

    def test_type_index(self):
        df1 = pd.DataFrame({'normalized_cone_resistance': [28.982146, 24.709059, 22.507572],
                            'normalized_friction_ratio': [0.5, 1, 4]})
        v = util.type_index(df1)
        df = pd.DataFrame({'normalized_cone_resistance': [28.982146, 24.709059, 22.507572],
                            'normalized_friction_ratio': [0.5, 1, 4],
                           'type_index': [2.208177, 2.408926, 2.793642]})
        assert_frame_equal(v, df)

    def test_ic_to_gamma(self):
        water_level = - 0.5
        df1 = pd.DataFrame({'type_index': [2.208177, 2.408926, 2.793642],
                            'depth': [0.5, 1, 4]})
        v = util.ic_to_gamma(df1, water_level)
        df = pd.DataFrame({'type_index': [2.208177, 2.408926, 2.793642],
                            'depth': [0.5, 1, 4],
                            'gamma_predict': [18, 18, 18]})
        assert_frame_equal(v, df)

    def test_ic_to_soil_type(self):
        df1 = pd.DataFrame({'type_index': [2.208177, 2.408926, 2.793642]})
        v = util.ic_to_soil_type(df1)
        df = pd.DataFrame({'type_index': [2.208177, 2.408926, 2.793642],

                           'soil_type': ['Sand mixtures - silty sand to sandy silt',
                                         'Sand mixtures - silty sand to sandy silt',
                                         'Silt mixtures - clayey silt to silty clay']})
        assert_frame_equal(v, df)

    def test_nan_to_zero(self):
        df1 = pd.DataFrame({'type_index': [np.nan]})
        v = util.nan_to_zero(df1)
        df = pd.DataFrame({'type_index': [0]})
        assert_frame_equal(v, df)

    def test_type_index_to_gamma(self):
        ic = 3.6
        gamma_calc = util.type_index_to_gamma(ic)
        gamma = 16
        self.assertEqual(gamma_calc, gamma)

    def test_type_index_to_gamma_sat(self):
        ic = 3.6
        gamma_calc = util.type_index_to_gamma_sat(ic)
        gamma = 16
        self.assertEqual(gamma_calc, gamma)

    def test_type_index_to_soil_type(self):
        ic = 2.70
        soil_type_calc = util.type_index_to_soil_type(ic)
        soil_type = 'Silt mixtures - clayey silt to silty clay'
        self.assertEqual(soil_type_calc, soil_type)

    def test_old_robertson(self):
        water_level = -0.5
        df1 = pd.DataFrame({'qc': [1, 1, 1],
                            'fs': [0.5, 0.5, 0.5],
                            'depth': [0, 0.5, 1],
                            'gamma': [18, 18, 18]})
        v = util.old_robertson(df1, water_level)

        df = pd.DataFrame({'qc': [1, 1, 1],
                           'fs': [0.5, 0.5, 0.5],
                           'depth': [0, 0.5, 1],
                           'gamma': [18, 18, 18],
                           'delta_depth': [0.0, 0.5, 0.5],
                           'soil_pressure': [0., 0.009, 0.0180],
                           'qt': [1, 1, 1],
                           'water_pressure': [0.0049050000000000005, 0.009810000000000001, 0.014715],
                           'effective_soil_pressure': [-0.0049050000000000005, -0.0008100000000000005, 0.003285],
                           'normalized_cone_resistance': [1.0, 1.0, 298.9345509893455],
                           'normalized_friction_ratio': [50.0, 50.45408678102926, 50.91649694501018],
                           'type_index': [4.534455412308453, 4.536983917975774, 3.0911777110285397],
                           'gamma_predict': [11, 11, 16]
                           })

        assert_frame_equal(v, df)

    def test_new_robertson(self):
        water_level = -0.5
        df1 = pd.DataFrame({'qc': [1, 1, 1],
                            'fs': [0.5, 0.5, 0.5],
                            'depth': [0, 0.5, 1],
                            'gamma': [18, 18, 18],
                            'n': [1, 1, 1],
                            'type_index_n': [1, 1, 1]})
        v = util.new_robertson(df1, water_level)

        df = pd.DataFrame({'qc': [1, 1, 1],
                           'fs': [0.5, 0.5, 0.5],
                           'depth': [0, 0.5, 1],
                           'gamma': [18, 18, 18],
                           'n': [0.2285475, 0.23059500000000002, 0.2326425],
                           'type_index_n': [1, 1, 1],
                           'delta_depth': [0.0, 0.5, 0.5],
                           'soil_pressure': [0., 0.009, 0.0180],
                           'qt': [1, 1, 1],
                           'water_pressure': [0.0049050000000000005, 0.009810000000000001, 0.014715],
                           'effective_soil_pressure': [-0.0049050000000000005, -0.0008100000000000005, 0.003285],
                           'normalized_cone_resistance': [0, 0, 21.73844],
                           'normalized_friction_ratio': [50.0, 50.45408678102926, 50.91649694501018],
                           'type_index': [np.inf, np.inf, 3.6214935376891986],
                           'gamma_predict': [11, 11, 11]
                           })

        assert_frame_equal(v, df)

    def test_iterate_robertson(self):
        water_level = - 0.5
        df1 = pd.DataFrame({'qc': [1, 1, 1],
                            'fs': [0.5, 0.5, 0.5],
                            'depth': [0, 0.5, 1],
                            'gamma': [18, 18, 18],
                            'n': [1, 1, 1],
                            'type_index_n': [1, 1, 1]})
        v = util.iterate_robertson(df1, water_level)

        df = pd.DataFrame({'qc': [1, 1, 1],
                           'fs': [0.5, 0.5, 0.5],
                           'depth': [0, 0.5, 1],
                           'gamma': [11, 11, 11],
                           'n': [0.2285475, 0.228845, 0.2291425],
                           'type_index_n': [1.0, 1.0, 1.0],
                           'delta_depth': [0.0, 0.5, 0.5],
                           'soil_pressure': [0., 0.00550, 0.0110],
                           'qt': [1, 1, 1],
                           'water_pressure': [0.0049050000000000005, 0.009810000000000001, 0.014715],
                           'effective_soil_pressure': [-0.0049050000000000005, -0.0043100000000000005, -0.003715],
                           'normalized_cone_resistance': [0., 0., 0.],
                           'normalized_friction_ratio': [50.0, 50.27652086475616, 50.55611729019211],
                           'type_index': [np.inf, np.inf, np.inf],
                           'gamma_predict': [11, 11, 11],
                           'soil_type': ['Peat', 'Peat', 'Peat']
                           })

        assert_frame_equal(v, df)

