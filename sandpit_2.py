import serial.tools.list_ports
import socket
from camera import *

Camera(0)


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_open_ports():
    for port in range(1, 8081):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            res = sock.connect_ex(('localhost', port))
            if res == 0:
                yield port


# ports_list = serial.tools.list_ports.comports()
for port in range(3):
    result = is_port_in_use(port)
    print(result)


