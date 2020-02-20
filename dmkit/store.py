from   contextlib import suppress
import yaml

from   . import game
from   .dice import d20
from   .ez import EzObject, EzAttr, EzList, fuzzy_match, fuzzy_get
from   .lib import if_none

#-------------------------------------------------------------------------------

class Check(EzAttr):

    def __init__(self, modifier):
        self.modifier = modifier


    def __call__(self):
        return d20() + self.modifier


    def __truediv__(self, dc):
        mod = self.modifier
        roll = d20()
        i = input(f"check ({mod:+d}) DC {dc} [roll {roll}] ").strip()
        if i != "":
            roll = int(roll)
            assert 1 <= roll <= 20
        return roll + mod >= dc



class Ability(EzAttr):

    def __init__(self, val):
        self.val = int(val)
        self.check = Check(self.modifier)


    def __repr__(self):
        return f"{self.val:2d} ({self.modifier:+d})"
    

    @property
    def modifier(self):
        return self.val // 2 - 5




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
        
        

class HitPoints(EzObject):

    def __init__(self, max, current=None, temporary_max=None):
        self.max = int(max)
        self.current = int(if_none(current, self.max))
        self.temporary_max = int(if_none(temporary_max, self.max))


    @classmethod
    def from_jso(cls, jso):
        if isinstance(jso, int):
            return cls(jso)

        max = fuzzy_get(jso, "max")
        current = fuzzy_get(jso, "current", None)
        temporary_max = fuzzy_get(jso, "temporary_max", None)
        return cls(max, current, temporary_max)



class Creature(EzObject):

    def __init__(self, abilities, hit_points):
        self.abilities  = abilities
        self.hit_points = hit_points


    strength        = property(lambda self: self.abilities.strength)
    dexterity       = property(lambda self: self.abilities.dexterity)
    constitution    = property(lambda self: self.abilities.constitution)
    intelligence    = property(lambda self: self.abilities.intelligence)
    wisdom          = property(lambda self: self.abilities.wisdom)
    charisma        = property(lambda self: self.abilities.charisma)

    hp              = property(lambda self: self.hit_points)


    @classmethod
    def from_jso(cls, jso):
        return cls(
            abilities   = Abilities.from_jso(jso["abilities"]),
            hit_points  = HitPoints.from_jso(jso.get("hit points")),
        )



class Character(Creature):

    def __init__(self, name, race, class_, abilities, hit_points, level, xp):
        super().__init__(abilities, hit_points)
        self.name       = name
        self.race       = race
        self.abilities  = abilities
        self.level      = level
        self.xp         = xp


    @classmethod
    def from_jso(cls, jso):
        self = Creature.from_jso(jso)
        self.__dict__.update(
            name        = jso["name"],
            race        = fuzzy_match(jso["race"], game.RACES),
            class_      = fuzzy_match(jso["class"], game.CLASSES),
            level       = int(jso.get("level", 0)),
            xp          = int(jso.get("xp", 0)),
        )
        return self


def load_party(path):
    with open(path) as file:
        jso = yaml.load(file)
    return EzList( Character.from_jso(o) for o in jso )


#-------------------------------------------------------------------------------

def _to_name(obj):
    if isinstance(obj, str):
        return obj
    with suppress(AttributeError):
        return obj.name
    with suppress(AttributeError):
        return obj.__name__
    return str(obj)


