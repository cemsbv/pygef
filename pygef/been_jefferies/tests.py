import unittest

import polars as pl
import pygef.been_jefferies.util as util


class BeenJeffreyTest(unittest.TestCase):
    def test_type_index(self):
        df1 = pl.DataFrame(
            {
                "normalized_cone_resistance": [28.982146, 24.709059, 22.507572],
                "normalized_friction_ratio": [0.5, 1, 4],
                "excess_pore_pressure_ratio": [0.5, 0.5, 0.5],
            }
        )
        v = df1.with_column(util.type_index())
        df = pl.DataFrame(
            {
                "normalized_cone_resistance": [28.982146, 24.709059, 22.507572],
                "normalized_friction_ratio": [0.5, 1, 4],
                "excess_pore_pressure_ratio": [0.5, 0.5, 0.5],
                "type_index": [
                    2.1224830270720094,
                    2.4006807734341495,
                    2.977470281698126,
                ],
            }
        )
        assert v.frame_equal(df, null_equal=True)

    def test_excess_pore_pressure_ratio(self):
        df1 = pl.DataFrame(
            {
                "soil_pressure": [0.002, 0.003, 0.004],
                "qt": [1, 1, 1],
                "water_pressure": [
                    0.0049050000000000005,
                    0.009810000000000001,
                    0.014715,
                ],
                "u2": [0.002, 0.002, 0.002],
            }
        )
        v = util.excess_pore_pressure_ratio(df1)
        df = pl.DataFrame(
            {
                "soil_pressure": [0.002, 0.003, 0.004],
                "qt": [1, 1, 1],
                "water_pressure": [
                    0.0049050000000000005,
                    0.009810000000000001,
                    0.014715,
                ],
                "u2": [0.002, 0.002, 0.002],
                "excess_pore_pressure_ratio": [
                    -0.002910821643286574,
                    -0.007833500501504515,
                    -0.012766064257028113,
                ],
            }
        )
        assert v.frame_equal(df, null_equal=True)

    def test_ic_to_gamma(self):
        water_level = -0.5
        df1 = pl.DataFrame(
            {"type_index": [2.208177, 2.408926, 2.793642], "depth": [0.5, 1, 4]}
        )
        df1 = df1.with_column(util.ic_to_gamma(water_level))
        df = pl.DataFrame(
            {
                "type_index": [2.208177, 2.408926, 2.793642],
                "depth": [0.5, 1, 4],
                "gamma_predict": [18, 18, 16],
            }
        )
        assert df1.frame_equal(df, null_equal=True)

    def test_ic_to_soil_type(self):
        df1 = pl.DataFrame({"type_index": [2.208177, 2.408926, 2.793642]}).with_column(
            util.ic_to_soil_type()
        )
        df = pl.DataFrame(
            {
                "type_index": [2.208177, 2.408926, 2.793642],
                "soil_type": [
                    "Silty sand to sandy silt",
                    "Clayey silt to silty clay",
                    "Clays",
                ],
            }
        )
        assert df1.frame_equal(df, null_equal=True)

    def test_been_jeffrey(self):
        water_level = -0.5
        df1 = pl.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "u2": [0.002, 0.002, 0.002],
                "depth": [0.0, 0.5, 1.0],
                "gamma": [18, 18, 18],
            }
        )
        v = util.been_jeffrey(df1, water_level)

        df = pl.DataFrame(
            {
                "qc": [1.0, 1.0, 1.0],
                "fs": [0.5, 0.5, 0.5],
                "u2": [0.002, 0.002, 0.002],
                "depth": [0.0, 0.5, 1.0],
                "gamma": [18.0, 18.0, 18.0],
                "delta_depth": [0.0, 0.5, 0.5],
                "soil_pressure": [0.0, 0.009, 0.0180],
                "qt": [1.0, 1.0, 1.0],
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
                "excess_pore_pressure_ratio": [
                    -0.0029050000000000005,
                    -0.007880928355196772,
                    -0.01294806517311609,
                ],
                "normalized_cone_resistance": [1.0, 1.0, 298.9345509893455],
                "normalized_friction_ratio": [
                    50.0,
                    50.45408678102926,
                    50.91649694501018,
                ],
                "type_index": [4.58641508344352, 4.589910119940267, 3.7547362767270505],
                "gamma_predict": [11.0, 11.0, 11.0],
            }
        )

        # TODO: why doesn't v.frame_equal(df, null_equal=True) work here
        for column in df.columns:
            assert v[column] == df[column]

    def test_iterate_been_jeffrey(self):
        water_level = -0.5
        df1 = pl.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "u2": [0.002, 0.002, 0.002],
                "depth": [0.0, 0.5, 1.0],
                "gamma": [18, 18, 18],
            }
        )
        v = util.iterate_been_jeffrey(df1, water_level)

        df = pl.DataFrame(
            {
                "qc": [1, 1, 1],
                "fs": [0.5, 0.5, 0.5],
                "u2": [0.002, 0.002, 0.002],
                "depth": [0.0, 0.5, 1],
                "gamma": [11, 11, 11],
                "delta_depth": [0.0, 0.5, 0.5],
                "soil_pressure": [0.0, 0.0055, 0.011],
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
                "excess_pore_pressure_ratio": [
                    -0.0029050000000000005,
                    -0.007853192559074913,
                    -0.012856420626895855,
                ],
                "normalized_cone_resistance": [1.0, 1.0, 1.0],
                "normalized_friction_ratio": [
                    50.0,
                    50.27652086475616,
                    50.55611729019211,
                ],
                "type_index": [4.58641508344352, 4.588303274171629, 4.590201600408948],
                "gamma_predict": [11, 11, 11],
                "soil_type": ["Peat", "Peat", "Peat"],
            }
        )

        # TODO: why doesn't v.frame_equal(df, null_equal=True) work here
        for column in df.columns:
            assert v[column] == df[column]
