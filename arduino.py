import serial.tools.list_ports

ports_list = serial.tools.list_ports.comports()
serialInst = serial.Serial()

ports = []

for port in ports_list:
    ports.append(str(port))

print(ports)

val = input("Select Port: COM")

for x in range(0, len(ports)):
    if ports[x].startswith("COM" + str(val)):
        port = "COM" + str(val)
        print("Port '" + port + "'")

serialInst.baudrate = 9600
serialInst.port = port
serialInst.open()

running = True
while running:
    command = input("Arduino Command: (ON/OFF):")
    serialInst.write(command.encode('utf-8'))
    if command == "exit": running = False

serialInst.close()

