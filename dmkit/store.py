import yaml

from   . import game

#-------------------------------------------------------------------------------

def is_repl():
    return True


def fuzzy_match(string, options):
    string = str(string).lower()
    matches = { o for o in options if str(o).lower().startswith(string) }
    if len(matches) == 0:
        raise LookupError(f"no match: {string}")
    elif len(matches) == 1:
        match, = matches
        return match
    else:
        matches = " ".join( str(o) for o in matches )
        raise LookupError(f"ambiguous match: {string}: {matches}")


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
                yield indent + name + repr(obj)
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
            name = fuzzy_match(name, self.__dict__)
        except LookupError:
            raise AttributeError(name)
        else:
            return self.__dict__[name]



class EzObject(EzFormat, EzAttr):

    pass



def normalize_abilities(jso):
    if isinstance(jso, list):
        assert len(jso) == 6
        res = dict(zip(game.ABILITIES, ( int(a) for a in jso )))
    else:
        res = { a: int(jso[fuzzy_match(a, jso)]) for a in game.ABILITIES }
    return EzObject(**res)
        


def normalize_player(jso, name):
    return EzObject(
        name        = name,
        race        = fuzzy_match(jso.pop("race"), game.RACES),
        class_      = fuzzy_match(jso.pop("class"), game.CLASSES),
        abilities   = normalize_abilities(jso.pop("abilities")),
        level       = int(jso.pop("level", 0)),
        xp          = int(jso.pop("xp", 0)),
        **jso,
    )


def load_player_file(path):
    with open(path) as file:
        jso = yaml.load(file)
    return EzObject(**{ n: normalize_player(p, n) for n, p in jso.items() })


