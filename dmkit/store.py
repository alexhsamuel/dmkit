import yaml

from   . import game
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
        self.xp = xp


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


