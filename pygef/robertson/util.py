import numpy as np
from pygef import geo


def n_exponent(df, p_a):
    return df.assign(n=df.apply(
        lambda row: (0.381 * row['type_index_n'] + 0.05 * (row['effective_soil_pressure'] / p_a) - 0.15)
        if (0.381 * row['type_index_n'] + 0.05 * (row['effective_soil_pressure'] / p_a) - 0.15) < 1
        else 1, axis=1))


def normalized_cone_resistance_n(df, p_a):
    df = df.assign(normalized_cone_resistance=((df['qt'] - df['soil_pressure'])/p_a *
                                               (p_a / df['effective_soil_pressure'])**df['n']))
    df.loc[df['normalized_cone_resistance'] < 0, 'normalized_cone_resistance'] = 1
    return df


def type_index(df):
    return df.assign(type_index=(((3.47 - np.log10(df['normalized_cone_resistance'])) ** 2 +
                                  (np.log10(df['normalized_friction_ratio']) + 1.22) ** 2) ** 0.5))


def ic_to_gamma(df, water_level):
    return df.assign(gamma_predict=df.apply(
        lambda row: type_index_to_gamma(row['type_index']) if row['depth'] > water_level
                                        else type_index_to_gamma_sat(row['type_index']), axis=1))


def ic_to_soil_type(df):
    return df.assign(soil_type=df.apply(
        lambda row: type_index_to_soil_type(row['type_index']), axis=1))


def nan_to_zero(df):
    return df.fillna(0)


def type_index_to_gamma(ic):
    gamma = None
    if ic > 3.6:
        gamma = 11
    elif 2.95 < ic <= 3.6:
        gamma = 16
    elif 2.60 < ic <= 2.95:
        gamma = 18
    elif 2.05 < ic <= 2.60:
        gamma = 18
    elif 1.31 < ic <= 2.05:
        gamma = 18
    elif ic <= 1.31:
        gamma = 18
    return gamma


def type_index_to_gamma_sat(ic):  # todo: maybe insert the case in which ic is nan
    gamma_sat = None
    if ic > 3.6:
        gamma_sat = 11
    elif 2.95 < ic <= 3.6:
        gamma_sat = 16
    elif 2.60 < ic <= 2.95:
        gamma_sat = 18
    elif 2.05 < ic <= 2.60:
        gamma_sat = 19
    elif 1.31 < ic <= 2.05:
        gamma_sat = 20
    elif ic <= 1.31:
        gamma_sat = 20
    return gamma_sat


def type_index_to_soil_type(ic):
    soil_type = None
    if ic > 3.6:
        soil_type = 'Peat'
    elif 2.95 < ic <= 3.6:
        soil_type = 'Clays - silty clay to clay'
    elif 2.60 < ic <= 2.95:
        soil_type = 'Silt mixtures - clayey silt to silty clay'
    elif 2.05 < ic <= 2.60:
        soil_type = 'Sand mixtures - silty sand to sandy silt'
    elif 1.31 < ic <= 2.05:
        soil_type = 'Sands - clean sand to silty sand'
    elif ic <= 1.31:
        soil_type = 'Gravelly sand to dense sand'
    return soil_type


def iterate_robertson(original_df, water_level, new=True, area_quotient_cone_tip=None, pre_excavated_depth=None, p_a=0.1):
    gamma = np.ones(original_df.shape[0]) * 18
    n = np.ones(original_df.shape[0])
    type_index_n = np.ones(original_df.shape[0])

    c = 0
    while True:
        c += 1

        if new:
            df = original_df.assign(n=n, type_index_n=type_index_n, gamma=gamma)
            f = new_robertson

            def condition(x):
                return np.all(x['gamma_predict'] == gamma) and np.all(x['n'] == n)
        else:
            df = original_df.assign(gamma=gamma)
            f = old_robertson

            def condition(x):
                return np.all(x['gamma_predict'] == gamma)

        df = f(df, water_level, area_quotient_cone_tip=area_quotient_cone_tip,
               pre_excavated_depth=pre_excavated_depth, p_a=p_a)
        df = df.assign(gamma_predict=np.nan_to_num(df['gamma_predict']))
        if condition(df):
            break
        elif c > 10:
            break
        else:
            gamma = df['gamma_predict']
            if new:
                n = df['n']

    return df.pipe(ic_to_soil_type)


def old_robertson(df, water_level, area_quotient_cone_tip=None, pre_excavated_depth=None, p_a=None):
    df = (df
          .pipe(geo.delta_depth, pre_excavated_depth)
          .pipe(geo.soil_pressure)
          .pipe(geo.qt, area_quotient_cone_tip)
          .pipe(geo.water_pressure, water_level)
          .pipe(geo.effective_soil_pressure)
          .pipe(geo.kpa_to_mpa, ['soil_pressure', 'effective_soil_pressure', 'water_pressure'])
          .pipe(geo.normalized_cone_resistance)
          .pipe(geo.normalized_friction_ratio)
          .pipe(nan_to_zero)
          .pipe(type_index)
          .pipe(ic_to_gamma, water_level)
          )
    return df


def new_robertson(df, water_level, area_quotient_cone_tip=None, pre_excavated_depth=None, p_a=0.1):
    df = (df
          .pipe(geo.delta_depth, pre_excavated_depth)
          .pipe(geo.soil_pressure)
          .pipe(geo.qt, area_quotient_cone_tip)
          .pipe(geo.water_pressure, water_level)
          .pipe(geo.effective_soil_pressure)
          .pipe(geo.kpa_to_mpa, ['soil_pressure', 'effective_soil_pressure', 'water_pressure'])
          .pipe(n_exponent, p_a)
          .pipe(normalized_cone_resistance_n, p_a)
          .pipe(geo.normalized_friction_ratio)
          .pipe(nan_to_zero)
          .pipe(type_index)
          .pipe(ic_to_gamma, water_level)
          )
    return df
