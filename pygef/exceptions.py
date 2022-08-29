from __future__ import annotations


def concat_args(msg: str, args: tuple):
    if not isinstance(args, tuple):
        args = tuple(args)
    return " ".join(str(x) for x in [msg, *args])


class UserError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ParseGefError(UserError):
    def __init__(self, *args, **kwargs):
        msg = "Pygef encountered an error during parsing of the .gef file"
        UserError.__init__(self, concat_args(msg, args), **kwargs)


class ParseCptGefError(ParseGefError):
    def __init__(self, *args, **kwargs):
        msg = "for CPT data"
        UserError.__init__(self, concat_args(msg, args), **kwargs)
