from abc import ABC
from pygef.gef import ParseGEF
from pygef.broxml import ParseBroXml


class BaseParser(ABC):
    def __init__(self, path=None, string=None, file_type=None):
        """
        Abstract base class to parse cpt and boreholes in gef or xml format.

        Parameters
        ----------
        path:
            Path to the file.
        string: str
            String version of the file.
        file_type:
            One of [gef, xml]
        """
        self.test_id = None
        self.type = None
        self.x = None
        self.y = None
        self.df = None
        self.zid = None

        if file_type is not None:
            assert (
                file_type == "gef" or file_type == "xml"
            ), f"file_type can be only one of [gef, xml] "
        if path is not None:
            if path.lower().endswith("gef"):
                parsed = ParseGEF(path)
            elif path.lower().endswith("xml"):
                raise NotImplementedError
                # parsed = ParseBroXml(path)
        elif string is not None and file_type is not None:
            if file_type == "gef":
                parsed = ParseGEF(string=string)
            elif file_type == "xml":
                # parsed = ParseBroXml()
                raise NotImplementedError
        else:
            raise ValueError("One of [path, (string, file_type)] should be not None.")

        self.__dict__.update(parsed.__dict__)

    def __str__(self):
        return (
            "test id: {} \n"
            "type: {} \n"
            "(x,y): ({:.2f},{:.2f}) \n"
            "First rows of dataframe: \n {}".format(
                self.test_id, self.type, self.x, self.y, self.df.head(2)
            )
        )
