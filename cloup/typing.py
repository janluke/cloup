__all__ = ['MISSING', 'Possibly',  'Decorator', 'F']

from enum import Enum
from typing import Callable, TypeVar, Union


# PEP-blessed solution for defining a Singleton type:
# https://www.python.org/dev/peps/pep-0484/#id30
class _Missing(Enum):
    flag = 'Missing'


MISSING = _Missing.flag
"""Singleton that indicates a missing value to use when None can't be used."""

_T = TypeVar('_T')
Possibly = Union[_Missing, _T]
"""Possibly[T] is MISSING or a value of type T."""

F = TypeVar('F', bound=Callable)
"""Type variable for a Callable."""

Decorator = Callable[[Callable], Callable]
"""Type alias for a simple function decorator."""
