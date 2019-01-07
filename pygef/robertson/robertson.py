from pygef.gef import ParseGEF
import numpy as np

gef = ParseGEF("/home/martina/Documents/gef_files/2018/18337/18337_C03-696.GEF")
df = gef.df

# INPUT
water_level = 0  # (m) respect to the ground floor
qc = df['qc']
fs = df['fs']
depth = df['depth']

# qt
if gef.net_surface_area_quotient_of_the_cone_tip is not None and 'qc' in df.columns and 'u2' in df.columns:
    qt = qc + df['u2']*(1-gef.net_surface_area_quotient_of_the_cone_tip)
else:
    qt = qc


def hydrostatic_water_pressure(water_level, depth):
    hydrostatic_water_pressure = []
    for z in depth:
        if z <= water_level:
            hydrostatic_water_pressure.append(0)
        else:
            hydrostatic_water_pressure.append((z - water_level)*9.81)
    return hydrostatic_water_pressure


def type_index_to_gamma(ic):
    gamma = None
    if ic > 3.6:
        gamma = 11
    elif 2.5 < ic <= 3.6:
        gamma = 16
    elif 2.60 < ic <= 2.95:
        gamma = 18
    elif 2.05 < ic <= 2.60:
        gamma = 18
    elif 1.31 < ic <= 2.05:
        gamma = 18
    elif ic < 1.31:
        gamma = 18
    return gamma


def type_index_to_gamma_sat(ic):
    gamma_sat = None
    if ic > 3.6:
        gamma_sat = 11
    elif 2.5 < ic <= 3.6:
        gamma_sat = 16
    elif 2.60 < ic <= 2.95:
        gamma_sat = 18
    elif 2.05 < ic <= 2.60:
        gamma_sat = 19
    elif 1.31 < ic <= 2.05:
        gamma_sat = 20
    elif ic < 1.31:
        gamma_sat = 20
    return gamma_sat


def type_index_to_soil_type(ic):
    soil_type = None
    if ic > 3.6:
        soil_type = 'Peat'
    elif 2.5 < ic <= 3.6:
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


def effective_stress(sigma_v0, u):
    sigma_v0_eff = sigma_v0 - u
    return sigma_v0_eff


def normalized_cone_resistance(qt, sigma_v0, sigma_v0_eff):
    Qt = (qt - sigma_v0)/sigma_v0_eff
    return Qt

def friction_ratio(fs, qt, sigma_v0):
    fr = fs*100/(qt-sigma_v0)
    return fr

def type_index(fs, qt, sigma_v0):
    I_c = ((3.47-))
    return I_c

# calculation of sigma_v and u
u = hydrostatic_water_pressure(water_level, df['depth'])

#sigma_v0_eff = effective_stress(np.zeros(len(depth)), u)
#Qt = normalized_cone_resistance(qt, np.zeros(len(depth)), sigma_v0_eff)

for i in range(1,len(depth)):
    if i == 1:
        sigma_v0 = 0

    else:
        


