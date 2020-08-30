""" Class to manage the demands and convert them into actual inputs for the Helicopter """
from helicopter import Helicopter
from threading import Thread
from pithonwy.sensors import Gyro

class HelicopterPilot:

    # Rates which equate to a demand of e.g. yaw rate = 1
    _max_gyro_rates = [10,10,10]

    def __init__(self):
        # Get the helicopter instance
        self.heli = Helicopter()
        # Gyro - how we sense the difference between the demand and the reality
        self.gyro = Gyro(normalise_rates=True,gyro_normalisation_rates=[1,1,1],acceleration_normalisation_rates=[1,1,1])
        # Init the demands variable
        self.demands = None
        self.flying = False
        self.thread_running = True
        # Create a thread for this to run in
        self.pilot_thread = Thread(target=self.fly, daemon=True)



    def update_demands(self, demands):
        """ Update the helicopter's input demands"""
        if not demands:
            # Then we haven't fired the motor up yet, so get it spinning
            self.heli.start_motor()
            self.flying = True
        self.demands = demands

    def fly(self):
        while self.thread_running:
            if self.flying:
                accelerations = self.gyro.get_acceleration()
                gyro_rates = self.gyro.get_gyro()
                for demand in self.demands:
                    demand_value = self.demands[demand]
                    if demand == 'stop':
                        pass
                    if demand == 'throttle_demand':
                        pass
                    if demand == 'yaw_demand':
                        current_yaw_rate = gyro_rates[2]
                        # TODO: Implement the control
                        pass
                    if demand == 'pitch_demand':
                        pass
                    if demand == 'roll_demand':
                        pass
                    if demand == 'init_connection_demand':
                        pass
