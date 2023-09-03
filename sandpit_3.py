from infi.devicemanager import DeviceManager
import serial.tools.list_ports
import time
serial_1 = serial.Serial()
from pos import *
# pip install infi.devicemanager
import re

def main():
    device_manager = DeviceManager()
    device_manager.root.rescan()
    pattern = r"USB Serial Port \(COM(\d)\)"

    for device in device_manager.all_devices:
        print(device)

def get_port():
    ports_list = serial.tools.list_ports.comports()

    ports = []
    for port in ports_list:
        print(port)
        ports.append(str(port))

# if __name__ == "__main__":
#     import sys
#     sys.exit(main())

get_port()