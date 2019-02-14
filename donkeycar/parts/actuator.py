"""
actuators.py
Classes to control the motors and servos. These classes
are wrapped in a mixer class before being used in the drive loop.
"""

import time
import datetime
import donkeycar as dk
import donkeycar.parts.ev3_package.ev3 as ev3
import donkeycar.parts.ev3_package.ev3mail as ev3mail

flag = False

class PCA9685:
    """
    PWM motor controler using PCA9685 boards.
    This is used for most RC Cars
    """
    def __init__(self, channel, frequency=60):

        # Initialise the EV3 module
        global my_ev3
        global flag
        if flag == False:
            print ("Initialise the EV3 module")
            my_ev3 = ev3.EV3(protocol=ev3.WIFI, host='00:16:53:44:23:17')
            my_ev3.verbosity = 0
            flag = True
        else:
            print ("Skip EV3 Initialialise")

        self.pre_angle = 0
        self.pre_throttle = 0

    def get_ev3():
        return my_ev3

    def set_pulse(self, pulse):
        try:
            tmp = 1
#            print ("Bin's update - set_pulse", tmp++)
             #            self.pwm.set_pwm(self.channel, 0, pulse)
        except OSError as err:
            print("Unexpected issue setting PWM (check wires to motor board): {0}".format(err))

    def set_Steering(self, angle):
        try:
            angle = int(angle * 45)
            if angle < 1 and angle > -1 :
                angle = 0

            if angle == self.pre_angle:
                #print("skip since angle keep same: angle {} pre_angle {}".format(angle, self.pre_angle))
                return
            else:
                self.pre_angle = angle

            now = datetime.datetime.now().strftime('%H:%M:%S.%f')
            print(now + " Ev3 Steering <<< >>> Angle: {:+3d}".format(angle))
            s = ev3mail.ev3mailbox.encodeMessage(ev3mail.MessageType.Numeric, 'AngleBox', angle)
            my_ev3.send_system_cmd(s, False)
            #time.sleep(0.5)

        except OSError as err:
            print("Unexpected issue setting Steering (check wires to motor board): {0}".format(err))

    def set_Throttle(self, throttle):
        try:
            throttle = int(throttle * 40)

            if throttle == self.pre_throttle:
                #print("skip since throttle keep same: throttle {} pre_throttle {}".format(throttle,self.pre_throttle))
                return
            else:
                self.pre_throttle = throttle

            now = datetime.datetime.now().strftime('%H:%M:%S.%f')
            print(now + " Ev3 Throttle ^^^ vvv Throttle: {:+3d} ".format(throttle))
            s = ev3mail.ev3mailbox.encodeMessage(ev3mail.MessageType.Numeric, 'ThrottleBox', throttle)
            my_ev3.send_system_cmd(s, False)
#            time.sleep(0.5)

        except OSError as err:
            print("Unexpected issue setting Throttle EV3 (check wires to motor board): {0}".format(err))

    def run(self, pulse):
        print ("Bin's update - run")
#        self.set_pulse(pulse)


class PWMSteering:
    """
    Wrapper over a PWM motor cotnroller to convert angles to PWM pulses.
    """
    LEFT_ANGLE = -1
    RIGHT_ANGLE = 1

    def __init__(self, controller=None,
                 left_pulse=290, right_pulse=490):

        self.controller = controller
        self.left_pulse = left_pulse
        self.right_pulse = right_pulse

    def run(self, angle):
        # map absolute angle to angle that vehicle can implement.
        # wangbin
        self.controller.set_Steering(angle)

    def shutdown(self):
        self.run(0)  # set steering straight


class PWMThrottle:
    """
    Wrapper over a PWM motor cotnroller to convert -1 to 1 throttle
    values to PWM pulses.
    """
    MIN_THROTTLE = -1
    MAX_THROTTLE = 1

    def __init__(self,
                 controller=None,
                 max_pulse=300,
                 min_pulse=490,
                 zero_pulse=350):

        self.controller = controller
        self.max_pulse = max_pulse
        self.min_pulse = min_pulse
        self.zero_pulse = zero_pulse

        self.controller.set_pulse(self.zero_pulse)
        time.sleep(1)

    def run(self, throttle):
        # wangbin
        self.controller.set_Throttle(throttle)

    def shutdown(self):
        self.run(0)  # stop vehicle


class Adafruit_DCMotor_Hat:
    """
    Adafruit DC Motor Controller
    Used for each motor on a differential drive car.
    """
    def __init__(self, motor_num):
        from Adafruit_MotorHAT import Adafruit_MotorHAT
        import atexit

        self.FORWARD = Adafruit_MotorHAT.FORWARD
        self.BACKWARD = Adafruit_MotorHAT.BACKWARD
        self.mh = Adafruit_MotorHAT(addr=0x60)

        self.motor = self.mh.getMotor(motor_num)
        self.motor_num = motor_num

        atexit.register(self.turn_off_motors)
        self.speed = 0
        self.throttle = 0

    def run(self, speed):
        """
        Update the speed of the motor where 1 is full forward and
        -1 is full backwards.
        """
        if speed > 1 or speed < -1:
            raise ValueError("Speed must be between 1(forward) and -1(reverse)")

        self.speed = speed
        self.throttle = int(dk.util.data.map_range(abs(speed), -1, 1, -255, 255))

        if speed > 0:
            self.motor.run(self.FORWARD)
        else:
            self.motor.run(self.BACKWARD)

        self.motor.setSpeed(self.throttle)

    def shutdown(self):
        self.mh.getMotor(self.motor_num).run(Adafruit_MotorHAT.RELEASE)
