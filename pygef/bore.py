from pygef.base import BaseParser
import pygef.plot_utils as plot


class Bore(BaseParser):
    def __init__(self, path=None, string=None, file_type=None):
        """
        Bore class.

        Parameters
        ----------
        path:
            Path to the file.
        string: str
            String version of the file.
        file_type:
            One of [gef, xml]
        """
        super().__init__(path=path, string=string, file_type=file_type)

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
