import pandas as pd


class GroupClassification:
    def __init__(self, df, dict_soil_type, min_thickness):
        df_group = df.copy()
        self.zid = df_group['elevation_respect_to_NAP'].iloc[0]
        df_group = df_group.loc[:, ['depth', 'soil_type']]
        self.df_group = (df_group
                         .pipe(self.group_equal_layers, 'soil_type', 'depth')
                         .pipe(self.group_significant_layers, dict_soil_type, min_thickness)
                         .pipe(self.group_equal_layers, 'layer', 'zf')
                         )

    def group_equal_layers(self, df_group, column1, column2):
        """
        Group equal layers by checking the difference between the original column of soil type and the shifted one and
        storing that in a boolean array, then it does a cumulative sum of the boolean array and it groups the
        result of the cumulative sum.

        :param df_group: Original Dataframe to group.
        :param column1: Column to group, it can be soil_type or layer.
        :param column2: Depth or zf (final z).
        :return: Grouped dataframe.
        """
        df_group = (df_group.groupby((df_group[column1] != df_group[column1].shift())
                                     .cumsum())
                    .max()
                    .reset_index(drop=True))

        df_group = pd.DataFrame({'layer': df_group[column1],
                                 'z_in': df_group[column2].shift().fillna(0),
                                 'zf': df_group[column2]})
        return (df_group
                .pipe(calculate_thickness)
                .pipe(calculate_z_centr)
                .pipe(calculate_zf_NAP, self.zid))

    def group_significant_layers(self, df_group, min_thickness):
        """
        Drop the layers with thickness < min_thickness and adjust the limits of the others.
        :param df_group: Original dataframe.
        :param min_thickness: Minimum thickness.
        :return: Dataframe without the dropped layers.
        """
        df_group = df_group.loc[:, ['zf', 'layer', 'thickness']]
        depth = df_group['zf'].iloc[-1]
        indexes = df_group[df_group.thickness < min_thickness].index.values.tolist()
        df_group = df_group.drop(indexes).reset_index(drop=True)
        df_group = pd.DataFrame({'layer': df_group.layer,
                                 'z_in': df_group.zf.shift().fillna(0),
                                 'zf': df_group.zf})
        df_group['zf'].iloc[-1] = depth
        return (df_group
                .pipe(calculate_thickness)
                .pipe(calculate_z_centr))


def calculate_thickness(df):
    """
    Assign the thickness to an existing Dataframe.

    :param df: Original dataframe.
    :return: Dataframe with thickness column.
    """
    return df.assign(thickness=(df['zf'] - df['z_in']))


def calculate_z_centr(df):
    """
    Assign the central z to each layer of an existing Dataframe.

    :param df: Original dataframe.
    :return: Dataframe with the z_centr column.
    """
    return df.assign(z_centr=(df['zf'] + df['z_in']) / 2)


def calculate_zf_NAP(df, z_id):
    """
    Assign the zf respect to NAP to each layer of a dataframe.

    :param df: Original dataframe.
    :param z_id: Elevation respt to the NAp of my field.
    :return: Dataframe with zf_NAP column.
    """
    return df.assign(zf_NAP=(z_id - df['zf']))
