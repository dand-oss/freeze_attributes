"""

Disallows creating attributes after __init__.

https://stackoverflow.com/a/29368642
"""
import typing
from functools import wraps


def freeze_attributes(cls: typing.Type) -> typing.Type:
    """
    Class decorator which disallows creating attributes after __init__.

    Monkeypatches __setattr__ to check for attr before setting
    Set frozen flag after __init__

    There are only two lines that do the WORK, the rest is convenience.

    :param cls:
    """
    # class variable flag to check "frozen"
    cls.__is_frozen = False

    def _setattr_check_exists(
        self: typing.Any, key: str, value: typing.Any
    ) -> None:
        """
        Proxy for __setattr__ which checks attr already exists.

        :param self: the class
        :param key: name of attribute to set
        :param value: value to set in attribute
        :raises AttributeError:
        """
        # hasattr costs an extra lookup at runtime...
        if self.__is_frozen and not hasattr(self, key):
            raise AttributeError(
                f"Class {cls.__name__} is frozen. Cannot set {key} = {value}"
            )

        # WORK - send to "the real one"
        object.__setattr__(self, key, value)

    def _flag_class_as_frozen_attr(
        func: typing.Callable,
    ) -> typing.Callable:
        """
        Member function proxy which sets the class frozen flag after invocation.

        :param func: function to be wrap
        """

        @wraps(func)
        def the_wrapper(
            self: typing.Any, *args: typing.Any, **kwargs: typing.Any
        ) -> None:
            r"""
            Decorate to set class frozen flag.

            Apply to __init__

            :param \*args:
            :param \**kwargs:
            """
            func(self, *args, **kwargs)

            # WORK - set the class flag
            self.__is_frozen = True

        return the_wrapper

    # monkeypatch __init__ and __setattr__
    cls.__setattr__ = _setattr_check_exists
    cls.__init__ = _flag_class_as_frozen_attr(cls.__init__)

    return cls
