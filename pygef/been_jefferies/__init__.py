from pygef.been_jefferies.util import iterate_been_jeffrey


def classify(
    df,
    water_level_and_zid_NAP=None,
    water_level_wrt_depth=None,
    area_quotient_cone_tip=None,
    pre_excavated_depth=None,
):
    """
    Classify function for Been & Jefferies.

    :param df: (DataFrame) Original dataframe.
    :param water_level_and_zid_NAP: (float)
    :param water_level_wrt_depth: (float)
    :param area_quotient_cone_tip: (float)
    :param pre_excavated_depth: (float)
    :return:
    """
    if water_level_and_zid_NAP["water_level_NAP"] is not None:
        water_level = (
            water_level_and_zid_NAP["zid"] - water_level_and_zid_NAP["water_level_NAP"]
        )
    elif water_level_wrt_depth is not None:
        water_level = water_level_wrt_depth
    else:
        raise ValueError(
            "You should specify one of water_level_NAP / water_level_wrt_depth"
        )
    return iterate_been_jeffrey(
        df,
        water_level,
        area_quotient_cone_tip=area_quotient_cone_tip,
        pre_excavated_depth=pre_excavated_depth,
    )
