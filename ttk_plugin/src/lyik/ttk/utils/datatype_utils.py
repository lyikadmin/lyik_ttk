import inspect


def props_dict(obj, include_private=False, *, skip_errors=True):
    """Return a dict of {property_name: value} for @property attributes only."""
    out = {}
    for name, prop in inspect.getmembers(type(obj), lambda o: isinstance(o, property)):
        if not include_private and name.startswith("_"):
            continue
        try:
            out[name] = getattr(obj, name)
        except Exception as e:
            if skip_errors:
                continue
            raise
    return out
