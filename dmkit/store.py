from   contextlib import suppress
import yaml

from   . import game
from   .dice import d20
from   .ez import EzObject, EzAttr, EzList, fuzzy_match

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
        
        

class Creature(EzObject):

    def __init__(self, abilities):
        self.abilities  = abilities


    strength        = property(lambda self: self.abilities.strength)
    dexterity       = property(lambda self: self.abilities.dexterity)
    constitution    = property(lambda self: self.abilities.constitution)
    intelligence    = property(lambda self: self.abilities.intelligence)
    wisdom          = property(lambda self: self.abilities.wisdom)
    charisma        = property(lambda self: self.abilities.charisma)


    @classmethod
    def from_jso(cls, jso):
        return cls(
            abilities   = Abilities.from_jso(jso["abilities"]),
        )



class Character(Creature):

    def __init__(self, name, race, class_, abilities, level, xp):
        super().__init__(abilities)
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


