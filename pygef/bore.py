from pygef.base import BaseParser
import pygef.plot_utils as plot
from pygef.gef import ParseGefBore
from pygef.broxml import ParseBroXmlBore


class Bore(BaseParser):
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

        if content is not None:
            assert (
                content["file_type"] == "gef" or content["file_type"] == "xml"
            ), f"file_type can be only one of [gef, xml] "
            assert content["string"] is not None, "content['string'] must be specified"
            if content["file_type"] == "gef":
                parsed = ParseGefBore(string=content["string"])
            elif content["file_type"] == "xml":
                parsed = ParseBroXmlBore(string=content["string"])

        elif path is not None:
            if path.lower().endswith("gef"):
                parsed = ParseGefBore(path)
            elif path.lower().endswith("xml"):
                parsed = ParseBroXmlBore(path)
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
        return plot.plot_bore(self.df, figsize=figsize, show=show, dpi=dpi)
