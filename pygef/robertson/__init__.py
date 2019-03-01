from pygef.robertson.util import iterate_robertson


def classify(df, zid, water_level_NAP, new=True, area_quotient_cone_tip=None,
             pre_excavated_depth=None, p_a=None):
    water_level = zid - water_level_NAP
    if new:
        return iterate_robertson(df, water_level, new=True, area_quotient_cone_tip=area_quotient_cone_tip,
                                 pre_excavated_depth=pre_excavated_depth, p_a=p_a)
    else:
        return iterate_robertson(df, water_level, area_quotient_cone_tip=area_quotient_cone_tip,
                                 pre_excavated_depth=pre_excavated_depth, p_a=p_a)
