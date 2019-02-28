import numpy as np


def soil_pressure(df, pre_excavated_depth=None):
    if pre_excavated_depth is not None and df['depth'][0] == 0:
        df['depth'] = df['depth'] + pre_excavated_depth
        return df.assign(soil_pressure=np.cumsum(df['gamma'] * df['depth']))
    return df.assign(soil_pressure=np.cumsum(df['gamma'] * df['depth']))


def water_pressure(df, water_level):
    df = df.assign(water_pressure=(df['depth'] + water_level) * 9.81)
    df.loc[df['water_pressure'] < 0, 'water_pressure'] = 0
    return df


def effective_soil_pressure(df):
    return df.assign(effective_soil_pressure=(df['soil_pressure'] - df['water_pressure']))


def assign_multiple_columns(df, columns, partial_df):
    return df.assign(**dict(zip(columns, partial_df.values.T)))


def kpa_to_mpa(df, columns):
    return assign_multiple_columns(df, columns, df[columns] * 10 ** -3)


def qt(df, area_quotient_cone_tip=None):
    if 'u2' in df.columns and area_quotient_cone_tip is not None:
        return df.assign(qt=df['qc'] * df['u2'] * (1 - area_quotient_cone_tip))

    return df.assign(qt=df['qc'])


def normalized_cone_resistance(df):
    df = df.assign(normalized_cone_resistance=((df['qt'] - df['soil_pressure']) /
                                               (df['effective_soil_pressure'])))
    df.loc[df['normalized_cone_resistance'] < 0, 'normalized_cone_resistance'] = 1
    return df


def normalized_friction_ratio(df):
    df = df.assign(normalized_friction_ratio=((df['fs'] / (df['qt'] - df['soil_pressure'])) * 100))
    df.loc[df['normalized_friction_ratio'] < 0, 'normalized_friction_ratio'] = 0.1
    return df
