import pandas as pd


class GroupClassification:
    def __init__(self, df, dict_soil_type, min_thickness):
        df_group = df.copy()
        df_group = df_group.loc[:, ['depth', 'soil_type']]
        self.df_group = (df_group
                         .pipe(group_equal_layers)
                         #.pipe(group_significant_layers, dict_soil_type, min_thickness)
                         #.pipe(regroup_significant_layers)
                         )


def calculate_thickness(df):
    return df.assign(thickness=(df['zf'] - df['z_in']))


def calculate_z_centr(df):
    return df.assign(z_centr=(df['zf'] + df['z_in'])/2)


def group_equal_layers(df_group):
    df_group = df_group.groupby((df_group.soil_type != df_group.soil_type.shift()).cumsum()).max().reset_index(drop=True)
    df_group = pd.DataFrame({'layer': df_group.soil_type,
                             'z_in': df_group.depth.shift().fillna(0),
                             'zf': df_group.depth})
    return (df_group
            .pipe(calculate_thickness)
            .pipe(calculate_z_centr))


def group_equal_layers_not_functional(df_group):
    layer = []
    z_in = []
    zf = []
    for i, st in enumerate(df_group['soil_type']):
        if i == 0:
            layer.append(st)
            z_in.append(df_group['depth'][i])
        elif i == len(df_group['depth']) - 1:
            zf.append(df_group['depth'][i])
        else:
            if st == df_group['soil_type'][i - 1]:
                pass
            else:
                layer.append(st)
                z_in.append(df_group['depth'][i])
                zf.append(df_group['depth'][i])
    df_soil_grouped = pd.DataFrame({'layer': layer,
                                    'z_in': z_in,
                                    'zf': zf})
    return (df_soil_grouped
            .pipe(calculate_thickness)
            .pipe(calculate_z_centr))


def group_significant_layers(df_group, dict_soil_type, min_thickness):
    significant_layers = []
    sig_z_in = []
    sig_zf = []
    num_sign_layers = 0
    store_thickness = 0
    for i, layer in enumerate(df_group['layer']):
        if i == 0:
            significant_layers.append(layer)
            sig_z_in.append(df_group['z_in'][i] - store_thickness)
            sig_zf.append(df_group['zf'][i])
            num_sign_layers += 1
            store_thickness = 0
        elif i == len(df_group['layer']) - 1:
            significant_layers.append(layer)
            sig_z_in.append(df_group['z_in'][i] - store_thickness)
            sig_zf.append(df_group['zf'][i])
            num_sign_layers += 1
            store_thickness = 0
        else:
            if df_group['thickness'][i] >= min_thickness:
                significant_layers.append(layer)
                sig_z_in.append(df_group['z_in'][i] - store_thickness)
                sig_zf.append(df_group['zf'][i])
                num_sign_layers += 1
                store_thickness = 0
            else:
                if store_thickness > 0:
                    store_thickness += df_group['thickness'][i]
                else:
                    n = num_sign_layers
                    soil_type_m = layer
                    soil_type_m_next = df_group['layer'][i + 1]
                    soil_type_m_previous = df_group['layer'][i - 1]
                    num_soil_type_m = dict_soil_type[soil_type_m]
                    num_soil_type_m_next = dict_soil_type[soil_type_m_next]
                    num_soil_type_m_previous = dict_soil_type[soil_type_m_previous]
                    diff1 = abs(num_soil_type_m - num_soil_type_m_previous)
                    diff2 = abs(num_soil_type_m - num_soil_type_m_next)
                    if diff1 <= diff2:
                        sig_zf[n - 1] += df_group['thickness'][i]
                    else:
                        store_thickness += df_group['thickness'][i]
    df_soil_grouped = pd.DataFrame({'layer': significant_layers,
                                    'z_in': sig_z_in,
                                    'zf': sig_zf
                                    })
    return (df_soil_grouped
            .pipe(calculate_thickness)
            .pipe(calculate_z_centr)
            )


def regroup_significant_layers(df_group):
    final_layers = []
    final_z_in = []
    final_zf = []
    final_store_thickness = 0
    for n, layer in enumerate(df_group['layer']):
        if n == 0:
            final_layers.append(layer)
            final_store_thickness += df_group['thickness'][n]
        elif n == (len(df_group['layer']) - 1):
            final_z_in.append(df_group['z_in'][n] - final_store_thickness)
            final_zf.append(df_group['z_in'][n])
            final_layers.append(layer)
            final_z_in.append(df_group['z_in'][n])
            final_zf.append(df_group['zf'][n])
        else:
            if layer == df_group['layer'][n - 1]:
                final_store_thickness += df_group['thickness'][n]
            else:
                final_layers.append(layer)
                final_z_in.append(df_group['z_in'][n] - final_store_thickness)
                final_zf.append(df_group['z_in'][n])
                final_store_thickness = 0
                final_store_thickness += df_group['thickness'][n]
    df_soil_grouped = pd.DataFrame({'layer': final_layers,
                                    'z_in': final_z_in,
                                    'zf': final_zf
                                    })
    return (df_soil_grouped
            .pipe(calculate_thickness)
            .pipe(calculate_z_centr)
            )
