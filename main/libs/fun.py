"""Funny helpers"""
import re
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    Set,
    TypeVar,
)

A = TypeVar("A", bound=Iterable)
B = TypeVar("B")
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def flatmap(f: Callable[[A], Iterable[B]], xs: Iterable[A]) -> Iterable[B]:
    """Map f over an iterable and flatten the result set."""
    return (y for x in xs for y in f(x))


def flatten(xs: Iterable[A]) -> Iterable[B]:
    """Flatten a set."""
    return (y for x in xs for y in x)


def filter_keys(mapping: Mapping[K, V], keys: Set[K]) -> Dict[K, V]:
    """Mask the given mapping, retaining only the specified keys."""
    return {k: mapping[k] for k in mapping if k not in keys}


def camel_to_snake(name: str) -> str:
    """CamelCase to snake_case"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def snake_case_keys(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Snakecase to camel_case for a dict"""
    return {camel_to_snake(k): v for k, v in input_dict.items()}


def snake_to_camel(name: str) -> str:
    """snake_case to CamelCase"""
    return "".join(word.title() for word in name.split("_"))


def camel_case_keys(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """CamelCase to snake_case for a dict"""
    return {snake_to_camel(k): v for k, v in input_dict.items()}


def try_exec(fn: Callable[..., B], *args: B, **kwargs: V) -> Optional[B]:
    """Try Execute fn, it's basically a wrapper to safely execute."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:  # pylint: disable=broad-except
        print(f" {fn.__name__} failed with exc {e}, returning None")
        return None
