""" Class for the 'controller' that will connect to the Heli server and issue commands """
from threading import Thread
from inputs import get_key, devices
from time import sleep
from gamepad import GamePad
from connection_manager import ControllerConnection

class HelicopterController:

    def __init__(self, config_file = './heli_server_config.json'):
        # Get the gamepad instance. Will return None if not found. (Will currently raise an exception if not possible as this is the only supported control mechanism)
        self.gp = self._get_gamepad()
        # Connect to the server
        with ControllerConnection(config_file) as self.heli_connection:
            self.heli_connection.test_connection()
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
        while self.run_thread:
            # Check if a gamepad is present
            if self.gp:
                try:
                    demands = self.gp.get_demands()
                    print(demands)
                    self.heli_connection.send_input_demands(demands)
                except Exception as e:
                    print("Had some exception")
                    print(e)
                    # TODO: Handle the loss of the gamepad?
                    pass # We still need to check keyboard events in case of q/r being pressed
            else:
                # # Check the keyboard regardless (so we can listen for reset / quit requests)
                # events = get_key()
                # if events:
                #     for event in events:
                #         print(event.code)
                print("Error: Gamepad required.")
                self.run_thread = False

            sleep(0.0001)

    def exit_thread(self):
        self.run_thread = False
