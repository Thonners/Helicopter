""" Class for the 'controller' that will connect to the Heli server and issue commands """
from threading import Thread
from inputs import get_key, devices
from time import sleep
from gamepad import GamePad
from connection_manager import ControllerConnection
import errno

class HelicopterController:

    def __init__(self, config_file = './heli_server_config.json'):
        # Get the gamepad instance. Will return None if not found. (Will currently raise an exception if not possible as this is the only supported control mechanism)
        self.gp = self._get_gamepad()
        # Connect to the server
        with ControllerConnection(config_file) as self.heli_connection:
            # Create a background thread to run the controller listener on
            self.run_thread = True
            self.input_thread = Thread(target=self.get_input_demands, daemon=True)
            self.input_thread.start()
            while self.run_thread:
                pass

    def _get_gamepad(self):
        """ Returns a GamePad instance if possible, otherwise will return None """
        try:
            # Asign it a real object if possible
            return GamePad()
        except IOError as e:
            print(f'Error: {e}')
            print('Gamepad currently the only supported input mechanism')
            raise e

    def get_input_demands(self):
        print("Helicopter controller thread started. Press 'start' on the controller to initialise the connection to the Helicopter server.")
        while self.run_thread:
            # Check if a gamepad is present
            if self.gp:
                try:
                    demands = self.gp.get_demands()
                    # print(demands)
                    if demands:
                        if self.heli_connection.is_connected:
                            if self.heli_connection.pilot_awake:
                                self.heli_connection.send_input_demands(demands)
                            else:
                                if self.heli_connection.set_battery_connected():
                                    print("")
                                    print("\tTo spin up the motor, hold both the left and right upper triggers together")
                                    print("")
                                    print("\tPress Xbox button at any time to stop the motor")
                                else:
                                    print("Some error occured during the waking up of the pilot :( Please ensure battery connected and press A again to retry")
                                    self.gp.battery_connected = False
                        elif demands['init_connection_demand']:
                            print("\tHelicopterServer connection requested")
                            # Connect to the server
                            connection_successful = self.heli_connection.init_connection()
                            if connection_successful:
                                print("")
                                print("\tConnection successful. Please connect the helicopter battery pack then press A.")
                        else:
                            print("Press start to initialise the connection to the Helicopter server.")
                except OSError as e:
                    # Handle connection errors gracefully
                    if isinstance(e.args, tuple):
                        error_no = e.args[0]
                        if error_no == errno.EHOSTUNREACH:
                            # No route to host
                            print("Unable to connect to the helicopter server. Please press START again to retry connecting when the heli server is available.")
                        elif error_no == errno.EPIPE:
                            # Broken pipe
                            print("Connection to heli lost.")
                            # Try to reconnect?
                            print("Trying to reconnect! (TODO: Implement this!)")
                        elif error_no == errno.ECONNRESET:
                            # Connection reset by peer
                            print("Connection reset by peer - heli server has shutdown!")
                        else:
                            print(f"OSError received: {e.args}")
                            # Abort as I'm not sure what's going on
                            raise e
                    else:
                        print(f"socket error {e.args}")
                except Exception as e:
                    print("Had some exception. Aborting the controller")
                    print(e)
                    # TODO: Handle the loss of the gamepad?
                    self.run_thread = False
                    break
            else:
                # # Check the keyboard regardless (so we can listen for reset / quit requests)
                # events = get_key()
                # if events:
                #     for event in events:
                #         print(event.code)
                print("Error: Gamepad required.")
                self.run_thread = False

    def exit_thread(self):
        self.run_thread = False
