from abc import ABC


class Base(ABC):
    def __init__(self):
        """
        Abstract base class to parse cpt and boreholes in gef or xml format.

        """
        self.test_id = None
        self.type = None
        self.x = None
        self.y = None
        self.df = None
        self.zid = None

    def __str__(self):
        return (
            "test id: {} \n"
            "type: {} \n"
            "(x,y): ({:.2f},{:.2f}) \n"
            "First rows of dataframe: \n {}".format(
                self.test_id, self.type, self.x, self.y, self.df.head(2)
            )
        )
