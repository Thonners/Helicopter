"""
Gamepad class to convert the basic gamepad interface into helicopter controller specifics

- Left joystick X  = Yaw
- Left joystick Y  = Throttle
- Right joystick X = Roll
- Right joystick Y = Pitch

Startup Procedure:
 1. Power on helicopter and ensure heli_server is running
 2. Press the start button to connect the controller to the helicopter
 3. Connect the battery to the ESC (might need to do this earlier if things fall over due to no power being delivered to gyro)
 4. Ensure the heli is on a flat, stationary surface then press and hold 'select' for 2s to calibrate the gyro
 5. Press both (upper) triggers simulateously to start the motor spinning

 Press the Xbox button at any time to stop the motor

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
        self.stop_demand = False
        self.start_demand = False
        self.calibration_demand = False
        self.throttle_demand = 0
        self.yaw_demand = 0
        self.pitch_demand = 0
        self.roll_demand = 0
        self.init_connection_demand = False
        self.battery_connected = False
        self.request_gyro_state = False
        # Make a note of the button states, for compound button press requirements
        self.left_trigger_pressed = False
        self.right_trigger_pressed = False

    def update_inputs(self):
        events = self.gamepad.read()
        for event in events:
            # print(event.code)
            # if abs(event.state) > (0.8*self._max_joystick_value):
            # print(event.state)
            if event.code == 'SYN_REPORT':
                # Ignore system sync reports - otherwise we end up with 2 events for every input action.
                return False
            if event.code == 'ABS_X':
                # Yaw - needs inverting to make 'left' on the controller +ve (i.e. +ve about an 'upwards' Z axis)
                self.yaw_demand = -min(1,max(-1,event.state/self._max_joystick_value))
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
                if event.state == 1:
                    print("Y button pressed, requesting gyro readings")
                    self.request_gyro_state = True
                else:
                    self.request_gyro_state = False
            if event.code == 'BTN_WEST':
                # 'X' button
                print("X button pressed, but currently does nothing")
            if event.code == 'BTN_EAST':
                # 'B' button
                print("B button pressed, but currently does nothing")
            if event.code == 'BTN_SOUTH':
                # 'A' button
                if event.state == 1:
                    print("A button pressed, waking up the pilot...")
                    self.battery_connected = True
            if event.code == 'BTN_SELECT':
                # 'Select' button
                if event.state == 1:
                    self.calibration_demand = True
                    print("Select button pressed, initiating Gyro calibration")
                else:
                    self.calibration_demand = False
            if event.code == 'BTN_START' and event.state == 0:
                # 'Start' button (just released)
                print("Start button pressed, Trying to connect to helicopter server.")
                self.init_connection_demand = True
            if event.code == 'BTN_MODE':
                # 'XBox' button
                print("XBox button pressed, stopping the motor!")
                if event.state == 1:
                    self.stop_demand = True
                    self.start_demand = False
            if event.code == 'BTN_TR':
                # Right trigger button
                if event.state == 1:
                    print("Right trigger button pressed")
                    self.right_trigger_pressed = True
                else:
                    print("Right trigger button released")
                    self.right_trigger_pressed = False
            if event.code == 'BTN_TL':
                # Left trigger button
                if event.state == 1:
                    print("Left trigger button pressed")
                    self.left_trigger_pressed = True
                else:
                    print("Left trigger button released")
                    self.left_trigger_pressed = False
        # Check for a motor start request
        if self.left_trigger_pressed and self.right_trigger_pressed:
            print("Both right and left triggers depressed")
            self.stop_demand = False
            self.start_demand = True
        return True

    def get_demands(self):
        legit_update = self.update_inputs()
        if legit_update:
            return {
                'stop_demand':self.stop_demand,
                'start_demand':self.start_demand,
                'calibration_demand':self.calibration_demand,
                'throttle_demand': self.throttle_demand,
                'yaw_demand': self.yaw_demand,
                'pitch_demand': self.pitch_demand,
                'roll_demand': self.roll_demand,
                'init_connection_demand': self.init_connection_demand,
                'battery_connected': self.battery_connected,
            }
    