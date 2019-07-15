from pygef.robertson.util import iterate_robertson


def classify(
    df,
    water_level_and_zid_NAP=None,
    water_level_wrt_depth=None,
    new=True,
    area_quotient_cone_tip=None,
    pre_excavated_depth=None,
    p_a=0.1,
):
    """
    Classify function for Rpbertson.

    :param df: (DataFrame) Original dataframe.
    :param water_level_NAP: (dict) {
                                        water_level: <water level wrt NAP,
                                        zid: <zid>
                                    }
    :param new: (bool): Old or New implementation of Robertson.
    :param area_quotient_cone_tip: (flt)
    :param pre_excavated_depth: (flt)
    :param p_a: (flt) Atmospheric pressure at ground level in MPA.
    :return: (DataFrame) containing classification and IC values.
    """

    if water_level_and_zid_NAP["water_level_NAP"] is not None:
        water_level = (
            water_level_and_zid_NAP["zid"] - water_level_and_zid_NAP["water_level_NAP"]
        )
    elif water_level_wrt_depth is not None:
        water_level = df["depth"].min() - water_level_wrt_depth
    else:
        raise ValueError(
            "You should specify one of water_level_NAP / water_level_wrt_depth"
        )

    return iterate_robertson(
        df,
        water_level,
        new=new,
        area_quotient_cone_tip=area_quotient_cone_tip,
        pre_excavated_depth=pre_excavated_depth,
        p_a=p_a,
    )
