ABILITIES = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)

RACES = {
    "elf",
    "half-elf",
    "human",
    "tiefling",
}

CLASSES = {
    "barbarian",
    "cleric",
    "druid",
    "monk",
    "ranger",
    "wizard",
}

LEVELS = [
    None,
    (2,      0),
    (2,    300),
    (2,    900),
    (2,   2700),
    (3,   6500),
    (3,  14000),
    (3,  23000),
    (3,  34000),
    (4,  48000),
    (4,  64000),
    (4,  85000),
    (4, 100000),
    (5, 120000),
    (5, 140000),
    (5, 165000),
    (5, 195000),
    (6, 225000),
    (6, 265000),
    (6, 305000),
    (6, 355000),
]


# Basic Rules p. 113.
XP_BY_CHALLENGE = {
    0       :     10,
    0.125   :     25,
    0.25    :     50,
    0.5     :    100,
    1       :    200,
    2       :    450,
    3       :    700,
    4       :   1100,
    5       :   1800,
    # ...
}
