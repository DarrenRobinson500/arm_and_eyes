import serial.tools.list_ports
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
            print(command, m0, m1, m2)
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

# get_port()
# wait_for_homing()

# Prescribed movements
# for x in range(400, 600, 50):
#     for y in range(-100, 100, 50):
#         result = get_angles(x, y, 30)
#         print(result_to_text(result))
#         command(result_to_text(result))
        # time.sleep(.25)

# Free range movements
# finished = False
# while not finished:
#     text = input("m1 m2 m3: ")
#     if text == "":
#         finished = True
#     else:
#         angles = text.split(" ")
#         text = "p " + text
#         get_pos(float(angles[0]), float(angles[1]), float(angles[2]))
#         # print(text)
#         command(text)



# command("p 1200 200 200")
# for m0 in range(0, 2501, 500):
#     for m1 in range(0, 601, 200):
#         for m2 in range(m1, 801, 200):
#             text = f"p {m0} {m1} {m2}"
#
#             print(text)
#             command(text)
#
# print("Finished")

serial_1.close()

# Position, angles, position: [440, 0, 40] => [1500.0, 237.7, 986.5] => [440.0, -0.0, 40.0]
# Position, angles, position: [440, -20, 40] => [1471.0, 238.7, 986.0] => [440.0, -20.1, 40.0]
# Position, angles, position: [440, -40, 40] => [1442.3, 241.8, 984.6] => [440.0, -40.0, 40.0]
# Position, angles, position: [440, -60, 40] => [1413.2, 244.2, 988.6] => [437.4, -60.0, 38.6]
# Position, angles, position: [440, -80, 40] => [1452.4, 240.3, 985.3] => [439.9, -33.0, 40.0]
# Position, angles, position: [440, -100, 40] => [1357.7, 262.9, 974.4] => [440.0, -100.0, 40.2]
# Position, angles, position: [440, -120, 40] => [1330.5, 274.2, 969.4] => [440.0, -120.0, 40.0]
# Position, angles, position: [440, -140, 40] => [1303.9, 287.0, 963.0] => [440.0, -140.0, 40.0]
# Position, angles, position: [440, -160, 40] => [1280.2, 298.5, 954.0] => [440.0, -158.3, 40.9]
# Position, angles, position: [440, -180, 40] => [1252.8, 318.1, 946.6] => [440.0, -180.0, 40.0]

