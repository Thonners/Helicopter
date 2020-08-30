""" Class to manage the demands and convert them into actual inputs for the Helicopter """
from helicopter import Helicopter
from threading import Thread
from pithonwy.sensors import Gyro

class HelicopterPilot:

    # Rates which equate to a demand of 1
    _gyro_normalisation_values = [50,50,80]

    # Thresholds
    _yaw_threshold = 0.1

    def __init__(self):
        # Get the helicopter instance
        self.heli = Helicopter()
        # Gyro - how we sense the difference between the demand and the reality
        # self.gyro = Gyro(normalise_rates=True,gyro_normalisation_values=self._gyro_normalisation_values,acceleration_normalisation_values=[1,1,1])
        self.gyro = None
        # Init the demands variable
        self.demands = None
        self.flying = False
        self.thread_running = True
        # Create a thread for this to run in
        self.pilot_thread = Thread(target=self.fly, daemon=True)
        self.pilot_thread.start()
        # while self.run_thread:
        #     pass

    def update_demands(self, demands):
        """ Update the helicopter's input demands"""
        if demands:
            print(f"Latest demands: {demands}")
            if not self.flying:
                if 'start_demand' in demands and 'stop_demand' in demands:
                    if demands['start_demand'] and not demands['stop_demand']:
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
                    if demand == 'stop_demand':
                        if demand_value:
                            self.heli.stop()
                            self.flying = False
                            # This call blocks, so we can't do any processing anyway
                            # Don't stop processing in this thread just yet in case we still need to do something on the other controls
                    if demand == 'start_demand':
                        # self.heli.start_motor()
                        # Motor started before we're 'flying', so do nothing now...
                        pass
                    if demand == 'throttle_demand':
                        pass
                    if demand == 'yaw_demand':
                        current_yaw_rate = gyro_rates[2]
                        demand_delta = demand_value - current_yaw_rate
                        # Only take action if we're outside the threshold range
                        if demand_delta > self._yaw_threshold:
                            print("Turning more left")
                            self.heli.turn_more_left()
                        elif demand_delta < -self._yaw_threshold:
                            print("Turning more right")
                            self.heli.turn_more_right()
                    if demand == 'pitch_demand':
                        pass
                    if demand == 'roll_demand':
                        pass
                    if demand == 'init_connection_demand':
                        pass

    def stop_flying(self):
        """ Cleanly and safely shut down the helicopter """
        self.heli.stop()
        self.thread_running = False
