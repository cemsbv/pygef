import logging
from typing import Union

import pygef.plot_utils as plot
from pygef import been_jefferies, robertson
from pygef.base import Base
from pygef.broxml import _BroXmlCpt
from pygef.gef import _GefCpt
from pygef.grouping import GroupClassification

logger = logging.getLogger(__name__)


class Cpt(Base):
    """
    ** Cpt attributes:**
        *Always present:*
            type: str
                Type of the gef file
            project_id: str
                Project id
            x: float
                X coordinate respect to the coordinate system
            y: float
                Y coordinate respect to the coordinate system
            zid: float
                Z coordinate respect to the height system
            height_system: float
                Type of coordinate system, 31000 is NAP
            file_date: datatime.datetime
                Start date time
            test_id: str
                Identifying name of gef file.
            s: str
                String version of gef file.
            df: polars.DataFrame
                DataFrame containing the same column contained in the original .gef file and
                some additional columns [depth, elevation_with_respect_to_nap]

                Tip: Use depth column instead of the penetration_length, the depth is corrected
                with the inclination(if present).

                Note that the Friction ratio is always calculated from the fs and qc values and not parsed from the file.

                If this attribute is called after the classify method the columns relative to the classification
                are also contained.

        *Not always present*

            default: None
            The description is added only for the most important attributes, for the others check:
            https://publicwiki.deltares.nl/download/attachments/102204318/GEF-CPT.pdf?version=1&modificationDate=1409732008000&api=v2

            cpt_class: str
                Cpt class. The format is not standard so it might be not always properly parsed.
            column_void: str
                It is the definition of no value for the gef file
            nom_surface_area_cone_tip: float
                Nom. surface area of cone tip [mm2]
            nom_surface_area_friction_element: float
                Nom. surface area of friction casing [mm2]
            net_surface_area_quotient_of_the_cone_tip: float
                Net surface area quotient of cone tip [-]
            net_surface_area_quotient_of_the_friction_casing: float
                Net surface area quotient of friction casing [-]
            distance_between_cone_and_centre_of_friction_casing: float

            friction_present: float

            ppt_u1_present: float

            ppt_u2_present: float

            ppt_u3_present: float

            inclination_measurement_present: float

            use_of_back_flow_compensator: float

            type_of_cone_penetration_test: float

            pre_excavated_depth: float
                 Pre excavate depth [m]
            groundwater_level: float
                Ground water level [m]
            water_depth_offshore_activities: float
            end_depth_of_penetration_test: float
            stop_criteria: float

            zero_measurement_cone_before_penetration_test: float

            zero_measurement_cone_after_penetration_test: float

            zero_measurement_friction_before_penetration_test: float

            zero_measurement_friction_after_penetration_test: float

            zero_measurement_ppt_u1_before_penetration_test: float

            zero_measurement_ppt_u1_after_penetration_test: float

            zero_measurement_ppt_u2_before_penetration_test: float

            zero_measurement_ppt_u2_after_penetration_test: float

            zero_measurement_ppt_u3_before_penetration_test: float

            zero_measurement_ppt_u3_after_penetration_test: float

            zero_measurement_inclination_before_penetration_test: float

            zero_measurement_inclination_after_penetration_test: float

            zero_measurement_inclination_ns_before_penetration_test: float

            zero_measurement_inclination_ns_after_penetration_test: float

            zero_measurement_inclination_ew_before_penetration_test: float

            zero_measurement_inclination_ew_after_penetration_test : float

            mileage: float
    """

    def __init__(self, path=None, content: dict = None):
        """
        Cpt class.

        Parameters
        ----------
        path:
            Path to the file.
        content: dict
            Dictionary with keys: ["string", "file_type"]
                - string: str
                    String version of the file.
                - file_type: str
                    One of [gef, xml]
        """
        self.net_surface_area_quotient_of_the_cone_tip = None
        self.pre_excavated_depth = None

        super().__init__()

        parsed: Union[_BroXmlCpt, _GefCpt]

        if content is not None:
            assert (
                content["file_type"] == "gef" or content["file_type"] == "xml"
            ), f"file_type can be only one of [gef, xml] "
            assert content["string"] is not None, "content['string'] must be specified"
            if content["file_type"] == "gef":
                parsed = _GefCpt(string=content["string"])
            elif content["file_type"] == "xml":
                parsed = _BroXmlCpt(string=content["string"])

        elif path is not None:
            if path.lower().endswith("gef"):
                parsed = _GefCpt(path)
            elif path.lower().endswith("xml"):
                parsed = _BroXmlCpt(path)
        else:
            raise ValueError("One of [path, (string, file_type)] should be not None.")

        self.__dict__.update(parsed.__dict__)

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
            If do_grouping is True a polars.DataFrame with the grouped layer is returned otherwise a polars.DataFrame
            with a classification for each row is returned.

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
        Plot the cpt file and return matplotlib.pyplot.figure .

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
