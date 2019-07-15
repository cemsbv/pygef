import unittest
import pygef.robertson.util as util
import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np


class RobertsonTest(unittest.TestCase):
    def test_n_exponent(self):
        df1 = pd.DataFrame(
            {
                "type_index_n": [1, 1, 1],
                "effective_soil_pressure": [0.001, 0.002, 0.003],
            }
        )
        p_a = 0.1
        v = util.n_exponent(df1, p_a)
        df = pd.DataFrame(
            {
                "type_index_n": [1, 1, 1],
                "effective_soil_pressure": [0.001, 0.002, 0.003],
                "n": [0.2315, 0.2320, 0.2325],
            }
        )
        assert_frame_equal(v, df)

    def test_normalized_cone_resistance_n(self):
        df1 = pd.DataFrame(
            {
                "qt": [1, 1, 1],
                "soil_pressure": [0.002, 0.003, 0.004],
                "effective_soil_pressure": [0.001, 0.002, 0.003],
                "n": [0.2315, 0.2320, 0.2325],
            }
        )
        p_a = 0.1
        v = util.normalized_cone_resistance_n(df1, p_a)
        df = pd.DataFrame(
            {
                "qt": [1, 1, 1],
                "soil_pressure": [0.002, 0.003, 0.004],
                "effective_soil_pressure": [0.001, 0.002, 0.003],
                "n": [0.2315, 0.2320, 0.2325],
                "normalized_cone_resistance": [28.982146, 24.709059, 22.507572],
            }
        )
        assert_frame_equal(v, df)

    def test_type_index(self):
        df1 = pd.DataFrame(
            {
                "normalized_cone_resistance": [28.982146, 24.709059, 22.507572],
                "normalized_friction_ratio": [0.5, 1, 4],
            }
        )
        v = util.type_index(df1)
        df = pd.DataFrame(
            {
                "normalized_cone_resistance": [28.982146, 24.709059, 22.507572],
                "normalized_friction_ratio": [0.5, 1, 4],
                "type_index": [2.208177, 2.408926, 2.793642],
            }
        )
        assert_frame_equal(v, df)

    def test_ic_to_gamma(self):
        water_level = 0.5  # gammas:    19       19       18
        df1 = pd.DataFrame(
            {"type_index": [2.208177, 2.408926, 2.793642], "depth": [0.5, 1, 4]}
        )
        v = util.ic_to_gamma(df1, water_level)
        df = pd.DataFrame(
            {
                "type_index": [2.208177, 2.408926, 2.793642],
                "depth": [0.5, 1, 4],
                "gamma_predict": [19, 19, 18],
            }
        )
        assert_frame_equal(v, df)

    def test_ic_to_soil_type(self):
        df1 = pd.DataFrame({"type_index": [2.208177, 2.408926, 2.793642]})
        v = util.ic_to_soil_type(df1)
        df = pd.DataFrame(
            {
                "type_index": [2.208177, 2.408926, 2.793642],
                "soil_type": [
                    "Sand mixtures - silty sand to sandy silt",
                    "Sand mixtures - silty sand to sandy silt",
                    "Silt mixtures - clayey silt to silty clay",
                ],
            }
        )
        assert_frame_equal(v, df)

    def test_old_robertson(self):
        water_level = -0.5
        df1 = pd.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "depth": [0, 0.5, 1],
                "gamma": [18, 18, 18],
            }
        )
        v = util.old_robertson(df1, water_level)

        df = pd.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "depth": [0, 0.5, 1],
                "gamma": [18, 18, 18],
                "delta_depth": [0.0, 0.5, 0.5],
                "soil_pressure": [0.0, 0.009, 0.0180],
                "qt": [1, 1, 1],
                "water_pressure": [
                    0.0049050000000000005,
                    0.009810000000000001,
                    0.014715,
                ],
                "effective_soil_pressure": [
                    -0.0049050000000000005,
                    -0.0008100000000000005,
                    0.003285,
                ],
                "normalized_cone_resistance": [1.0, 1.0, 298.9345509893455],
                "normalized_friction_ratio": [
                    50.0,
                    50.45408678102926,
                    50.91649694501018,
                ],
                "type_index": [
                    4.534455412308453,
                    4.536983917975774,
                    3.0911777110285397,
                ],
                "gamma_predict": [11, 11, 16],
            }
        )

        assert_frame_equal(v, df)

    def test_new_robertson(self):
        water_level = -0.5
        df1 = pd.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "depth": [0, 0.5, 1],
                "gamma": [18, 18, 18],
                "n": [1, 1, 1],
                "type_index_n": [1, 1, 1],
            }
        )
        v = util.new_robertson(df1, water_level)

        df = pd.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "depth": [0, 0.5, 1],
                "gamma": [18, 18, 18],
                "n": [0.2285475, 0.23059500000000002, 0.2326425],
                "type_index_n": [1, 1, 1],
                "delta_depth": [0.0, 0.5, 0.5],
                "soil_pressure": [0.0, 0.009, 0.0180],
                "qt": [1, 1, 1],
                "water_pressure": [
                    0.0049050000000000005,
                    0.009810000000000001,
                    0.014715,
                ],
                "effective_soil_pressure": [
                    -0.0049050000000000005,
                    -0.0008100000000000005,
                    0.003285,
                ],
                "normalized_cone_resistance": [0, 0, 21.73844],
                "normalized_friction_ratio": [
                    50.0,
                    50.45408678102926,
                    50.91649694501018,
                ],
                "type_index": [np.inf, np.inf, 3.6214935376891986],
                "gamma_predict": [11, 11, 11],
            }
        )

        assert_frame_equal(v, df)

    def test_iterate_robertson(self):
        water_level = -0.5
        df1 = pd.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "depth": [0, 0.5, 1],
                "gamma": [18, 18, 18],
                "n": [1, 1, 1],
                "type_index_n": [1, 1, 1],
            }
        )
        v = util.iterate_robertson(df1, water_level)

        df = pd.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "depth": [0, 0.5, 1],
                "gamma": [11, 11, 11],
                "n": [0.2285475, 0.228845, 0.2291425],
                "type_index_n": [1.0, 1.0, 1.0],
                "delta_depth": [0.0, 0.5, 0.5],
                "soil_pressure": [0.0, 0.00550, 0.0110],
                "qt": [1, 1, 1],
                "water_pressure": [
                    0.0049050000000000005,
                    0.009810000000000001,
                    0.014715,
                ],
                "effective_soil_pressure": [
                    -0.0049050000000000005,
                    -0.0043100000000000005,
                    -0.003715,
                ],
                "normalized_cone_resistance": [0.0, 0.0, 0.0],
                "normalized_friction_ratio": [
                    50.0,
                    50.27652086475616,
                    50.55611729019211,
                ],
                "type_index": [np.inf, np.inf, np.inf],
                "gamma_predict": [11, 11, 11],
                "soil_type": ["Peat", "Peat", "Peat"],
            }
        )

        assert_frame_equal(v, df)
