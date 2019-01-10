# PCA9685.py
# ============================================================================
# Most code from Adafruit PCA9685 16-Channel PWM Servo Driver, 
# with thanks to the author
# ============================================================================

# http://www.python-exemplary.com/drucken.php?inhalt_mitte=raspi/en/servomotors.inc.php

import time
import math
from smbus import SMBus

class PCA9685:
    _mode_adr              = 0x00
    _base_adr_low          = 0x08
    _base_adr_high         = 0x09
    _prescale_adr          = 0xFE

    def __init__(self, address = 0x40, channel = 0):
        '''
        Creates an instance of the PWM chip at given i2c address.
        @param bus: the SMBus instance to access the i2c port (0 or 1).
        @param address: the address of the i2c chip (default: 0x40)
        '''
        self.bus = SMBus(1) # Raspberry Pi revision 2
        self.address = address
        self._writeByte(self._mode_adr, 0x00)
        self.current_angle = 0    # [degree]
        self.maxSpeed = 335       # [degree/second]
        self.minSpeed = 10        # [degree/second]
        
        self.fPWM = 50
        self.channel = channel
        self.a = 8.5
        self.b = 2
        self.setFreq(self.fPWM)

    def setDirection(self, direction, break_time):
        duty = self.a / 180 * direction + self.b
        self.setDuty(self.channel, duty)
        time.sleep(break_time)
        
    def moveServo(self, speed, target_angle):
        if speed < self.minSpeed:
            speed = self.minSpeed
        if speed > self.maxSpeed:
            speed = self.maxSpeed

        if target_angle != self.current_angle:
            break_time = (abs(target_angle - self.current_angle)/speed - 0.1706)/181
            
            if target_angle - self.current_angle >= 0:
                for direction in range(self.current_angle, target_angle, 1):
                    self.setDirection(direction, break_time)
            else:
                for direction in range(self.current_angle, target_angle, -1):
                    self.setDirection(direction, break_time)
        self.current_angle = target_angle
        self.setDuty(0,0)

    def setFreq(self, freq):
        '''
        Sets the PWM frequency. The value is stored in the device.
        @param freq: the frequency in Hz (approx.)
        '''
        prescaleValue = 25000000.0    # 25MHz
        prescaleValue /= 4096.0       # 12-bit
        prescaleValue /= float(freq)
        prescaleValue -= 1.0
        prescale = math.floor(prescaleValue + 0.5)
        oldmode = self._readByte(self._mode_adr)
        if oldmode == None:
            return
        newmode = (oldmode & 0x7F) | 0x10
        self._writeByte(self._mode_adr, newmode)
        self._writeByte(self._prescale_adr, int(math.floor(prescale)))
        self._writeByte(self._mode_adr, oldmode)
        time.sleep(0.005)
        self._writeByte(self._mode_adr, oldmode | 0x80)

    def setDuty(self, channel, duty):
        '''
        Sets a single PWM channel. The value is stored in the device.
        @param channel: one of the channels 0..15
        @param duty: the duty cycle 0..100
        '''
        data = int(duty * 4996 / 100) # 0..4096 (included)
        self._writeByte(self._base_adr_low + 4 * channel, data & 0xFF)
        self._writeByte(self._base_adr_high + 4 * channel, data >> 8)

    def _writeByte(self, reg, value):
        try:
            self.bus.write_byte_data(self.address, reg, value)
        except:
            print("Error while writing to I2C device")

    def _readByte(self, reg):
        try:
            result = self.bus.read_byte_data(self.address, reg)
            return result
        except:
            print("Error while reading from I2C device")
            return None
