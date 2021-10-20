import logging

from pygef.base import BaseParser
from pygef import been_jefferies, robertson
from pygef.grouping import GroupClassification
import pygef.plot_utils as plot

logger = logging.getLogger(__name__)


class Cpt(BaseParser):
    def __init__(self, path=None, string=None, file_type=None):
        """
        Cpt class.

        Parameters
        ----------
        path:
            Path to the file.
        string: str
            String version of the file.
        file_type:
            One of [gef, xml]
        """
        self.net_surface_area_quotient_of_the_cone_tip = None
        self.pre_excavated_depth = None

        super().__init__(path=path, string=string, file_type=file_type)

    def classify(
        self,
        classification,
        water_level_NAP=None,
        water_level_wrt_depth=None,
        p_a=0.1,
        new=True,
        do_grouping=False,
        min_thickness=None,
    ):
        """
        Classify each row of the cpt type.

        Parameters
        ----------
        classification: str
            Specify the classification, possible choices : "robertson", "been_jefferies".
        water_level_NAP: float, only for cpt type, necessary for the classification: give this or water_level_wrt_depth
            Water level with respect to NAP
        water_level_wrt_depth: float, only for cpt type, necessary for the classification: give this or water_level_NAP
            Water level with respect to the ground_level [0], it should be a negative value.
        p_a: float
            Atmospheric pressure. Default: 0.1 MPa.
        new: bool, default:True
            If True and the classification is robertson, the new(2016) implementation of robertson is used.
        do_grouping: bool,  optional for the classification
            If True a group classification is added to the plot.
        min_thickness: float, optional for the classification [m]
            If specified together with the do_grouping set to True, a group classification is added to the plot.
            The grouping is a simple algorithm that merge all the layers < min_thickness with the last above one > min_thickness.
            In order to not make a big error do not use a value bigger then 0.2 m

        Returns
        -------
        df: polars.DataFrame
        If do_grouping is True a polars.DataFrame with the grouped layer is returned otherwise a polars.DataFrame with
        a classification for each row is returned.

        """
        # todo: refactor arguments, the arguments connected to each other
        #  should be given as a dict or tuple, check order
        water_level_and_zid_NAP = dict(water_level_NAP=water_level_NAP, zid=self.zid)

        if water_level_NAP is None and water_level_wrt_depth is None:
            water_level_wrt_depth = -1
            logger.warning(
                f"You did not input the water level, a default value of -1 m respect to the ground is used."
                f" Change it using the kwagr water_level_NAP or water_level_wrt_depth."
            )
        if min_thickness is None:
            min_thickness = 0.2
            logger.warning(
                f"You did not input the accepted minimum thickness, a default value of 0.2 m is used."
                f" Change it using th kwarg min_thickness"
            )

        if classification == "robertson":
            df = robertson.classify(
                self.df,
                water_level_and_zid_NAP=water_level_and_zid_NAP,
                water_level_wrt_depth=water_level_wrt_depth,
                new=new,
                area_quotient_cone_tip=self.net_surface_area_quotient_of_the_cone_tip,
                pre_excavated_depth=self.pre_excavated_depth,
                p_a=p_a,
            )
            if do_grouping:
                return GroupClassification(self.zid, df, min_thickness).df_group
            return df

        elif classification == "been_jefferies":
            df = been_jefferies.classify(
                self.df,
                water_level_and_zid_NAP=water_level_and_zid_NAP,
                water_level_wrt_depth=water_level_wrt_depth,
                area_quotient_cone_tip=self.net_surface_area_quotient_of_the_cone_tip,
                pre_excavated_depth=self.pre_excavated_depth,
            )
            if do_grouping:
                return GroupClassification(self.zid, df, min_thickness).df_group
            return df
        else:
            raise ValueError(
                f"Could not find {classification}. Check the spelling or classification not defined in the library"
            )

    def plot(
        self,
        classification=None,
        water_level_NAP=None,
        water_level_wrt_depth=None,
        min_thickness=None,
        p_a=0.1,
        new=True,
        show=False,
        figsize=(11, 8),
        df_group=None,
        do_grouping=False,
        grid_step_x=None,
        dpi=100,
        colors=None,
        z_NAP=False,
    ):
        """
        Plot the *.gef file and return matplotlib.pyplot.figure .

        It works both with a cpt or borehole type file. If no argument it is passed it returns:
        - CPT: plot of qc [MPa] and Friction ratio [%]
        - BOREHOLE: plot of soil components over the depth.

        Parameters
        ----------
        classification: str, only for cpt type
            If classification ("robertson", "been_jefferies") is specified a subplot is added with the classification
            for each cpt row.
        water_level_NAP: float, only for cpt type, necessary for the classification: give this or water_level_wrt_depth
            Water level with respect to NAP
        water_level_wrt_depth: float, only for cpt type, necessary for the classification: give this or water_level_NAP
            Water level with respect to the ground_level [0], it should be a negative value.
        min_thickness: float, only for cpt type, optional for the classification [m]
            If specified together with the do_grouping set to True, a group classification is added to the plot.
            The grouping is a simple algorithm that merge all the layers < min_thickness with the last above one >
            min_thickness.
            In order to not make a big error do not use a value bigger then 0.2 m
        p_a: float, only for cpt type, optional for the classification
            Atmospheric pressure. Default: 0.1 MPa.
        new: bool, only for cpt type, optional for the classification default:True
            If True and the classification is robertson, the new(2016) implementation of robertson is used.
        show: bool
            If True the plot is showed, else the matplotlib.pytplot.figure is returned
        figsize: tuple
            Figsize of the plot, default (11, 8).
        df_group: polars.DataFrame, only for cpt type, optional for the classification
            Use this argument to plot a defined soil layering next to the other subplots.
            It should contain the columns:
                - layer
                    Name of layer, should be either BeenJefferies of Robertson soil type,
                    if it is different then also the argument colors should be passed.
                - z_centr_NAP
                    Z value of the middle of the layer
                - thickness
                    Thickness of the layer
        do_grouping: bool, only for cpt type, optional for the classification
            If True a group classification is added to the plot.
        grid_step_x: float, only for cpt type, default: None
            Grid step for qc and Fr subplots.
        dpi: int
            Dpi figure
        colors: dict
            Dictionary containing the colors associated to each soil type, if specified
        z_NAP: bool
            If True the Z-axis is with respect to NAP.
        Returns
        -------
        matplotlib.pyplot.figure
        """
        # todo: refactor arguments, the arguments connected to each other should
        #  be given as a dict or tuple, check order
        if classification is None:
            df = self.df
        else:
            df = self.classify(
                classification=classification,
                water_level_NAP=water_level_NAP,
                water_level_wrt_depth=water_level_wrt_depth,
                p_a=p_a,
                new=new,
            )

            if df_group is None and do_grouping is True:
                df_group = self.classify(
                    classification=classification,
                    water_level_NAP=water_level_NAP,
                    water_level_wrt_depth=water_level_wrt_depth,
                    p_a=p_a,
                    new=new,
                    do_grouping=True,
                    min_thickness=min_thickness,
                )

        return plot.plot_cpt(
            df,
            df_group,
            classification,
            show=show,
            figsize=figsize,
            grid_step_x=grid_step_x,
            colors=colors,
            dpi=dpi,
            z_NAP=z_NAP,
        )
