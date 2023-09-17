import serial.tools.list_ports
from math import sin, cos, radians, atan, pi, acos, sqrt

base_h = 100
base_v = 100
end_h = 80
end_v = -90
l1 = 50
l2 = 218
l3 = 250


serial_1 = serial.Serial()

def get_port():
    ports_list = serial.tools.list_ports.comports()

    port = str(ports_list[0])[0:4]

    serial_1.baudrate = 9600
    serial_1.port = port
    serial_1.timeout = 5
    serial_1.open()

    # print("Selected port:", port[0:4])

def wait_for_homing():
    homed = False
    homing_string = "homing complete"
    i = 0
    while not homed:
        result = str(serial_1.readline(), 'UTF-8')
        # print(f"Reading from the serial port {i}:", result, result.find(homing_string))
        # print(type(result))

        if result.find(homing_string) >= 0:
            print("Homed")
            homed = True
        # else:
            # print("Not homed")

        i += 1

def wait_for_serial(text):
    complete = False
    i = 0
    while not complete:
        result = str(serial_1.readline(), 'UTF-8').strip()
        # print(f"Reading from the serial port {i}:", result)

        if result.find(text) >= 0:
            # print("Complete")
            complete = True
        # else:
        #     print("Not complete")

        i += 1

def read_serial():
    i = 0
    while i < 40:
        result = str(serial_1.readline(), 'UTF-8').strip()
        print(f"Reading from the serial port {i}:", result)
        i += 1

def command(text):
    reason = ""
    text_elements = text.split()
    if text_elements[0] == "p":
        if len(text_elements) != 4:
            reason = "Starts with p but doesn't have 4 elements"
        else:
            command, m0, m1, m2 = text_elements
            print("Command to arduino:", command, m0, m1, m2)
            m0, m1, m2 = int(m0), int(m1), int(m2)
            if m1 > 800:
                reason = f"M1 being asked to move beyond 800 ({m1})"
            if m1 + m2 > 1450:
                reason = f"M1 + M2 being asked to move beyond 1450 ({m2})"
    if reason == "":
        text = text + " "
        serial_1.write(text.encode('utf-8'))
        wait_for_serial("complete")
    else:
        print("Requested command:", text)
        print("Not sending command:", reason)

def get_angles(x, y, z):
    z = z - base_v - end_v
    angle_1 = atan(y/x)
    angle_1_degrees = angle_1 * 360 / (2 * pi)
    angle_1_pulses = int(angle_1_degrees * 1000 / 90 + 1500)

    reach_v = z
    reach_h_inc_adj = sqrt(x * x + y * y)
    reach_h = reach_h_inc_adj - (base_h + end_h)
    reach_2 = reach_v * reach_v + reach_h * reach_h
    reach = sqrt(reach_2)

    reach_angle = atan(reach_v / reach_h)

    beta = acos((l2 * l2 + reach_2 - l3 * l3) / (2 * l2 * reach))
    angle_2 = pi / 2 - beta - reach_angle
    angle_2_degrees = angle_2 * 360 / (2 * pi)
    angle_2_pulses = int(angle_2_degrees * 1000 / 90)

    angle_c = cosine_angle(reach, l2, l3)
    angle_3_degrees = 360 - angle_c - (180 - angle_2_degrees)
    angle_3_pulses = int(angle_3_degrees * 1000 / 90 - 500)
    return angle_1_pulses, angle_2_pulses, angle_3_pulses

def cosine_angle(a, b, c):
    return acos((b * b + c * c - a * a) / (2 * b * c)) * 360 / (2 * pi)

def result_to_text(result):
    return "p " + str(round(result[0],0)) + " " + str(round(result[1],0)) + " " + str(round(result[2],0))
