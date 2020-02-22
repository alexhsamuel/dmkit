import collections.abc
import itertools


def flatten(items):
    """
    Generates items, or subitems from items.
    """
    for i in items:
        if is_seq(i):
            yield from i
        else:
            yield i


def group_by(items, key=None):
    return itertools.groupby(sorted(items, key=key), key=key)


def if_none(*objs):
    """
    Returns the first item in `objs` that is not none.

      >>> if_none(42, "Hello!")
      42
      >>> if_none(None, "Hello!")
      'Hello'

    """
    for obj in objs:
        if obj is not None:
            return obj
    else:
        return None


def is_seq(obj):
    """
    True if `obj` is a non-string sequence.
    """
    return (
        isinstance(obj, collections.abc.Sequence)
        and not isinstance(obj, (bytes, str))
    )


