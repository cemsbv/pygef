class ParseBroXml:
    def __init__(self, path=None, string=None):
        pass


class ParseBroXmlBore(ParseBroXml):
    def __init__(self, path=None, string=None):
        super().__init__(path=path, string=string)

        raise NotImplementedError(
            "The parsing of bore in format xml is not yet available."
        )


class ParseBroXmlCpt(ParseBroXml):
    def __init__(self, path=None, string=None):
        super().__init__(path=path, string=string)

        raise NotImplementedError(
            "The parsing of cpt in format xml is not yet available."
        )
