import numpy as np

GROUND_CLASS = {
    "NBE": None,
    "G": 0,
    'Z': 1,
    'L': 2,
    'K': 3,
    'V': 4,
    "H": 4,
    "S": 2
}

IC_MAPPING = {
    "G": 0.5,
    "Z": 2.6,
    "L": 2.95,
    "K": 4,
    "V": 100
}

GAMMA_MAPPING = {
    "G": 20,
    "Z": 20,
    "L": 20,
    "K": 17,
    "V": 11,
    "H": 11,
    "S": 20
}

MAIN_SOIL = ["G", "Z", "L", "K", "V"]
GAMMA_ARRAY = np.array([GAMMA_MAPPING[k] for k in MAIN_SOIL])


def det_u_hydrostatic(l, water_level=1.):
    """

    :param l: (array)
    :param water_level: (flt) Depth of the water level.
    :return: (array) Hydrostatic water pressure
    """
    u = (l - water_level) * 10e-3
    u[u < 0] = 0
    return u


def det_layer_weight(sp, dl):
    return dl * np.dot(GAMMA_ARRAY / 1e3, sp)


def det_ground_pressure(l, sp):
    """
    Assumes the last layer is the same thickness as the previous layer.

    Note that the l array could be like this:
     [1.2, 1.22, 1.24, ... n]

    The first values will be assumed to be 1.2 meters of the first layer.

    :param l: (array) Length
    :param sp: (array) Soil print
    :return: (array) Ground pressure
    """
    dl = np.diff(l)
    return np.cumsum(np.dot(sp, GAMMA_ARRAY * 1e-3) * np.append(l[0], dl))


def det_effective_stress(l, u2, sp):
    """

    :param l: (array) Length
    :param u2: (array) Water pressure
    :param sp: (2D array) Soil print
    :return: (array) Effective stress
    """
    return det_ground_pressure(l, sp) - u2