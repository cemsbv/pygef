import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal
from pygef.robertson import RobertsonClassifier as rob
from pygef.gef import ParseCPT


class RobertsonTest(unittest.TestCase):

    def setUp(self):
        self.gef = ParseCPT(string="""#GEFID= 1, 1, 0
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

    def test_hydrostatic_water_pressure(self):
        water_level = 1
        depth = pd.Series([0, 0.5, 1, 1.5, 2])
        hydrostatic_water_pressure_calc = rob.hydrostatic_water_pressure(water_level, depth)
        hydrostatic_water_pressure = [0, 0, 0, 4.905, 9.81]
        self.assertEqual(hydrostatic_water_pressure_calc, hydrostatic_water_pressure)

    def test_type_index_to_gamma(self):
        ic = 3.6
        gamma_calc = rob.type_index_to_gamma(ic)
        gamma = 16
        self.assertEqual(gamma_calc, gamma)

    def test_type_index_to_gamma_sat(self):
        ic = 3.6
        gamma_calc = rob.type_index_to_gamma_sat(ic)
        gamma = 16
        self.assertEqual(gamma_calc, gamma)

    def test_get_gamma(self):
        obj = rob(self.gef)
        obj.water_level = 1
        ic = 3.6
        depth = 2
        gamma_calc = rob.get_gamma(obj, ic, depth)
        gamma = 16
        self.assertEqual(gamma_calc, gamma)

    def test_type_index_to_soil_type(self):
        ic = 2.70
        soil_type_calc = rob.type_index_to_soil_type(ic)
        soil_type = 'Silt mixtures - clayey silt to silty clay'
        self.assertEqual(soil_type_calc, soil_type)

    def test_effective_stress(self):
        sigma_v0 = 10
        u = 3
        eff_stress_calc = rob.effective_stress(sigma_v0, u)
        eff_stress = 7
        self.assertEqual(eff_stress_calc, eff_stress)

    def test_normalized_cone_resistance(self):
        obj = rob(self.gef)
        qt = 2
        sigma_v0 = 1000  # kPa
        u = 0.5
        normalized_cone_resistance_calc = rob.normalized_cone_resistance(obj, qt, sigma_v0, u)
        normalized_cone_resistance = 1.0005002501250624
        self.assertEqual(normalized_cone_resistance_calc, normalized_cone_resistance)

    def test_n_exponent(self):
        obj = rob(self.gef)
        Ic = 2
        sigma_v0 = 1000
        p_a = 0.1
        u = 500
        n_exp_calc = rob.n_exponent(obj, Ic, sigma_v0, p_a, u)
        n_exp = 0.862
        self.assertEqual(n_exp_calc, n_exp)

    def test_normalized_cone_resistance_n(self):
        qt = 2
        sigma_v0 = 1000  # kPa
        sigma_v0_eff = 500
        n = 1
        p_a = 0.1
        normalized_cone_resistance_calc = rob.normalized_cone_resistance_n(qt, sigma_v0, sigma_v0_eff, n, p_a)
        normalized_cone_resistance = 2.0
        self.assertEqual(normalized_cone_resistance_calc, normalized_cone_resistance)

    def test_normalized_friction_ratio(self):
        fs = 0.3
        qt = 2
        sigma_v0 = 1000
        normalized_fs_calc = rob.normalized_friction_ratio(fs, qt, sigma_v0)
        normalized_fs = 30.0
        self.assertEqual(normalized_fs_calc, normalized_fs)

    def test_delta_vertical_stress(self):
        depth1 = 1
        depth2 = 1.5
        gamma = 18
        delta_vertical_stress_calc = rob.delta_vertical_stress(depth1, depth2, gamma)
        delta_vertical_stress = 9
        self.assertEqual(delta_vertical_stress_calc, delta_vertical_stress)

    def test_vertical_stress(self):
        sig0 = 1000
        delta_sigma_v0 = 200
        vertical_stress_calc = rob.vertical_stress(sig0, delta_sigma_v0)
        vertical_stress = 1200
        self.assertEqual(vertical_stress_calc, vertical_stress)

    def test_type_index(self):
        obj = rob(self.gef)
        fs = 0.5
        qt = 2
        sigma_v0 = 1000
        u = 500
        type_index_calc = rob.type_index(obj, fs, qt, sigma_v0, u)
        type_index = 4.308451783946856
        self.assertEqual(type_index_calc, type_index)

    def test_type_index_n(self):
        obj = rob(self.gef)
        fs = 0.5
        qt = 2
        sigma_v0 = 1000
        u = 500
        n = 0.8
        p_a = 0.1
        type_index_calc = rob.type_index_n(obj, fs, qt, sigma_v0, u, n, p_a)
        type_index = 4.206696226993901
        self.assertEqual(type_index_calc, type_index)

    def test_classify(self):
        obj = rob(self.gef)
        df_calc = rob.classify(obj)
        df = pd.DataFrame({'penetration_length':
                            [0.0000e+000, 1.0200e+000, 1.0400e+000, 1.0600e+000, 1.0800e+000, 1.1200e+000],
                           'qc': [0.0000e+000, 7.1000e-001, 7.3000e-001, 6.9000e-001, 6.1000e-001, 6.5000e-001],
                           'fs': [0.0000e+000, 4.6500e-002, 4.2750e-002, 3.9000e-002, 3.6500e-002, 4.5500e-002],
                           'depth': [0.0000e+000, 1.0200e+000, 1.0400e+000, 1.0600e+000, 1.0800e+000, 1.1200e+000],
                           'elevation_respect_to_NAP': [1.3, 0.28, 0.26, 0.24, 0.22, 0.17999999999999994],
                           'hydrostatic_pore_pressure': [0, 0, 0, 0, 0, 0],
                           'Ic': [3.476967069156681, 2.822213205390442, 2.7902205405302007, 2.800900469717346,
                                  2.853978458064875, 2.886830989476405],
                           'soil_type_Robertson': ['Clays - silty clay to clay',
                                                   'Silt mixtures - clayey silt to silty clay',
                                                   'Silt mixtures - clayey silt to silty clay',
                                                   'Silt mixtures - clayey silt to silty clay',
                                                   'Silt mixtures - clayey silt to silty clay',
                                                   'Silt mixtures - clayey silt to silty clay'],
                           'normalized_Qt': [1, 1, 1, 1, 1, 1],
                           'normalized_Fr': [0.10, 6.723150772077961, 6.010291305814869, 5.812913611160794,
                                             6.180574370089407, 7.2240569033405295]})
        assert_frame_equal(df_calc, df)


