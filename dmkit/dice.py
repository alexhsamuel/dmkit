import re
from   random import randint

#-------------------------------------------------------------------------------

class Roll:

    def __init__(self, max, num=1, inc=0):
        assert (max == 0 and num == 0) or (max > 0 and num >= 0)
        self.__max = max
        self.__num = num
        self.__inc = inc


    def __repr__(self):
        return f"{self.__class__.__name__}({self.__max}, {self.__num}, {self.__inc})"


    def __eq__(self, other):
        return (
                other.__num == self.__num
            and other.__max == self.__max 
            and other.__inc == self.__inc
            if isinstance(other, Roll)
            else NotImplemented
        )


    def __str__(self):
        if self.__num == 0:
            return "0"
        s = "d" + str(self.__max)
        if self.__num > 1:
            s = str(self.__num) + s
        if self.__inc != 0:
            s += format(self.__inc, "+d")
        return s


    def __call__(self):
        return sum( randint(1, self.__max) for _ in range(self.__num) ) + self.__inc

    
    def __rmul__(self, num):
        return type(self)(self.__max, self.__num * num, self.__inc)


    def __add__(self, inc):
        return type(self)(self.__max, self.__num, self.__inc + inc)



roll = lambda *a, **k: Roll(*a, **k)()

d4  = Roll( 4)
d6  = Roll( 6)
d8  = Roll( 8)
d10 = Roll(10)
d12 = Roll(12)
d20 = Roll(20)

def rep(n, fn):
    return [ fn() for _ in range(n) ]


_REGEX = re.compile(r"(\d*)d(\d+)([+-]\d+)?$")

def parse(string):
    """

      >>> parse("17")
      Roll(0, 0, 17)
      >>> parse("2d6")
      Roll(6, 2, 0)
      >>> parse("d8+4")
      Roll(8, 1, 4)
      >>> parse("4d4-4")
      Roll(4, 4, -4)

    """
    try:
        inc = int(string)
    except ValueError:
        pass
    else:
        # Fixed value.
        return Roll(0, 0, inc)

    match = _REGEX.match(string)
    if match is None:
        raise ValueError(f"can't parse dice roll: {string}")

    num, max, inc = match.groups()
    return Roll(
        int(max),
        1 if num == "" else int(num),
        0 if inc is None else int(inc),
    )


