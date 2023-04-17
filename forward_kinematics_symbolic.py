import numpy as np
from numpy.linalg import inv
import math
import sympy as sp


def T_mdh(alpha, a, d, theta):
    """Returns transformation matrix for modified denavit-hartenberg"""
    s = sp.sin
    c = sp.cos
    return sp.Matrix([
        [c(theta), -s(theta), 0, a],
        [s(theta) * c(alpha), c(theta) * c(alpha), -s(alpha), -s(alpha) * d],
        [s(theta) * s(alpha), c(theta) * s(alpha), c(alpha), c(alpha) * d],
        [0, 0, 0, 1]
    ])


def degrees_to_radiants(degrees: float) -> float:
    """Converts degrees to radiants"""
    return degrees * math.pi / 180


def radiants_to_degrees(radiants: float) -> float:
    """Converts degrees to radiants"""
    return radiants * 180 / math.pi


if __name__ == "__main__":
    d1, d2, d3, d4, d5, d6 = sp.symbols("d1, d2, d3, d4, d5, d6")
    af1, af2, af3, af4, af5, af6 = sp.symbols("af1, af2, af3, af4, af5, af6")
    a1, a2, a3, a4, a5, a6 = sp.symbols("a1, a2, a3, a4, a5, a6")
    t1, t2, t3, t4, t5, t6 = sp.symbols("t1, t2, t3, t4, t5, t6")
    T_01 = T_mdh(af1, a1, d1, t1)
    T_12 = T_mdh(af2, a2, d2, t2)
    T_23 = T_mdh(af3, a3, d3, t3)
    T_34 = T_mdh(af4, a4, d4, t4)
    T_45 = T_mdh(af5, a5, d5, t5)
    T_56 = T_mdh(af6, a6, d6, t6)
    sp.pprint(T_01 * T_12 * T_23 * T_34 * T_45 * T_56)
