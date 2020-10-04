""" Code for all swash plate admin """
import math
from pithonwy.actuators.servo import Servo

class SwashPlate:
    def __init__(self, right, left, rear):
        right_servo = SwashPlateServo(**right)
        left_servo = SwashPlateServo(**left)
        rear_servo = SwashPlateServo(**rear)
        self.servos = [right_servo, left_servo, rear_servo]
        # Store the target values separately, so we can update them individually without affecting the other one(s)
        self._collective = 0
        self._pitch = 0
        self._roll = 0
    def level(self):
        """ Set the swash-plate to its 'level' position """
        [s.centre() for s in self.servos]
    def rise(self):
        """ Raise the swashplate uniformly """
        [servo.increment() for servo in self.servos]
    def lower(self):
        """ Lower the swashplate uniformly """
        [servo.decrement() for servo in self.servos]
    def update_position(self):
        """ Updates the position of the swashplate to match the current collective/pitch/roll targets """
        # The servo movement that would correspond to a value of '1' (if the position of the servo is also '1')
        # TODO: Get this value from somewhere more appropriate than hard coding it here
        max_servo_delta=15
        # print(f'Current swashplate targets; Collective: {self._collective}, Pitch: {self._pitch}, Roll: {self._roll}')
        for servo in self.servos:
            # Get the amount we need to move this servo
            servo_target_raw = self._collective + self._roll * servo.lateral_position + self._pitch * servo.forward_position
            # Limit the demand to -1 <= demand <= +1
            servo_target = max_servo_delta * max(-1,min(1,servo_target_raw))
            servo.set_position(servo_target)
            # print(f'Servo "{servo.forward_position},{servo.lateral_position}" target value: {servo_target}')
    def set_height(self,height:float):
        """ 
            Set the height of the swashplate to 'height' (-1 -> +1) without altering its orientation. 
            +ve height implies raising the swash-plate from its neutral position, -ve implies lowering it
        """
        self._collective = height
        self.update_position()
    def set_pitch(self, amount:float):
        """ 
            Rotate the swashplate about 'Y' axis by 'amount' (-1 -> +1) without altering its height. 
            +ve pitch implies rotating the front of the plate down, i.e. for forwards movement
        """
        self._pitch = amount
        self.update_position()
    def set_roll(self, amount:float):
        """ 
            Rotate the swashplate about 'X' axis by 'amount' (-1 -> +1) without altering its height. 
            +ve pitch implies rotating the RHS of the plate down, i.e. for rolling right movement
        """
        self._roll = amount
        self.update_position()
    def pitch_forwards(self, amount:float):
        """ Rotate the swashplate forwards by 'amount' (0-1) without altering its net height """
        self.set_pitch(amount)
    def pitch_backwards(self, amount:float):
        """ Rotate the swashplate rearwards by 'amount' (0-1) without altering its net height """
        # Just make the amount -ve to make the swashplate move the 'other' direction
        self.set_pitch(-amount)
    def roll_right(self, amount:float):
        """ Rotate the swashplate to the right by 'amount' (0-1) without altering its net height """
        self.set_roll(amount)
    def roll_left(self, amount:float):
        """ Rotate the swashplate to the left by 'amount' (0-1) without altering its net height """
        # Just make the amount -ve to make the swashplate move the 'other' direction
        self.set_roll(-amount)
    def calibrate(self):
        """ Allows the user to level the swash plate manually, then record the required offsets """
        # TODO: Provide a better interface for this
        print("To calibrate the swash plate, please ensure the helicopter is on a level surface.")
        print("Set the swash plate to nominally level with: swash_plate.centre()")
        print("Increment/decrement each swash servo until the swash plate is also level.")
        print("\tTo access the servos: swash_plate.right_servo / swash_plate.left_servo / swash_plate.rear_servo")
        print("\tTo raise/lower the servo: servo.increment() / servo.decrement()")
        print("\tWhen the swash plate is level, run this command again to get the required offsets")
        print("")
        # print(f'The current offsets are: "right": {self.right_servo.current_position}, "left":{self.left_servo.current_position}, "rear":{self.rear_servo.current_position}')
        

class SwashPlateServo(Servo):
    __slots__ = ['forward_position','lateral_position']
    def __init__(self, position_angle:int, gpio_pin:int, centre_offset:int=0, invert_up_down:bool = False):
        # Create the servo instance to drive the physical servo
        super().__init__(gpio_pin=gpio_pin, centre_offset=centre_offset, invert_up_down=invert_up_down)
        # Calculate the position of the servo to help with SwashPlate movements.
        # Position value is -1 to 1, mapping back to front and left to right respectively for forward and lateral positions
        angle_radians = math.radians(position_angle)
        self.forward_position = math.cos(angle_radians)
        self.lateral_position = math.sin(angle_radians)
