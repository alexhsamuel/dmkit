from random import randint

class Roll:

    def __init__(self, max, num=1, inc=0):
        assert max > 0 and num >= 0
        self.__max = max
        self.__num = num
        self.__inc = inc


    def __repr__(self):
        return f"{self.__class__.__name__}({self.__max}, {self.__num}, {self.__inc})"


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


