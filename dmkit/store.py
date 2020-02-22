from   pathlib import Path
import yaml

from   . import dice, ez, game
from   .lib import if_none

#-------------------------------------------------------------------------------

class Check(ez.Attr):

    def __init__(self, modifier):
        self.modifier = modifier


    def __call__(self):
        return dice.d20() + self.modifier


    def __truediv__(self, dc):
        mod = self.modifier
        roll = dice.d20()
        i = input(f"check ({mod:+d}) DC {dc} [roll {roll}] ").strip()
        if i != "":
            roll = int(roll)
            assert 1 <= roll <= 20
        return roll + mod >= dc



class Ability(ez.Attr):

    def __init__(self, val):
        self.val = int(val)
        self.check = Check(self.modifier)


    def __repr__(self):
        return f"{self.val:2d} ({self.modifier:+d})"
    

    @property
    def modifier(self):
        return self.val // 2 - 5




class Abilities(ez.Object):

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
            scores = [ int(jso[ez.match(a, jso)]) for a in cls._names ]
        return cls(*scores)
        
        

class HitPoints(ez.Object):

    def __init__(self, max, current=None, temporary_max=None):
        self.max = int(max)
        self.current = int(if_none(current, self.max))
        self.temporary_max = int(if_none(temporary_max, self.max))


    @classmethod
    def from_jso(cls, jso):
        if isinstance(jso, int):
            return cls(jso)

        max = ez.get(jso, "max")
        current = ez.get(jso, "current", None)
        temporary_max = ez.get(jso, "temporary_max", None)
        return cls(max, current, temporary_max)



class Creature(ez.Object):

    # FIXME: Don't need.
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

    # FIXME: Dont' need?
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
        self.name       = jso["name"]
        self.race       = ez.match(jso["race"], game.RACES)
        self.class_     = ez.match(jso["class"], game.CLASSES)
        self.level      = int(jso.get("level", 0))
        self.xp         = int(jso.get("xp", 0))
        return self



class Monster(ez.Object):
    """
    A template for a monster.
    """

    @classmethod
    def from_jso(cls, jso):
        # FIXME: Others.
        self = cls()
        self.name       = jso["name"]
        # size
        # shape
        # alignment
        self.hit_dice   = dice.parse(jso["hp"])
        # speed
        self.abilities  = Abilities.from_jso(jso["abilities"])
        # skills
        # senses
        # languages
        self.challenge  = jso["challenge"]
        # features
        # actions
        return self


    @property
    def xp(self):
        return game.XP_BY_CHALLENGE[self.challenge]



#-------------------------------------------------------------------------------

class Initiative(ez.Object):

    pass



class Combat(ez.List):

    pass



#-------------------------------------------------------------------------------

def load_yaml_file(path):
    with open(path, "rt") as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def load_party(path):
    return ez.List( Character.from_jso(o) for o in load_yaml_file(path) )


def load_monsters(path):
    """
    Loads all monsters from files in `path`.
    """
    return ez.List(
        Monster.from_jso(o)
        for p in Path(path).iterdir()
        if p.suffix == ".yaml"
        for jso in (load_yaml_file(p), )
        for o in jso
    )
            

