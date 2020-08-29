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

    def __enter__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.conf['server_ip'], self.conf['server_port']))
        # Force NODELAY to stop the client waiting for a minmum amount of data before sending it
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        print("Exit called")
        self.s.close()

    def test_connection(self, test_message="Test"):
        self._send_data(test_message)

    def send_input_demands(self,demands):
        # Convert to json so it can be encoded as a string
        demands_data = json.dumps(demands)
        self._send_data(demands_data)

    def _send_data(self, data):
        if type(data) == str:
            data += '\n'
            data = data.encode('utf-8')
        print(f"Sending data: {data}")
        self.s.send(data)