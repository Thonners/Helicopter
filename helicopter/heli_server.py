""" Class to manage listening for the input to control the helicopter """

import os
import json
import sys
import socket
import socketserver


class HeliServerConnectionHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    connection_active = False

    def handle(self):
        print("handle() called")
        self.connection_active = True
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        while self.connection_active:
            self.data = self.rfile.readline().strip()
            print(f"{self.client_address[0]} wrote:")
            print(self.data)
        # just send back the same data, but upper-cased
        # self.request.sendall(self.data.upper())
    
    def finish(self):
        print("Finish called")
        self.connection_active = False

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
        with HelicopterServer() as server:
            while True:
                pass
    except KeyboardInterrupt:
        print("Server shutting down.")
        # server.__exit__()
