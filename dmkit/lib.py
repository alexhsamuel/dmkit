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


