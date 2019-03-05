from pygef.been_jeffrey.util import iterate_been_jeffrey


def classify(df, zid, water_level_NAP, area_quotient_cone_tip, pre_excavated_depth):
    water_level = zid - water_level_NAP
    return iterate_been_jeffrey(df, water_level, area_quotient_cone_tip=area_quotient_cone_tip,
                                pre_excavated_depth=pre_excavated_depth)
