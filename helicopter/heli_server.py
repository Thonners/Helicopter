""" Class to manage listening for the input to control the helicopter """

import os
import json
import sys
import socket
import socketserver
import errno
from time import sleep
from pilot import HelicopterPilot
from pithonwy.actuators import Motor 	# Keep this so we can force the motor shutdown if the server crashes/is killed

class HeliServerConnectionHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    connection_active = False

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        connection_test_request = self.rfile.read(1)
        if connection_test_request == bytes([1]):
            # Send a 'connection successful' message back
            self.wfile.write(bytes([1]))
            self.connection_active = True
            print("Controller connection established")
        else:
            raise ConnectionError()
        # Wait for word that the battery is connected
        pilot_started = False
        while not pilot_started:
            battery_connection_update = self.rfile.read(1)
            if battery_connection_update == bytes([2]):
                # Then user claims battery is connected, so let's fire up the HeliPilot instance
                try:
                    # If battery connected, then start up the heli instance (need the connection else the power won't be there for the Gyro, etc.)
                    self.pilot = HelicopterPilot()
                    # Send a 'Pilot wakeup successful' message back
                    self.wfile.write(bytes([2]))
                    pilot_started = True
                except OSError as e:
                    # Let the controller know that there was an issue (otherwise it'll block!)
                    self.wfile.write(bytes([0]))
                    # An issue reading one of the sensors?
                    if e.args[0] == errno.EREMOTEIO:
                        # This is seen when the gyro can't start (usually because it doesn't have any power)
                        print("Error starting Gyro. Please ensure main power battery conencted")
                    else:
                        print("Some error received whilst trying to initialise the HeliPilot instance :(")
                except ValueError as e:
                    print("Error starting Gyro. Please ensure main power battery conencted")
                    print(f"Error details: {e.args}")
                    self.wfile.write(bytes([0]))
        while self.connection_active:
            # Read the data (raw bytes)
            raw_data = self.rfile.readline().strip()
            # Decode the data
            data = raw_data.decode('utf-8')
            # print(f"{self.client_address[0]} sent: {data}")
            try:
                demands = json.loads(data)
                self.pilot.update_demands(demands)
            except json.JSONDecodeError as e:
                print("Error decoding the demands. Stopping the helicopter now")
                self.pilot.stop_flying()
                print(e)
    
    def finish(self):
        print("Finish called")
        self.connection_active = False
        # Ensure the motor is not spinining if the connection is lost
        # self.pilot.stop_flying()

class HelicopterServer:

    def __init__(self, host="0.0.0.0", port=4371):
        self.host = host
        self.port = port
        # Use this to determine when to close the server
        self.running = True

    def __enter__(self):
        """ Start listening for connections """
        # Create the server, binding to host/port set in the settings
        print(f"Starting server on host: {self.host}, listening on port: {self.port}...")
        self.server = socketserver.TCPServer((self.host, self.port), HeliServerConnectionHandler)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        self.server.serve_forever()

    def __exit__(self, exc_type, exc_value, traceback):
        """ Called when the 'with' statement ends, so clean up the connection """
        print("Shutting down server...")
        self.running = False
        self.server.shutdown()
        self.server.close()

if __name__ == "__main__":
    try:
        print("Starting helicopter server...")
        while True:
            try:
                with HelicopterServer() as server:
                    print("Server successfully started :)")
                    while True:
                        pass
            except OSError:
                print("Error binding to port, already in use. Trying again in 5 seconds")
                sleep(5)
    except KeyboardInterrupt:
        print("Server shutting down.")
        m = Motor()
        m.arm()
