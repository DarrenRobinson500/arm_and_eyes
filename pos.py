from math import sin, cos, radians, atan, pi, acos, sqrt, asin
import numpy as np
from scipy.optimize import minimize

base_h = 100
base_v = 100
end_h = 80
end_v = -90

# base_h = 0
# base_v = 0
# end_h = 0
# end_v = 0


l1 = 50
l2 = 218
l3 = 250

def get_pos(angle_1_raw, angle_2_raw, angle_3_raw, integer_results = False):
    angle_1_deg = (angle_1_raw - 1500) / (1000/90)  # 1000 pulses = 90 degrees
    angle_1 = radians(angle_1_deg)

    angle_2_deg = angle_2_raw / (1000/90)
    angle_2 = radians(angle_2_deg)

    angle_3_deg = (angle_3_raw + 500) / (1000/90)
    angle_3 = radians(angle_3_deg)

    reach_h = base_h + l2 * sin(angle_2) + l3 * sin(angle_3) + end_h
    reach_v = base_v + l2 * cos(angle_2) + l3 * cos(angle_3) + end_v
    # print("reach_v", base_v, l2 * cos(angle_2), l3 * cos(angle_3), end_v)

    x = reach_h * cos(angle_1)
    y = reach_h * sin(angle_1)
    z = reach_v
    # print(angle_1_raw, angle_2_raw, angle_3_raw, "=>", angle_1_deg, angle_2_deg, angle_3_deg, "=>", round(x,0), round(y,0), round(z,0))

    if integer_results:
        x, y, z = int(x), int(y), int(z)

    return x, y, z

def get_angles(x, y, z):
    z = z - base_v - end_v
    angle_1 = atan(y/x)
    angle_1_degrees = angle_1 * 360 / (2 * pi)
    angle_1_pulses = int(angle_1_degrees * 1000 / 90 + 1500)
    # print("Angle 1")
    # print("Radians:", round(angle_1, 2))
    # print("Degrees:", round(angle_1_degrees, 1))
    # print("Angle 1 Pulses:", round(angle_1_pulses, 0))

    reach_v = z
    # reach_h =
    reach_h_inc_adj = sqrt(x * x + y * y)
    # print("x, y, Reach_h_inc_adj:", x, y, reach_h_inc_adj)
    reach_h = reach_h_inc_adj - (base_h + end_h)
    reach_2 = reach_v * reach_v + reach_h * reach_h
    reach = sqrt(reach_2)
    reach_inc_adj = reach_v * reach_v + reach_h_inc_adj * reach_h_inc_adj

    # print("Reach_h, Reach_v, Reach:", round(reach_h, 1), round(reach_v, 1), round(reach, 1))

    reach_angle = atan(reach_v / reach_h)
    reach_angle_degrees = reach_angle * 360 / (2 * pi)
    # print("Reach angle (degrees):", round(reach_angle_degrees, 1))

    # print()

    beta = acos((l2 * l2 + reach_2 - l3 * l3) / (2 * l2 * reach))
    beta_degrees = cosine_angle(l3, l2, reach)
    # beta_degrees = beta * 360 / (2 * pi)
    # print("Beta Degrees:", round(beta_degrees, 1))
    angle_2 = pi / 2 - beta - reach_angle
    angle_2_degrees = angle_2 * 360 / (2 * pi)
    angle_2_pulses = int(angle_2_degrees * 1000 / 90)
    # print("Angle 2")
    # print("Radians:", round(angle_2, 2))
    # print("Degrees:", round(angle_2_degrees, 1))
    # print("Angle 2 Pulses:", round(angle_2_pulses, 0))

    angle_c = cosine_angle(reach, l2, l3)
    angle_3_degrees = 360 - angle_c - (180 - angle_2_degrees)
    # angle_3_degrees = angle_3 * 360 / (2 * pi)
    angle_3_pulses = int(angle_3_degrees * 1000 / 90 - 500)
    # print("Angle 3")
    # print("Radians:", round(angle_3, 2))
    # print("Degrees:", round(angle_3_degrees, 1))
    # print("Angle 3 Pulses:", round(angle_3_pulses, 0))
    return angle_1_pulses, angle_2_pulses, angle_3_pulses


def result_to_text(result):
    text = "p " + str(round(result[0],0)) + " " + str(round(result[1],0)) + " " + str(round(result[2],0))
    return text

def cosine_angle(a, b, c):
    return acos((b * b + c * c - a * a) / (2 * b * c)) * 360 / (2 * pi)


def distance(x, y):
    return sqrt((x * x) + (y * y))

# print("Cosine test:", cosine_angle(429, 218, 250))


# print("Atan 0", atan(0))
# get_pos(1500, 244, 989)
# get_angles(441, 0, 38)

for x in range(400, 700, 50):
    for y in range(-100, 100, 50):
        pass




# z = 100
# for x in range(400, 600, 50):
#     for y in range(-100, 100, 50):
#         result = get_angles(x, y, 100)
#         pos = get_pos(result[0], result[1], result[2], integer_results=True)
#         print(x, y, z , "=>", result, "=>", pos, ".  Error:", pos[0] - x, pos[1] - y, pos[2] - z)


# x, y, z = 600, 0, 100
# result = get_angles(x, y, 100)
# pos = get_pos(result[0], result[1], result[2], integer_results=True)
# print(x, y, z , "=>", result, "=>", pos, ".  Error:", pos[0] - x, pos[1] - y, pos[2] - z)
