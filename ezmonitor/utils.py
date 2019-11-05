import yaml
from pathlib import Path

__default_confg = Path("config.yaml")

def load_config(path: Path = __default_confg) -> dict:
    try:
        with open(path) as fil:
            config = yaml.safe_load(fil)
    except (OSError, FileNotFoundError) as e:
        raise e
    finally:
        return config

def first(iterable, condition = lambda x: True):
    """
    Returns the first item in the `iterable` that
    satisfies the `condition`.

    If the condition is not given, returns the first item of
    the iterable.

    Raises `StopIteration` if no item satysfing the condition is found.

    >>> first( (1,2,3), condition=lambda x: x % 2 == 0)
    2
    >>> first(range(3, 100))
    3
    >>> first( () )
    Traceback (most recent call last):
    ...
    StopIteration
    """

    return next(x for x in iterable if condition(x))