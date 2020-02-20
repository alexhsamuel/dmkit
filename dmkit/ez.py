#-------------------------------------------------------------------------------

NONE = object()

def is_repl():
    return True


def fuzzy_match(string, options):
    string = str(string).lower()
    options = [ o for o in options if not str(o).startswith("_") ]
    matches = { o for o in options if str(o).lower().startswith(string) }
    if len(matches) == 0:
        raise LookupError(f"no match: {string}")
    elif len(matches) == 1:
        match, = matches
        return match
    else:
        matches = " ".join( str(o) for o in matches )
        raise LookupError(f"ambiguous match: {string}: {matches}")


def fuzzy_get(mapping, key, default=NONE):
    try:
        key = fuzzy_match(str(key), mapping)
    except LookupError:
        if default is NONE:
            raise KeyError(key) from None
        else:
            return default
    else:
        return mapping[key]
    


class EzFormat:

    NAME_WIDTH = 24

    def __genrepr__(self, indent=""):
        width = self.NAME_WIDTH - len(indent)
        for name, obj in self.__dict__.items():
            if name.startswith("_"):
                continue
            try:
                fmt = obj.__genrepr__(indent=indent + "  ")
            except AttributeError:
                name = format(name + ":", f"{width}s")
                yield indent + name + str(obj)
            else:
                yield indent + name + ":"
                yield from fmt


    def __repr__(self):
        if is_repl():
            return "\n".join(self.__genrepr__())
        else:
            return super().__repr__()



class EzAttr:

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


    def __getattr__(self, name):
        try:
            name = fuzzy_match(name, dir(self))
        except LookupError:
            raise AttributeError(name) from None
        else:
            return getattr(self, name)



class EzObject(EzFormat, EzAttr):

    pass



class EzList(list):

    def __getattr__(self, name):
        items = { i.name: i for i in self }
        try:
            name = fuzzy_match(name, items)
        except LookupError:
            raise AttributeError(name)
        else:
            return items[name]
        

    def __genrepr__(self, indent=""):
        width = EzObject.NAME_WIDTH - len(indent)
        for obj in self:
            name = obj.name
            try:
                fmt = obj.__genrepr__(indent=indent + "  ")
            except AttributeError:
                name = format(name + ":", f"{width}s")
                yield indent + name + str(obj)
            else:
                yield indent + name + ":"
                yield from fmt


    def __repr__(self):
        if is_repl():
            return "\n".join(self.__genrepr__())
        else:
            return super().__repr__()

