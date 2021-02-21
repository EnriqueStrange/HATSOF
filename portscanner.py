import socket
from IPy import IP


class PortScan():
    banners = []
    open_ports = []
    def __init__(self, target, port_num):
        self.target = target
        self.port_num = port_num

    def scan(self):
        for port in range(1,500):
            self.scan_port(port)


    def check_ip(self):
        try:
            IP(self.target)
            return(self.target)