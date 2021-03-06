""" Class to manage the demands and convert them into actual inputs for the Helicopter """
from helicopter import Helicopter
from threading import Thread
from pithonwy.sensors import Gyro

class HelicopterPilot:

    # Rates which equate to a demand of 1
    _gyro_normalisation_values = [50,50,80]

    # Thresholds
    _min_throttle = 0.3
    _yaw_threshold = 0.1

    def __init__(self):
        # Get the helicopter instance
        self.heli = Helicopter()
        # Gyro - how we sense the difference between the demand and the reality
        self.gyro = Gyro(normalise_rates=True,gyro_normalisation_values=self._gyro_normalisation_values,acceleration_normalisation_values=[1,1,1])
        # Init the demands variable
        self.demands = None
        self.flying = False
        self.thread_running = True
        # Create a thread for this to run in
        self.pilot_thread = Thread(target=self.fly, daemon=True)
        self.pilot_thread.start()

    def update_demands(self, demands):
        """ Update the helicopter's input demands"""
        if demands:
#            print(f"Latest demands: {demands}")
            if not self.flying:
                if 'start_demand' in demands and 'stop_demand' in demands:
                    if demands['start_demand'] and not demands['stop_demand']:
                        # Then we haven't fired the motor up yet, so get it spinning
                        self.heli.start_motor()
                        self.flying = True
                if 'calibration_demand' in demands and demands['calibration_demand']:
                    # Then we want to calibrate - the gyro class will prevent us from running this multiple times, so just call calibrate() while the button is down
                    self.gyro.calibrate()

            self.demands = demands

    def fly(self):
        while self.thread_running:
            if self.flying:
                try:
                    accelerations = self.gyro.get_acceleration()
                    gyro_rates = self.gyro.get_gyro()
                except IOError as e:
                    print("Error getting gyro/accelerometer details!")
                    print(e)
                    accelerations = [0,0,0]
                    gyro_rates = [0,0,0]
                for demand in self.demands:
                    demand_value = self.demands[demand]
                    #print(f"Demand: {demand}, value = {demand_value}")
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
                        # Need to blend the throttle and blade pitch - increment throttle to match demand if above the threshold
                        throttle_demand = max(self._min_throttle, abs(demand_value)) # Make sure that the throttle is always at least _min_throttle, and set it equal to the magnitude of the demand
                        if self.flying:
                            # Update the motor speed
                            self.heli.motor.set_motor_speed(throttle_demand)
                            # Update the swash plate position
                            self.heli.swash_plate.set_height(demand_value)
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
                    if demand == 'request_gyro_state_demand':
                        if demand_value:
                            print(f"Gyro rates: {gyro_rates}, accelerations: {accelerations}")

    def stop_flying(self):
        """ Cleanly and safely shut down the helicopter """
        self.heli.stop()
        self.thread_running = False
