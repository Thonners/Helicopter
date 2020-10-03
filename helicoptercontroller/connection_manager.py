""" Class to manage the connection to the helicopter server """
import json
import socket

class ControllerConnection:

    def __init__(self, config_file):
        # Read the config file
        with open(config_file,'r') as file:
            self.conf = json.load(file)
        # Check there's an IP address
        if 'server_ip' not in self.conf or 'server_port' not in self.conf:
            raise ValueError("Error: 'server_ip' & 'server_port required in the config file")

        print(self.conf)
        self.is_connected = False
        self.pilot_awake = False

    def __enter__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s.connect((self.conf['server_ip'], self.conf['server_port']))
        # Force NODELAY to stop the client waiting for a minmum amount of data before sending it
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Closing controller connection")
        if self.s:
            self.s.close()

    def init_connection(self):
        self.s.connect((self.conf['server_ip'], self.conf['server_port']))
        self.test_connection()
        connection_confirmation = self.s.recv(1)
        if connection_confirmation == bytes([1]):
            print("Helicopter Server connection established.")
            self.is_connected = True
        return self.is_connected

    def test_connection(self):
        self._send_data(bytes([1]))

    def set_battery_connected(self):
        self._send_data(bytes([2]))
        pilot_started_confirmation = self.s.recv(1)
        if pilot_started_confirmation == bytes([2]):
            print("Helicopter Pilot woken up and ready to fly :)")
            self.pilot_awake = True
        return self.pilot_awake

    def send_input_demands(self,demands):
        # Convert to json so it can be encoded as a string
        demands_data = json.dumps(demands)
        self._send_data(demands_data)

    def _send_data(self, data, response_expected=False):
        if type(data) == str:
            data += '\n'
            data = data.encode('utf-8')
        # print(f"Sending data: {data}")
        self.s.send(data)
        if response_expected:
            # TODO: Deal with reading the reply...
            pass