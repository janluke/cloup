"""Generic utilities."""


def class_name(obj):
    return obj.__class__.__name__


def check_value(condition: bool, msg: str = ''):
    if not condition:
        raise ValueError(msg)
