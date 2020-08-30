from pithonwy.actuators.servo import Servo

class TailServo(Servo):
    """ Class to hold tail servo specific admin here if required """

    def __init__(self, gpio_pin:int, centre_offset:int=0, invert_up_down:bool = False):
        # Create the servo instance to drive the physical servo
        super().__init__(gpio_pin=gpio_pin, centre_offset=centre_offset, invert_up_down=invert_up_down)
