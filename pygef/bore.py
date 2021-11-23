from typing import Union

import pygef.plot_utils as plot
from pygef.base import Base
from pygef.broxml import _BroXmlBore
from pygef.gef import _GefBore


class Bore(Base):
    """
    ** Bore attributes:**
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
            DataFrame containing the columns: [
                                                "depth_top",
                                                "depth_bottom",
                                                "soil_code",
                                                "gravel_component",
                                                "sand_component",
                                                "clay_component",
                                                "loam_component",
                                                "peat_component",
                                                "silt_component",
                                                "remarks",
                                            ]
    """

    def __init__(self, path=None, content: dict = None):
        """
        Bore class.

        Parameters
        ----------
        path:
            Path to the file.
        content: dict
            Dictionary with keys: ["string", "file_type"]
                -string: str
                    String version of the file.
                -file_type:
                    One of [gef, xml]
        """
        super().__init__()

        parsed: Union[_BroXmlBore, _GefBore]

        self.nen_version = None

        if content is not None:
            assert (
                content["file_type"] == "gef" or content["file_type"] == "xml"
            ), f"file_type can be only one of [gef, xml] "
            assert content["string"] is not None, "content['string'] must be specified"
            if content["file_type"] == "gef":
                parsed = _GefBore(string=content["string"])
            elif content["file_type"] == "xml":
                parsed = _BroXmlBore(string=content["string"])

        elif path is not None:
            if path.lower().endswith("gef"):
                parsed = _GefBore(path)
            elif path.lower().endswith("xml"):
                parsed = _BroXmlBore(path)
        else:
            raise ValueError("One of [path, (string, file_type)] should be not None.")

        self.__dict__.update(parsed.__dict__)

    def plot(self, figsize=(11, 8), show=False, dpi=100):
        """
        Plot plot of soil components over the depth.

        Parameters
        ----------
        show: bool
            If True the plot is showed, else the matplotlib.pytplot.figure is returned
        figsize: tuple
            Figsize of the plot, default (11, 8).
        dpi: int
            Dpi figure
        Returns
        -------
        matplotlib.pyplot.figure
        """
        if self.nen_version == "NEN 5104":
            return plot.plot_bore(self.df, figsize=figsize, show=show, dpi=dpi)
        elif self.nen_version == "NEN-EN-ISO 14688":
            return plot.plot_bore(self.df, figsize=figsize, show=show, dpi=dpi)
        else:
            raise ValueError(
                "Supported NEN version are only: 'NEN 5104' and 'NEN-EN-ISO 14688'"
            )
