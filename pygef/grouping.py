import pandas as pd
########
# INPUT
MinimumThickness = 0.20
########

dict_soil_type = {'Peat': 1,
                  'Clays - silty clay to clay': 2,
                  'Silt mixtures - clayey silt to silty clay': 3,
                  'Sand mixtures - silty sand to sandy silt': 4,
                  'Sands - clean sand to silty sand': 5,
                  'Gravelly sand to dense sand': 6
                  }


class GroupClassification:
    def __init__(self, df):
        df_group = df.copy()
        self.df_group = (df_group
                         .pipe(self.group_equal_layers)
                         .pipe(self.group_significant_layers)
                         .pipe(self.regroup_significant_layers)
                         )

    @staticmethod
    def calculate_thickness(df):
        return df.assign(thickness=(df['zf'] - df['z_in']))

    @staticmethod
    def calculate_z_centr(df):
        return df.assign(z_centr=(df['zf'] + df['z_in'])/2)

    def group_equal_layers_try(self, df_group):

        return

    def group_equal_layers(self, df_group):
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
                .pipe(self.calculate_thickness)
                .pipe(self.calculate_z_centr))

    @staticmethod
    def group_significant_layers(df_group):
        significant_layers = []
        sig_z_in = []
        sig_zf = []
        sig_layer_thickness = []
        num_sign_layers = 0
        store_thickness = 0
        for m in range(len(df_group['layer'])):
            if m == 0:
                sig_layer_thickness.append(df_group['thickness'][m] + store_thickness)
                significant_layers.append(df_group['layer'][m])
                sig_z_in.append(df_group['z_in'][m] - store_thickness)
                sig_zf.append(df_group['zf'][m])
                num_sign_layers += 1
                store_thickness = 0
            elif m == len(df_group['layer']) - 1:
                sig_layer_thickness.append(df_group['thickness'][m] + store_thickness)
                significant_layers.append(df_group['layer'][m])
                sig_z_in.append(df_group['z_in'][m] - store_thickness)
                sig_zf.append(df_group['zf'][m])
                num_sign_layers += 1
                store_thickness = 0
            else:
                if df_group['thickness'][m] >= MinimumThickness:
                    sig_layer_thickness.append(df_group['thickness'][m] + store_thickness)
                    significant_layers.append(df_group['layer'][m])
                    sig_z_in.append(df_group['z_in'][m] - store_thickness)
                    sig_zf.append(df_group['zf'][m])
                    num_sign_layers += 1
                    store_thickness = 0
                else:
                    if store_thickness > 0:
                        store_thickness += df_group['thickness'][m]
                    else:
                        n = num_sign_layers
                        soil_type_m = df_group['layer'][m]
                        soil_type_m_next = df_group['layer'][m + 1]
                        soil_type_m_previous = df_group['layer'][m - 1]
                        num_soil_type_m = dict_soil_type[soil_type_m]
                        num_soil_type_m_next = dict_soil_type[soil_type_m_next]
                        num_soil_type_m_previous = dict_soil_type[soil_type_m_previous]
                        diff1 = abs(num_soil_type_m - num_soil_type_m_previous)
                        diff2 = abs(num_soil_type_m - num_soil_type_m_next)
                        if diff1 <= diff2:
                            sig_layer_thickness[n - 1] += df_group['thickness'][m]
                            sig_zf[n - 1] += df_group['thickness'][m]
                        else:
                            store_thickness += df_group['thickness'][m]

        return pd.DataFrame({'layer': significant_layers,
                             'z_in': sig_z_in,
                             'zf': sig_zf,
                             'thickness': sig_layer_thickness})

    def regroup_significant_layers(self, df_group):
        final_layers = []
        final_z_in = []
        final_zf = []
        for n in range(len(df_group['layer'])):
            if n == 0:
                final_layers.append(df_group['layer'][n])
            elif n == (len(df_group['layer']) - 1):
                final_z_in.append(df_group['z_in'][n])
                final_zf.append(df_group['z_in'][n])
                final_layers.append(df_group['layer'][n])
                final_z_in.append(df_group['z_in'][n])
                final_zf.append(df_group['zf'][n])
            else:
                if df_group['layer'][n] == df_group['layer'][n - 1] and n != (len(df_group['layer']) - 1):
                    pass
                else:
                    final_layers.append(df_group['layer'][n])
                    final_z_in.append(df_group['z_in'][n])
                    final_zf.append(df_group['z_in'][n])
        df_soil_grouped = pd.DataFrame({'layer': final_layers,
                                        'z_in': final_z_in,
                                        'zf': final_zf,
                                        })

        return(df_soil_grouped
               .pipe(self.calculate_thickness)
               .pipe(self.calculate_z_centr))





