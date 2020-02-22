import re

#-------------------------------------------------------------------------------

NONE = object()

def is_repl():
    return True


class AmbiguousMatchError(LookupError):

    def __init__(self, string, matches):
        matches = ", ".join( str(m) for m in matches )
        super().__init__(f"ambiguous match: {string}: {matches}")



def _substring_match(string, target):
    """

      >>> _substring_match("ellwo", "hello, world!")
      True
      >>> _substring_match("fuck", "fire truck")
      True
      >>> _substring_match("yolo", "you only live twice")
      False
      >>> _substring_match("lp8", "love potion #9")
      False

    """
    for c in string:
        try:
            i = target.index(c)
        except ValueError:
            return False
        else:
            target = target[i + 1 :]
    else:
        return True


def match(string, options):
    string = str(string).lower()
    options = [ o for o in options if not str(o).startswith("_") ]
    targets = [ str(o).lower() for o in options ]

    # Try prefix match.
    matches = [ o for o, t in zip(options, targets) if t.startswith(string) ]
    if len(matches) == 1:
        return matches[0]

    # Try substring match.
    matches = [ o for o, t in zip(options, targets) if _substring_match(string, t) ]
    if len(matches) == 0:
        pass
    elif len(matches) == 1:
        return matches[0]
    else:
        raise AmbiguousMatchError(string, matches)

    raise LookupError(f"no match: {string}")


def get(mapping, key, default=NONE):
    try:
        key = match(str(key), mapping)
    except LookupError:
        if default is NONE:
            raise KeyError(key) from None
        else:
            return default
    else:
        return mapping[key]
    

def sanitize(string):
    """
    Converts `string` to an identifier.

      >>> sanitize("Love Potion #9")
      'LovePotion9'
      >>> sanitize("99 red balloons")
      '_99redballoons'
    
    """
    string = str(string)
    if string.isidentifier():
        return string
    else:
        string = re.sub(r"[^a-zA-Z0-9_]", "", string)
        if len(string) > 0 and string[0] in "0123456789":
            string = "_" + string
        assert string.isidentifier()
        return string


class Format:

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



class Attr:

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


    def __getattr__(self, name):
        try:
            name = match(name, dir(self))
        except LookupError:
            raise AttributeError(name) from None
        else:
            return getattr(self, name)



class Object(Format, Attr):

    pass



class List(list):

    def __getattr__(self, name):
        items = { i.name: i for i in self }
        try:
            name = match(name, items)
        except AmbiguousMatchError as exc:
            raise AttributeError(str(exc)) # from None
        except LookupError:
            raise AttributeError(name) from None
        else:
            return items[name]
        

    def __genrepr__(self, indent=""):
        width = Object.NAME_WIDTH - len(indent)
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


    def __dir__(self):
        return ( sanitize(i.name) for i in self )



