"""
Gamepad class to convert the basic gamepad interface into helicopter controller specifics

- Left joystick X  = Yaw
- Left joystick Y  = Throttle
- Right joystick X = Roll
- Right joystick Y = Pitch

 """
from inputs import devices

class GamePad:

    _max_joystick_value = 32000

    def __init__(self):
        # Check there is a gamepad present!
        if len(devices.gamepads) == 0:
            raise IOError("No gamepad found.")
        # If so, get reference to it
        self.gamepad = devices.gamepads[0]
        # Initialise the status of all the possible inputs
        self.throttle_demand = 0
        self.yaw_demand = 0
        self.pitch_demand = 0
        self.roll_demand = 0

    def update_inputs(self):
        events = self.gamepad.read()
        for event in events:
            # print(event.code)
            # if abs(event.state) > (0.8*self._max_joystick_value):
            #     print(event.state)
            if event.code == 'ABS_X':
                # Yaw - needs inverting to make 'up' on the controller = +1
                self.yaw_demand = min(1,max(-1,event.state/self._max_joystick_value))
            if event.code == 'ABS_Y':
                # Throttle
                # TODO: Filter the throttle demand so it only starts after has been fully down, or move it to right trigger
                self.throttle_demand = -min(1,max(-1,event.state/self._max_joystick_value))
            if event.code == 'ABS_RX':
                # Roll
                self.roll_demand = min(1,max(-1,event.state/self._max_joystick_value))
            if event.code == 'ABS_RY':
                # Pitch - needs inverting to make 'up' on the controller = +1
                self.pitch_demand = -min(1,max(-1,event.state/self._max_joystick_value))
            if event.code == 'ABS_Z':
                # Left lower trigger
                print("Left lower trigger pressed, but currently does nothing")
                # self.?_demand = Math.min(1,Math.max(-1,event.state/self._max_joystick_value))
            if event.code == 'ABS_RZ':
                # Right lower trigger
                print("Right lower trigger pressed, but currently does nothing")
                # self.?_demand = Math.min(1,Math.max(-1,event.state/self._max_joystick_value))
            if event.code == 'BTN_NORTH':
                # 'Y' button
                print("Y button pressed, but currently does nothing")
            if event.code == 'BTN_WEST':
                # 'X' button
                print("X button pressed, but currently does nothing")
            if event.code == 'BTN_EAST':
                # 'B' button
                print("B button pressed, but currently does nothing")
            if event.code == 'BTN_SOUTH':
                # 'A' button
                print("A button pressed, but currently does nothing")
            if event.code == 'BTN_SELECT':
                # 'Select' button
                print("Select button pressed, but currently does nothing")
            if event.code == 'BTN_START':
                # 'Start' button
                print("Start button pressed, but currently does nothing")
            if event.code == 'BTN_MODE':
                # 'XBox' button
                print("XBox button pressed, but currently does nothing")
            if event.code == 'BTN_TR':
                # Right trigger button
                print("Right trigger button pressed, but currently does nothing")
            if event.code == 'BTN_TL':
                # Left trigger button
                print("Left trigger button pressed, but currently does nothing")

    def get_demands(self):
        self.update_inputs()
        return {
            'throttle_demand': self.throttle_demand,
            'yaw_demand': self.yaw_demand,
            'pitch_demand': self.pitch_demand,
            'roll_demand': self.roll_demand,
        }
    