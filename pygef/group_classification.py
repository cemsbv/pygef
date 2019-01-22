from pygef.robertson.robertson import Robertson, NewRobertson
import pandas as pd
########
# INPUT
UseNewRobertson = True
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
    def __init__(self, path=None):
        self.path = path

        if UseNewRobertson is True:
            rob = NewRobertson(path)
        else:
            rob = Robertson(path)
        df_rob = rob.df_complete
        depth = df_rob['depth']
        soil_type = df_rob['soil_type_Robertson']
        layer = []
        z_in = []
        zf = []
        add_all_layer = []
        layer_thickness = []
        for i in range(len(depth)):
            if i == 0:
                layer_i = soil_type[i]
                zii = depth[i]
                layer.append(layer_i)
                add_all_layer.append(layer_i)
                z_in.append(zii)
            else:
                layer_i_check = soil_type[i]
                if layer_i_check == add_all_layer[i-1]:
                    add_all_layer.append(layer_i_check)
                else:
                    zii = depth[i]
                    layer.append(layer_i_check)
                    add_all_layer.append(layer_i_check)
                    z_in.append(zii)
                    zfi = depth[i]
                    zf.append(zfi)

        for j in range(len(layer)-1):
            layer_thickness_i = zf[j] - z_in[j]
            layer_thickness.append(layer_thickness_i)

        df_layer = pd.DataFrame(layer, columns=['layer'])
        df_z_in = pd.DataFrame(z_in, columns=['z_in'])
        df_zf = pd.DataFrame(zf, columns=['zf'])
        df_layer_thickness = pd.DataFrame(layer_thickness, columns=['layer_thickness'])
        self.df_soil_grouped = pd.concat([df_layer, df_z_in, df_zf, df_layer_thickness], axis=1, sort=False)

        # Create significant layers

        significant_layers = []
        sig_z_in = []
        sig_zf = []
        sig_layer_thickness = []
        num_sign_layers = 0
        store_thickness = 0
        for m in range(len(layer)-1):
            if m == 0:
                sig_layer_i = layer[m]
                sig_layer_thickness_i = layer_thickness[m] + store_thickness
                sig_zf_i = zf[m]
                sig_z_in_i = z_in[m] - store_thickness
                sig_layer_thickness.append(sig_layer_thickness_i)
                significant_layers.append(sig_layer_i)
                sig_z_in.append(sig_z_in_i)
                sig_zf.append(sig_zf_i)
                num_sign_layers += 1
                store_thickness = 0
            else:
                if layer_thickness[m] >= MinimumThickness:
                    sig_layer_i = layer[m]
                    sig_layer_thickness_i = layer_thickness[m] + store_thickness
                    sig_zf_i = zf[m]
                    sig_z_in_i = z_in[m] - store_thickness
                    sig_layer_thickness.append(sig_layer_thickness_i)
                    significant_layers.append(sig_layer_i)
                    sig_z_in.append(sig_z_in_i)
                    sig_zf.append(sig_zf_i)
                    num_sign_layers += 1
                    store_thickness = 0
                else:
                    if store_thickness > 0:
                        store_thickness += layer_thickness[m]
                    else:
                        n = num_sign_layers
                        soil_type_m = layer[m]
                        soil_type_m_next = layer[m+1]
                        soil_type_m_previous = layer[m-1]
                        num_soil_type_m = dict_soil_type[soil_type_m]
                        num_soil_type_m_next = dict_soil_type[soil_type_m_next]
                        num_soil_type_m_previous = dict_soil_type[soil_type_m_previous]
                        diff1 = abs(num_soil_type_m-num_soil_type_m_previous)
                        diff2 = abs(num_soil_type_m-num_soil_type_m_next)
                        if diff1 <= diff2:
                            sig_layer_thickness[n - 1] += layer_thickness[m]
                            sig_zf[n-1] += layer_thickness[m]
                        else:
                            store_thickness += layer_thickness[m]

        df_significant_layers = pd.DataFrame(significant_layers, columns=['significant_layers'])
        df_sig_z_in = pd.DataFrame(sig_z_in, columns=['sig_z_in'])
        df_sig_zf = pd.DataFrame(sig_zf, columns=['sig_zf'])
        df_sig_layer_thickness = pd.DataFrame(sig_layer_thickness, columns=['sig_layer_thickness'])
        self.df_soil_grouped_significant = pd.concat([df_significant_layers, df_sig_z_in, df_sig_zf,
                                                      df_sig_layer_thickness], axis=1, sort=False)
        # Regrouping significant layers

        final_layers = []
        final_z_in = []
        final_zf = []
        final_layer_thickness = []
        final_add_all_layer = []
        final_store_thickness = 0
        for n in range(len(significant_layers)):
            if n == 0:
                final_layer_i = significant_layers[n]
                final_layers.append(final_layer_i)
                final_add_all_layer.append(final_layer_i)
                final_store_thickness += sig_layer_thickness[n]
            else:
                layer_check = significant_layers[n]
                if layer_check == final_add_all_layer[n-1] and n != (len(significant_layers) - 1):
                    final_add_all_layer.append(layer_check)
                    final_store_thickness += sig_layer_thickness[n]
                elif n == (len(significant_layers) - 1):
                    final_z_in_i = sig_z_in[n] - final_store_thickness
                    final_z_f_i = sig_zf[n]
                    final_z_in.append(final_z_in_i)
                    final_zf.append(final_z_f_i)
                    final_store_thickness += sig_layer_thickness[n]
                    final_layer_thickness.append(final_store_thickness)
                else:
                    final_z_in_i = sig_z_in[n] - final_store_thickness
                    final_z_f_i = sig_z_in[n]
                    final_layers.append(layer_check)
                    final_add_all_layer.append(layer_check)
                    final_z_in.append(final_z_in_i)
                    final_zf.append(final_z_f_i)
                    final_layer_thickness.append(final_store_thickness)
                    final_store_thickness = 0
                    final_store_thickness += sig_layer_thickness[n]




        df_final_layers = pd.DataFrame(final_layers, columns=['final_layers'])
        df_final_z_in = pd.DataFrame(final_z_in, columns=['final_z_in'])
        df_final_zf = pd.DataFrame(final_zf, columns=['final_zf'])
        df_final_layer_thickness = pd.DataFrame(final_layer_thickness, columns=['final_layer_thickness'])
        self.df_soil_grouped_final = pd.concat([df_final_layers, df_final_z_in, df_final_zf,
                                                df_final_layer_thickness], axis=1, sort=False)

