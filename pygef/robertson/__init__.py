import numpy as np
import pandas as pd

# INPUT: insert manually the water level
water_level_NAP = -1.56  # (m) respect to the NAP
p_a = 0.1  # MPa (only new robertson)


class RobertsonClassifier:
    def __init__(self, gef):
        self.gef = None
        self.df_complete = None

        self.gef = gef
        qc = gef.df['qc']
        self.depth = gef.df['depth']
        self.fs = gef.df['fs']
        self.pre_excavated_depth = gef.pre_excavated_depth
        zid = gef.zid
        self.water_level = water_level_NAP - zid
        self.p_a = p_a

        # qt
        if self.gef.net_surface_area_quotient_of_the_cone_tip is not None and 'qc' \
                in self.gef.df.columns and 'u2' in self.gef.df.columns:
            self.qt = qc + gef.df['u2'] * (1 - gef.net_surface_area_quotient_of_the_cone_tip)
        else:
            self.qt = qc

    def classify(self, new=True):  # set new =True to use the new robertson classification
        # calculation of sigma_v and u
        u = self.hydrostatic_water_pressure(self.water_level, self.gef.df['depth'])
        soil_type_robertson = []
        Ic = []
        sig0 = []
        series_Qt = []
        series_Fr = []
        for depth_i in self.depth:
            i = self.depth[self.depth == depth_i].index[0]
            qti = self.qt[i]
            fsi = self.fs[i]
            ui = u[i]
            if i == 0:  # add the check for the pre-excavation
                if self.pre_excavated_depth is not None:
                    sigma_v0i = 18 * self.pre_excavated_depth  # use of a standard gamma=18 for the excavated soil
                else:
                    sigma_v0i = 0
                if new:
                    n1 = 1
                    ic = self.type_index_n(fsi, qti, sigma_v0i, ui, n1, p_a)
                    n2 = self.n_exponent(ic, sigma_v0i, p_a, ui)
                    ii = 0
                    max_it = 5
                    while n2 != n1 and ii < max_it:
                        n1 = n2
                        ic = self.type_index_n(fsi, qti, sigma_v0i, ui, n1, p_a)
                        n2 = self.n_exponent(ic, sigma_v0i, p_a, ui)
                        ii += 1
                else:
                    ic = self.type_index(fsi, qti, sigma_v0i, ui)
            else:
                depth1 = self.depth.iloc[i - 1]
                depth2 = depth_i
                sig0i = sig0[i - 1]
                # iteration: it starts assuming gamma of the sand and iterate until the real gamma is found.
                gamma1 = 20
                delta_sigma_v0i = self.delta_vertical_stress(depth1, depth2, gamma1)
                sigma_v0i = self.vertical_stress(sig0i, delta_sigma_v0i)
                if new:
                    n1 = 1
                    ic = self.type_index_n(fsi, qti, sigma_v0i, ui, n1, p_a)
                    n2 = self.n_exponent(ic, sigma_v0i, p_a, ui)
                else:
                    ic = self.type_index(fsi, qti, sigma_v0i, ui)
                gamma2 = self.get_gamma(ic, depth_i)
                ii = 0
                max_it = 5
                if new:
                    while (gamma2 != gamma1 or n2 != n1) and ii < max_it:
                        gamma1 = gamma2
                        n1 = n2
                        delta_sigma_v0i = self.delta_vertical_stress(depth1, depth2, gamma1)
                        sigma_v0i = self.vertical_stress(sig0i, delta_sigma_v0i)
                        ic = self.type_index_n(fsi, qti, sigma_v0i, ui, n1, p_a)
                        n2 = self.n_exponent(ic, sigma_v0i, p_a, ui)
                        gamma2 = self.get_gamma(ic, depth_i)
                        ii += 1
                else:
                    while gamma2 != gamma1 and ii < max_it:
                        gamma1 = gamma2
                        delta_sigma_v0i = self.delta_vertical_stress(depth1, depth2, gamma1)
                        sigma_v0i = self.vertical_stress(sig0i, delta_sigma_v0i)
                        ic = self.type_index(fsi, qti, sigma_v0i, ui)
                        gamma2 = self.get_gamma(ic, depth_i)
                        ii += 1
            if new:
                Qti = self.normalized_cone_resistance_n(qti, sigma_v0i, ui, n1, p_a)
                Fri = self.normalized_friction_ratio(fsi, qti, sigma_v0i)
            else:
                Qti = self.normalized_cone_resistance(qti, sigma_v0i, ui)
                Fri = self.normalized_friction_ratio(fsi, qti, sigma_v0i)

            series_Qt.append(Qti)
            series_Fr.append(Fri)
            sig0.append(sigma_v0i)
            Ic.append(ic)
            soil_type = self.type_index_to_soil_type(ic)
            soil_type_robertson.append(soil_type)
        df_Ic = pd.DataFrame(Ic, columns=['Ic'])
        df_soil_type = pd.DataFrame(soil_type_robertson, columns=['soil_type_Robertson'])
        df_robertson = pd.concat([df_Ic, df_soil_type], axis=1, sort=False)
        df_u = pd.DataFrame(u, columns=['hydrostatic_pore_pressure'])
        df_Qt = pd.DataFrame(series_Qt, columns=['normalized_Qt'])
        df_Fr = pd.DataFrame(series_Fr, columns=['normalized_Fr'])
        self.df_complete = pd.concat([self.gef.df, df_u, df_robertson, df_Qt, df_Fr], axis=1, sort=False)
        return self.df_complete

    @staticmethod
    def hydrostatic_water_pressure(water_level, depth):
        hydrostatic_water_pressure = []
        for z in depth:
            if z <= water_level:
                hydrostatic_water_pressure.append(0)
            else:
                hydrostatic_water_pressure.append((z - water_level) * 9.81)
        return hydrostatic_water_pressure

    @staticmethod
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

    @staticmethod
    def type_index_to_gamma_sat(ic):
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

    def get_gamma(self, ic, depth):
        if depth <= self.water_level:
            gamma = self.type_index_to_gamma(ic)
        else:
            gamma = self.type_index_to_gamma_sat(ic)
        return gamma

    @staticmethod
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
        elif ic < 1.31:
            soil_type = 'Gravelly sand to dense sand'
        return soil_type

    @staticmethod
    def effective_stress(sigma_v0, u):
        sigma_v0_eff = sigma_v0 - u
        return sigma_v0_eff

    def normalized_cone_resistance(self, qt, sigma_v0, u):
        sigma_v0_eff = self.effective_stress(sigma_v0, u)
        if sigma_v0_eff > 0 and (qt - sigma_v0 * (10 ** -3)) > 0:
            Qt = (qt - sigma_v0 * (10 ** -3)) / (sigma_v0_eff * (10 ** -3))
        else:
            Qt = 1
        return Qt

    def n_exponent(self, Ic, sigma_v0, p_a, u):
        sigma_v0_eff = self.effective_stress(sigma_v0, u)
        n1 = 0.381 * Ic + 0.05 * (sigma_v0_eff * (10 ** -3) / p_a) - 0.15
        n = min(n1, 1)
        return n

    def normalized_cone_resistance_n(self, qt, sigma_v0, sigma_v0_eff, n, p_a):
        if sigma_v0_eff > 0 and (qt - sigma_v0 * (10 ** -3)) > 0:
            Qt = (qt - sigma_v0 * (10 ** -3)) / p_a * (p_a / (sigma_v0_eff * (10 ** -3))) ** n
        else:
            Qt = 1
        return Qt

    @staticmethod
    def normalized_friction_ratio(fs, qt, sigma_v0):
        if (qt - sigma_v0 * (10 ** -3)) > 0 and fs > 0:
            fr = fs * 100 / (qt - sigma_v0 * (10 ** -3))
        else:
            fr = 0.1
        return fr

    @staticmethod
    def delta_vertical_stress(depth1, depth2, gamma):
        delta_sigma_v0 = (depth2 - depth1) * gamma
        return delta_sigma_v0

    @staticmethod
    def vertical_stress(sig0, delta_sigma_v0):
        sigma_v0 = sig0 + delta_sigma_v0
        return sigma_v0

    def type_index(self, fs, qt, sigma_v0, u):
        Qt = self.normalized_cone_resistance(qt, sigma_v0, u)
        Fr = self.normalized_friction_ratio(fs, qt, sigma_v0)
        I_c = ((3.47 - np.log10(Qt)) ** 2 + (np.log10(Fr) + 1.22) ** 2) ** 0.5
        return I_c

    def type_index_n(self, fs, qt, sigma_v0, u, n, p_a):
        sigma_v0_eff = self.effective_stress(sigma_v0, u)
        Qt = self.normalized_cone_resistance_n(qt, sigma_v0, sigma_v0_eff, n, p_a)
        Fr = self.normalized_friction_ratio(fs, qt, sigma_v0)
        I_c = ((3.47 - np.log10(Qt)) ** 2 + (np.log10(Fr) + 1.22) ** 2) ** 0.5
        return I_c


