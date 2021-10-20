from abc import ABC


class _BroXml(ABC):
    def __init__(self, path=None, string=None):
        pass


class _BroXmlBore(_BroXml):
    def __init__(self, path=None, string=None):
        super().__init__(path=path, string=string)

        raise NotImplementedError(
            "The parsing of boreholes in xml format is not yet available."
        )


class _BroXmlCpt(_BroXml):
    def __init__(self, path=None, string=None):
        super().__init__(path=path, string=string)

        raise NotImplementedError(
            "The parsing of cpts in xml format is not yet available."
        )
