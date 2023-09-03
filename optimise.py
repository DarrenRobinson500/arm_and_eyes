from math import sin, cos, radians, atan, pi, acos, sqrt, asin
import numpy as np
from scipy.optimize import minimize

base_h = 100
base_v = 100
end_h = 80
end_v = -90

base_h = 0
# base_v = 0
end_h = 0
# end_v = 0


l1 = 50
l2 = 218
l3 = 250

def get_pos(angle_1_raw, angle_2_raw, angle_3_raw):
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

    return x, y, z

def get_angles(x, y, z):
    z = z - base_v - end_v
    angle_1 = atan(y/x)
    angle_1_degrees = angle_1 * 360 / (2 * pi)
    angle_1_pulses = angle_1_degrees * 1000 / 90 + 1500
    # print("Angle 1")
    # print("Radians:", round(angle_1, 2))
    # print("Degrees:", round(angle_1_degrees, 1))
    print("Angle 1 Pulses:", round(angle_1_pulses, 0))

    reach_2 = x * x + y * y + z * z
    reach = sqrt(reach_2)
    reach_v = z
    reach_h = sqrt(x * x + y * y)
    reach_angle = atan(reach_v / reach_h)
    beta = acos((l2 * l2 + reach_2 - l3 * l3) / (2 * l2 * reach))
    angle_2 = pi / 2 - beta - reach_angle
    angle_2_degrees = angle_2 * 360 / (2 * pi)
    angle_2_pulses = angle_2_degrees * 1000 / 90
    # print("Angle 2")
    # print("Radians:", round(angle_2, 2))
    # print("Degrees:", round(angle_2_degrees, 1))
    print("Angle 2 Pulses:", round(angle_2_pulses, 0))

    angle_c = asin(sin(beta) / l3 * reach) * 360 / (2 * pi)
    # print("Reach:", reach)
    # print("Beta (degrees):", beta * 360 / (2 * pi))
    # print("Angle C (degrees):", 360, angle_c)

    angle_3_degrees = 360 - angle_c - (180 - angle_2_degrees)
    # angle_3_degrees = angle_3 * 360 / (2 * pi)
    angle_3_pulses = angle_3_degrees * 1000 / 90 - 500
    # print("Angle 3")
    # print("Radians:", round(angle_3, 2))
    # print("Degrees:", round(angle_3_degrees, 1))
    print("Angle 3 Pulses:", round(angle_3_pulses, 0))


# print("Atan 0", atan(0))
get_pos(1500, 244, 989)
get_angles(261, 0, 38)



current_angles = [1200, 0, 0]
target = [50, 0, 35]
target = np.array(target)

def error(angles):
    angle_1, angle_2, angle_3 = angles
    guess = get_pos(angle_1, angle_2, angle_3)
    # error = pow((target[0] - guess[0]), 2) + pow((target[1] - guess[1]), 2) + pow((target[2] - guess[2]), 2)

    error = abs(target[0] - guess[0]) + abs(target[1] - guess[1]) + abs(target[2] - guess[2])
    # print("Error function:", guess, error)

    return error

def array_round(values, dp):
    rounded_values = []
    for x in values:
        rounded_values.append(round(x, dp))
    return rounded_values



def get_angles_opti(x, y, z):
    global target
    target = [x, y, z]
    angles = minimize(error, np.array(current_angles), method='SLSQP').x
    a0, a1, a2 = angles
    # print("Position, angles, position:", target, "=>", array_round(angles, 1), "=>", array_round(get_pos(a0, a1, a2), 1))
    resulting_error = round(error(angles),0)
    if resulting_error > 5:
        print("Resulting error:", round(error(angles),0))
    return angles

# get_pos(1500, 0, 0)
# get_pos(1500, 0, 500)
# get_pos(1500, 0, 1000)
# get_pos(500, 0, 0)
# get_pos(500, 0, 500)
# get_pos(500, 0, 1000)

# for x in range(400, 500, 20):
#     get_angles(x, 0, 40)

# for y in range(0, -160, -20):
#     result = get_angles(440, y, 10)
#     print(result_to_text(result))

