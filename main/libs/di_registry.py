""" Dead-simple DI registry.
    This is used to isolate real side effecting clients (talking to network
    services, reading from disk, etc.) from functions that perform some
    business logic as well.
"""
import re
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, Pattern, Type, TypeVar

from libs.fun import camel_to_snake

__REGISTRY = {}

Client = TypeVar("Client")

ReturnType = TypeVar("ReturnType")
ToDecorate = Callable[..., ReturnType]
Decorated = Callable[..., ReturnType]
Decorator = Callable[[ToDecorate], Decorated]


def _key(client_class: Type[Client]) -> str:
    return camel_to_snake(client_class.__name__)


def register(client_class: Type[Client], instance: Client) -> None:
    """ Register an instantiated client.
    """
    __REGISTRY[_key(client_class)] = instance


def register_fn(name: str, fn: Any) -> None:
    """registers a function"""
    __REGISTRY[name] = fn
    return fn


def deregister(client_class: Type[Client]) -> None:
    """ De-register a client.
    """
    if _key(client_class) in __REGISTRY:
        del __REGISTRY[_key(client_class)]


def _default_close(_: Client) -> None:
    pass


def inject_fn(fn_name: str) -> Decorator:
    """Inject a function based on the provided name."""

    def wrapper(fn: ToDecorate) -> Decorated:

        if not fn_name:
            return fn

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> ReturnType:
            injected_kwargs = (
                {fn_name: __REGISTRY[fn_name]} if fn_name in __REGISTRY else {}
            )
            try:
                return fn(*args, **{**injected_kwargs, **kwargs})
            except TypeError:
                # I know it's ugly, sorry.
                print(
                    "Warning, got a double argument, not injecting the supplied function."
                )
                return fn(*args, **kwargs)

        return wrapped

    return wrapper


def inject(*client_classes: Type[Client]) -> Decorator:
    """ Decorate receiving functions with 'inject' and supply the
        wanted type. At runtime, the function will receive a single instance
        via the 'client' keyword argument, or, if multiple types are supplied,
        via arguments named after the CamelCase -> snake_case transformations.

        Example:

        @inject(DnsClient, GitClient)
        def will_effect(
            some_arg: str, dns_client: DnsClient, git_client: GitClient
        ) -> None:
            dns_client.do_stuff()
            git_client.do_stuff()

        # can now simply be called as:
        will_effect(some_arg_value)
    """

    def wrapper(fn: ToDecorate) -> Decorated:
        if not client_classes:
            return fn

        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> ReturnType:
            if len(client_classes) == 1:
                _cname = _key(client_classes[0])
                injected_kwargs = (
                    {"client": __REGISTRY[_cname]}
                    if _cname in __REGISTRY
                    else {}
                )
            else:
                injected_kwargs = {
                    _key(_): __REGISTRY[_key(_)]
                    for _ in client_classes
                    if _key(_) in __REGISTRY
                }

            print(f"returning with {args} and {kwargs} and {injected_kwargs}")
            return fn(*args, **{**injected_kwargs, **kwargs})

        return wrapped

    return wrapper


@contextmanager
def client(
    instance_class: Type[Client],
    instance: Client,
    on_close: Callable[[Client], None] = _default_close,
) -> Generator[Client, None, None]:
    """ Convenience function for scoped client injection.
        Can be useful while writing tests to make sure Mocks get injected
        instead of real clients.
    """
    register(instance_class, instance)
    yield instance
    on_close(instance)
    deregister(instance_class)


CTS: Pattern = re.compile(r"(?<!^)(?=[A-Z])")


def _camel_to_snake(text: str) -> str:
    return CTS.sub("_", text).lower()
