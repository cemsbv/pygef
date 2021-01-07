import pandas as pd


class GroupClassification:
    def __init__(self, zid, df, min_thickness):
        # TODO: docstring
        df_group = df.copy()
        self.zid = zid
        start_depth = df_group["depth"][0]
        df_group = df_group.loc[:, ["depth", "soil_type"]]

        self.df_group = (
            df_group.pipe(self.group_equal_layers, "soil_type", "depth", start_depth)
            .pipe(group_significant_layers, min_thickness, start_depth)
            .pipe(self.group_equal_layers, "layer", "zf", start_depth)
        )

    def group_equal_layers(self, df_group, column1, column2, start_depth):
        """
        Group equal layers by checking the difference between the original column of soil type and the shifted one and
        storing that in a boolean array, then it does a cumulative sum of the boolean array and it groups the
        result of the cumulative sum.

        :param df_group: Original DataFrame to group.
        :param column1: Column to group, it can be soil_type or layer.
        :param column2: Depth or zf (final z).
        :param start_depth: First value of depth.
        :return: Grouped dataframe.
        """
        df_group = (
            df_group.groupby((df_group[column1] != df_group[column1].shift()).cumsum())
            .max()
            .reset_index(drop=True)
        )

        df_group = pd.DataFrame(
            {
                "layer": df_group[column1],
                "z_in": df_group[column2].shift().fillna(start_depth),
                "zf": df_group[column2],
            }
        )
        return (
            df_group.pipe(calculate_thickness)
            .pipe(calculate_z_centr)
            .pipe(calculate_z_in_NAP, self.zid)
            .pipe(calculate_zf_NAP, self.zid)
            .pipe(calculate_z_centr_NAP, self.zid)
        )


def group_significant_layers(df_group, min_thickness, start_depth):
    """
    Drop the layers with thickness < min_thickness and adjust the limits of the others.

    :param df_group: Original DataFrame.
    :param min_thickness: Minimum thickness.
    :param start_depth: First value of depth.
    :return: DataFrame without the dropped layers.
    """
    df_group = df_group.loc[:, ["zf", "layer", "thickness"]]
    depth = df_group["zf"].iloc[-1]
    indexes = df_group[df_group.thickness < min_thickness].index.values.tolist()
    df_group = df_group.drop(indexes).reset_index(drop=True)
    df_group = pd.DataFrame(
        {
            "layer": df_group.layer,
            "z_in": df_group.zf.shift().fillna(start_depth),
            "zf": df_group.zf,
        }
    )
    df_group.iloc[-1, df_group.columns.get_loc("zf")] = depth
    return df_group.pipe(calculate_thickness).pipe(calculate_z_centr)


def calculate_thickness(df):
    """
    Assign the thickness to an existing DataFrame.

    :param df: Original DataFrame.
    :return: Dataframe with thickness column.
    """
    return df.assign(thickness=(df["zf"] - df["z_in"]))


def calculate_z_centr(df):
    """
    Assign the central z to each layer of an existing DataFrame.

    :param df: Original DataFrame.
    :return: Dataframe with the z_centr column.
    """
    return df.assign(z_centr=(df["zf"] + df["z_in"]) / 2)


def calculate_zf_NAP(df, z_id):
    """
    Assign the zf with respect to NAP to each layer of a DataFrame.

    :param df: Original DataFrame.
    :param z_id: (float) Elevation with respect to the NAP of my field.
    :return: DataFrame with zf_NAP column.
    """
    return df.assign(zf_NAP=(z_id - df["zf"]))


def calculate_z_in_NAP(df, z_id):
    """
    Assign z_in with respect to NAP to each layer of a DataFrame.

    :param df: Original DataFrame.
    :param z_id: Elevation with respect to the NAP of my field.
    :return:  DataFrame with z_in_NAP column.
    """
    return df.assign(z_in_NAP=(z_id - df["z_in"]))


def calculate_z_centr_NAP(df, z_id):
    """
    Assign z_centr with respect to NAP to each layer of a DataFrame.
    :param df: Original DataFrame.
    :param z_id: Elevation with respect to the NAP of my field.
    :return:  DataFrame with z_centr_NAP column.
    """
    return df.assign(z_centr_NAP=(z_id - df["z_centr"]))
