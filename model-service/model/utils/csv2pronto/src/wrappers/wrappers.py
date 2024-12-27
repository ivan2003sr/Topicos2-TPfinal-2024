import functools
from typing import Callable

from rdflib import BNode, Namespace

from ..incrementals.incrementals import Incremental
from ..null_objects.null_objects import NoneNode


def default_to_BNode(func: Callable) -> Callable:
    """
    Decorator that returns a `BNode` if the URI creation raises a
    `KeyError`.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return BNode()

    return wrapper


def default_to_NoneNode(func: Callable) -> Callable:
    """
    Decorator that returns a `NoneNode` if the URI creation raises a
    `KeyError`.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return NoneNode()

    return wrapper


def default_to_incremental(ns: Namespace, inc: Incremental) -> Callable:
    """
    Decorator that returns a URI with an incremental value if the URI
    creation raises a `KeyError`.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyError:
                return ns[inc.fragment()]

        return wrapper

    return decorator
