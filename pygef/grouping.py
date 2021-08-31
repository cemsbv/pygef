import polars as pl


class GroupClassification:
    def __init__(self, zid, df, min_thickness):
        self.zid = zid
        start_depth = df["depth"][0]
        df_group = df[:, ["depth", "soil_type"]]

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
        # df_group = (
        #    df_group.groupby((df_group[column1] != df_group[column1].shift(periods=1)).cumsum())
        #    .max()
        #    .reset_index(drop=True)
        # )
        # df_group = (
        #     df_group.groupby(column1)
        #     .agg(pl.last("*").exclude(column1).keep_name())
        #     .sort(column2)
        # )

        df_group = pl.DataFrame(
            {
                "layer": df_group[column1],
                "z_in": df_group[column2].shift(periods=1),
                # TODO: .fillna(start_depth),
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
    df_group = df_group[:, ["zf", "layer", "thickness"]]

    # Get the last zf value
    depth = df_group["zf"].tail(length=1)[0]

    df_group = df_group.filter(pl.col("thickness") >= min_thickness)

    # Create a new column z_in by shifting zf and filling the empty first spot
    # with the starting depth
    df_group = df_group.with_column(
        pl.col("zf").shift(periods=1).fill_null(start_depth).alias("z_in")
    )

    # TODO: df_group[-1, df_group.columns.get_loc("zf")] = depth

    return df_group.pipe(calculate_thickness).pipe(calculate_z_centr)


def calculate_thickness(df):
    """
    Assign the thickness to an existing DataFrame.

    :param df: Original DataFrame.
    :return: Dataframe with thickness column.
    """
    df["thickness"] = df["zf"] - df["z_in"]

    return df


def calculate_z_centr(df):
    """
    Assign the central z to each layer of an existing DataFrame.

    :param df: Original DataFrame.
    :return: Dataframe with the z_centr column.
    """
    df["z_centr"] = (df["zf"] + df["z_in"]) / 2

    return df


def calculate_zf_NAP(df, z_id):
    """
    Assign the zf with respect to NAP to each layer of a DataFrame.

    :param df: Original DataFrame.
    :param z_id: (float) Elevation with respect to the NAP of my field.
    :return: DataFrame with zf_NAP column.
    """
    df["zf_NAP"] = z_id - df["zf"]

    return df


def calculate_z_in_NAP(df, z_id):
    """
    Assign z_in with respect to NAP to each layer of a DataFrame.

    :param df: Original DataFrame.
    :param z_id: Elevation with respect to the NAP of my field.
    :return:  DataFrame with z_in_NAP column.
    """
    df["z_in_NAP"] = z_id - df["z_in"]

    return df


def calculate_z_centr_NAP(df, z_id):
    """
    Assign z_centr with respect to NAP to each layer of a DataFrame.
    :param df: Original DataFrame.
    :param z_id: Elevation with respect to the NAP of my field.
    :return:  DataFrame with z_centr_NAP column.
    """
    df["z_centr_NAP"] = z_id - df["z_centr"]

    return df
