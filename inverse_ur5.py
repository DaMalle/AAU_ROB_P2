import numpy as np
from numpy.linalg import inv
import math


def T_mdh(alpha: float, a: float, d: float, theta: float) -> np.ndarray:
    """Returns transformation matrix for modified denavit-hartenberg"""
    s = math.sin
    c = math.cos
    return np.array([
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
    d1 = 89.159
    d2 = 0
    d3 = 0
    d4 = 109.15
    d5 = 94.65
    d6 = 82.3

    alpha1 = 0
    alpha2 = math.pi / 2
    alpha3 = 0
    alpha4 = 0
    alpha5 = math.pi / 2
    alpha6 = -math.pi / 2

    a1 = 0
    a2 = 0
    a3 = -425
    a4 = -392.25
    a5 = 0
    a6 = 0

    theta1 = -math.pi / 4
    theta2 = -math.pi / 4
    theta3 = degrees_to_radiants(22)
    theta4 = degrees_to_radiants(22)
    theta5 = degrees_to_radiants(26)
    theta6 = degrees_to_radiants(26)

    T_01 = T_mdh(alpha1, a1, d1, theta1)
    T_12 = T_mdh(alpha2, a2, d2, theta2)
    T_23 = T_mdh(alpha3, a3, d3, theta3)
    T_34 = T_mdh(alpha4, a4, d4, theta4)
    T_45 = T_mdh(alpha5, a5, d5, theta5)
    T_56 = T_mdh(alpha6, a6, d6, theta6)

    T_06 = T_01 @ T_12 @ T_23 @ T_34 @ T_45 @ T_56
    np.set_printoptions(precision=3, suppress=True)
    print(f"\nforward kinematic model:\n{T_06}\n")

    P_06 = np.array([
        [T_06[0][3]],
        [T_06[1][3]],
        [T_06[2][3]]
    ])
    P_05 = T_06 @ np.array([0, 0, -d6, 1])

    P5_y = P_05[1]
    P5_x = P_05[0]
    phi1 = math.atan2(P5_y, P5_x)
    phi2 = np.arccos(d4 / math.sqrt(P5_x**2 + P5_y**2))
    theta1 = phi1 + phi2 + math.pi / 2
    print(f"phi1 is: {phi1}, phi2 is: {phi2}")
    #theta1 = phi1 - phi2 + math.pi / 2
    print(f"Theta 1 is: {radiants_to_degrees(theta1):.3f}\n")
    theta5 = np.arccos(
        (P_06[0][0] * math.sin(theta1) - P_06[1][0] * math.cos(theta1)
            - d4) / d6
    )
    # theta5 = -np.arccos((P_06[0][0] * math.sin(theta1) - P_06[1][0] * math.cos(theta1)- d4) / d6)
    print(f"Theta 5 is: {radiants_to_degrees(theta5):.3f}\n")

    T_60 = inv(T_06)
    theta6 = math.atan2((-T_60[1][0] * math.sin(theta1) + T_60[1][1] * math.cos(theta1)) / math.sin(theta5), (T_60[0][0] * math.sin(theta1)-T_60[0][1] * math.cos(theta1)) / math.sin(theta5))
    print(f"Theta 6 is: {radiants_to_degrees(theta6):.3f}\n")

    # T_14 = T_12 @ T_23 @ T_34
    T_01 = T_mdh(alpha1, a1, d1, theta1)
    T_45 = T_mdh(alpha5, a5, d5, theta5)
    T_56 = T_mdh(alpha6, a6, d6, theta6)
    T_14 = inv(T_01) @ T_06 @ inv(T_56) @ inv(T_45)

    P_14_x = T_14[0][3]
    P_14_z = T_14[2][3]
    theta3 = math.acos((P_14_x**2 + P_14_z**2 - a3**2 - a4**2) / (2 * a3 * a4))
    # theta3 = -np.arccos((P_14_x**2 + P_14_z**2 - a3**2 - a4**2) / (2 * a3 * a4))
    print(f"Theta 3 is : {radiants_to_degrees(theta3):.3f}\n")

    theta2 = math.atan2(-P_14_z, -P_14_x) - math.asin((-a4 * math.sin(theta3) / math.sqrt(P_14_x**2 + P_14_z**2)))
    print(f"Theta 2 is: {radiants_to_degrees(theta2):.3f}\n")

    T_12 = T_mdh(alpha2, a2, d2, theta2)
    T_23 = T_mdh(alpha3, a3, d3, theta3)
    T_34 = inv(T_12 @ T_23) @ T_14
    theta4 = math.atan2(T_34[1][0], T_34[0][0])
    print(f"Theta 4 is : {radiants_to_degrees(theta4):.3f}\n")

    T_01 = T_mdh(alpha1, a1, d1, theta1)
    T_12 = T_mdh(alpha2, a2, d2, theta2)
    T_23 = T_mdh(alpha3, a3, d3, theta3)
    T_34 = T_mdh(alpha4, a4, d4, theta4)
    T_45 = T_mdh(alpha5, a5, d5, theta5)
    T_56 = T_mdh(alpha6, a6, d6, theta6)

    T_06 = T_01 @ T_12 @ T_23 @ T_34 @ T_45 @ T_56
    print(f"\nforward kinematic model:\n{T_06}\n")
