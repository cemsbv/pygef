import numpy as np
from pygef import geo
import pygef.utils as utils


def type_index_to_gamma(ic):
    gamma = None
    if ic > 3.22:
        gamma = 11
    elif 2.76 < ic <= 3.22:
        gamma = 16
    elif 2.40 < ic <= 2.76:
        gamma = 18
    elif 1.80 < ic <= 2.40:
        gamma = 18
    elif 1.25 < ic <= 1.80:
        gamma = 18
    elif ic <= 1.25:
        gamma = 18
    return gamma


def type_index_to_gamma_sat(ic):
    gamma_sat = None
    if ic > 3.22:
        gamma_sat = 11
    elif 2.76 < ic <= 3.22:
        gamma_sat = 16
    elif 2.40 < ic <= 2.76:
        gamma_sat = 18
    elif 1.80 < ic <= 2.40:
        gamma_sat = 19
    elif 1.25 < ic <= 1.80:
        gamma_sat = 20
    elif ic <= 1.25:
        gamma_sat = 20
    return gamma_sat


def type_index_to_soil_type(ic):
    soil_type = None
    if ic > 3.22:
        soil_type = 'Peat'
    elif 2.76 < ic <= 3.22:
        soil_type = 'Clays'
    elif 2.40 < ic <= 2.76:
        soil_type = 'Clayey silt to silty clay'
    elif 1.80 < ic <= 2.40:
        soil_type = 'Silty sand to sandy silt'
    elif 1.25 < ic <= 1.80:
        soil_type = 'Sands: clean sand to silty'
    elif ic <= 1.25:
        soil_type = 'Gravelly sands'
    return soil_type


def excess_pore_pressure_ratio(df):
    try:
        u2 = df['u2']
    except KeyError:
        raise SystemExit("ERROR: u2 not defined in .gef file, change classifier")
    return df.assign(excess_pore_pressure_ratio=(u2 - df['water_pressure']) / (df['qt'] - df['soil_pressure']))


def ic_to_gamma(df, water_level):
    return df.assign(gamma_predict=df.apply(
        lambda row: type_index_to_gamma(row['type_index']) if row['depth'] > water_level
        else type_index_to_gamma_sat(row['type_index']), axis=1))


def ic_to_soil_type(df):
    return df.assign(soil_type=df.apply(
        lambda row: type_index_to_soil_type(row['type_index']), axis=1))


def type_index(df):
    return df.assign(type_index=(((3 - np.log10(df['normalized_cone_resistance'] *
                                                (1 - df['excess_pore_pressure_ratio']) + 1)) ** 2 +
                                  (1.5 + 1.3 * np.log10(df['normalized_friction_ratio'])) ** 2) ** 0.5))


def iterate_been_jeffrey(original_df, water_level, area_quotient_cone_tip=None, pre_excavated_depth=None):
    gamma = np.ones(original_df.shape[0]) * 18

    c = 0
    while True:
        c += 1
        df = original_df.assign(gamma=gamma)

        def condition(x):
            return np.all(x['gamma_predict'] == gamma)
        df = been_jeffrey(df, water_level, area_quotient_cone_tip=area_quotient_cone_tip,
                          pre_excavated_depth=pre_excavated_depth)
        df = df.assign(gamma_predict=np.nan_to_num(df['gamma_predict']))
        if condition(df):
            break
        elif c > 10:
            break
        else:
            gamma = df['gamma_predict']

    return df.pipe(ic_to_soil_type)


def been_jeffrey(df, water_level, area_quotient_cone_tip=None, pre_excavated_depth=None):
    df = (df
          .pipe(geo.delta_depth, pre_excavated_depth)
          .pipe(geo.soil_pressure)
          .pipe(geo.qt, area_quotient_cone_tip)
          .pipe(geo.water_pressure, water_level)
          .pipe(geo.effective_soil_pressure)
          .pipe(utils.kpa_to_mpa, ['soil_pressure', 'effective_soil_pressure', 'water_pressure'])
          .pipe(excess_pore_pressure_ratio)
          .pipe(geo.normalized_cone_resistance)
          .pipe(geo.normalized_friction_ratio)
          .pipe(utils.nan_to_zero)
          .pipe(type_index)
          .pipe(ic_to_gamma, water_level)
          )
    return df

