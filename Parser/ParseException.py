class ParseException(Exception):
    """
        Exception class for signaling logic inside the parser
        This should NOT be confused with the error state inside the parser
        The latter one indicates an error in the parsing process and will yield a
        syntax error to the end user. This class should instead show errors to the
        programmer.
    """
    pass
