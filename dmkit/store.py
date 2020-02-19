from   contextlib import suppress
import yaml

from   . import game
from   .dice import d20
from   .ez import EzObject, EzAttr, EzList, fuzzy_match

#-------------------------------------------------------------------------------

class Ability(EzAttr):

    def __init__(self, val):
        self.val = int(val)


    def __repr__(self):
        return f"{self.val:2d} ({self.modifier:+d})"
    

    @property
    def modifier(self):
        return self.val // 2 - 5


    def check(self):
        return d20() + self.modifier



class Abilities(EzObject):

    _names = [
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
    ]


    def __init__(self, *scores):
        assert len(scores) == 6
        scores = ( Ability(s) for s in scores )
        self.__dict__.update(zip(self._names, scores))


    @classmethod
    def from_jso(cls, jso):
        if isinstance(jso, list):
            scores = jso
        else:
            scores = [ int(jso[fuzzy_match(a, jso)]) for a in cls._names ]
        return cls(*scores)
        
        

class Player(EzObject):

    def __init__(self, name, race, class_, abilities, level, xp):
        self.name       = name
        self.race       = race
        self.class_     = class_
        self.abilities  = abilities
        self.level      = level
        self.xp         = xp

        # Inject abilities.
        self.__dict__.update(abilities.__dict__)


    @classmethod
    def from_jso(cls, jso):
        return cls(
            name        = jso["name"],
            race        = fuzzy_match(jso["race"], game.RACES),
            class_      = fuzzy_match(jso["class"], game.CLASSES),
            abilities   = Abilities.from_jso(jso["abilities"]),
            level       = int(jso.get("level", 0)),
            xp          = int(jso.get("xp", 0)),
        )



def load_player_file(path):
    with open(path) as file:
        jso = yaml.load(file)
    return EzList( Player.from_jso(o) for o in jso )


#-------------------------------------------------------------------------------

def _to_name(obj):
    if isinstance(obj, str):
        return obj
    with suppress(AttributeError):
        return obj.name
    with suppress(AttributeError):
        return obj.__name__
    return str(obj)


def check_modifier(who, type):
    type = _to_name(type)
    with suppress(AttributeError):
        return getattr(who.abilities, type).modifier
    with suppress(AttributeError):
        return getattr(who.skills, type).modifier
    raise AttributeError(f"no check type: {type}")


# FIXME: Elsewhere.
def check(who, type, dc):
    type = _to_name(type)
    mod = check_modifier(who, type)
    roll = d20() + mod
    succ = roll >= dc
    succ_str = "success" if succ else "failure"
    print(f"{type} check ({mod:+d}) DC {dc}: roll {roll}: {succ_str}")
    return succ



