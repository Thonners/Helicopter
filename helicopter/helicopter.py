from pithonwy.actuators import Motor
from pithonwy.actuators import Servo
# from pithonwy.sensors import Gyro
from swash_plate import SwashPlate
from tail_servo import TailServo
import json

class Helicopter:
    def __init__(self, config=None):
        if not config:
            config = HelicopterConfig()
        # Get the sensors/actuators that we will need
        # # Gyro
        # self.gyro = Gyro()
        # Main motor - arm it so it's ready for connection
        self.motor = Motor(**config.motor)
        self.motor.arm()
        # Swash plate control
        self.swash_plate = SwashPlate(**config.swash_servos)
        # Tail
        self.tail = TailServo(**config.tail_servo)
    def arm(self):
        self.motor.arm()
    def stop(self, estop=False):
        """ Stop the motor (but not instantaneously (unless E-stopping!)) """
        if estop:
            self.motor.estop()
            print("Helicopter motor E-Stop!!!")
        else:
            print("Helicopter motor spinning down!")
            self.motor.spin_down()
    def start_motor(self,initial_speed = 0.3):
        """ Slowly spins up the motor to the requested speed """
        print("Helicopter motor spinning up!")
        self.motor.spin_up(limit=initial_speed, stop_after_initial_spin=False)
        print("\tMotor running")
    def level_swash(self):
        self.swash_plate.level()
    def up_more(self):
        # Loop through all servos controlling the swash plate and increment them to make the swash plate go up (and therefore AoA of blades go down)
        self.swash_plate.lower()
    def down_more(self):
        # Loop through all servos controlling the swash plate and decrement them to make the swash plate go down
        self.swash_plate.rise()
    def pitch_forwards(self):
        self.swash_plate.pitch_forwards()
    def pitch_backwards(self):
        self.swash_plate.pitch_backwards()
    def turn_more_left(self):
        self.tail.decrement()
    def turn_more_right(self):
        self.tail.increment()

class HelicopterConfig:
    """ Class to manage loading/saving a helicopter config file """
    def __init__(self, file_path = './heli_config.json'):
        with open(file_path,'r') as conf_file:
            conf = json.load(conf_file)
        if 'motor' not in conf:
            raise HelicopterConfigParseError(f"No motor settings found in the config file: {file_path}")
        if 'swash_servos' not in conf:
            raise HelicopterConfigParseError(f"No swash servo settings found in the config file: {file_path}")
        if 'tail_servo' not in conf:
            raise HelicopterConfigParseError(f"No tail servo settings found in the config file: {file_path}")
        if 'gyro' not in conf:
            raise HelicopterConfigParseError(f"No gyro settings found in the config file: {file_path}")
        self.motor = conf['motor']
        self.swash_servos = conf['swash_servos']
        self.tail_servo = conf['tail_servo']
        self.gyro = conf['gyro']

class HelicopterConfigParseError(Exception):
    pass
