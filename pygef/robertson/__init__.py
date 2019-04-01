from pygef.robertson.util import iterate_robertson


def classify(df, zid, water_level_NAP, new=True, area_quotient_cone_tip=None,
             pre_excavated_depth=None, p_a=0.1):
    """
    :param df: (DataFrame)
    :param zid: (flt) Depth of cpt ground level.
    :param water_level_NAP: (flt) Water level relative to NAP.
    :param new: (bool): Old or New implementation of Robertson.
    :param area_quotient_cone_tip: (flt)
    :param pre_excavated_depth: (flt)
    :param p_a: (flt) Atmospheric pressure at ground level in MPA.
    :return: (DataFrame) containing classification and IC values
    """
    water_level = zid - water_level_NAP
    return iterate_robertson(df, water_level, new=new, area_quotient_cone_tip=area_quotient_cone_tip,
                             pre_excavated_depth=pre_excavated_depth, p_a=p_a)
