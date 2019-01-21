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

    def __init__(self, address = 0x40, channels=[0]):
        '''
        Creates an instance of the PWM chip at given i2c address.
        @param bus: the SMBus instance to access the i2c port (0 or 1).
        @param address: the address of the i2c chip (default: 0x40)
        '''
        self.bus = SMBus(1) # Raspberry Pi revision 2
        self.address = address
        self._writeByte(self._mode_adr, 0x00)
        self.channels = channels
        self.current_angles = [0,0]   # [degree]
        self.maxSpeed = 335           # [degree/second]
        self.minSpeed = 10            # [degree/second]
        
        self.fPWM = 50
        
        self.a = 8.5
        self.b = 2
        self.setFreq(self.fPWM)

    def setDirection(self, channel, direction, break_time):
        duty = self.a / 180 * direction + self.b
        self.setDuty(channel, duty)
        time.sleep(break_time)
 
    def moveServo(self, speed, channel, target_angle):
        if speed < self.minSpeed:
            speed = self.minSpeed
        if speed > self.maxSpeed:
            speed = self.maxSpeed
        id = 0
        for i in range(len(self.channels)):
            if self.channels[i] == channel:
                id = i
        if target_angle != self.current_angles[id]:
            break_time = (abs(target_angle - self.current_angles[id])/speed - 0.1706)/181
            if break_time <=0:
                break_time = 0
            
            if target_angle - self.current_angles[id] >= 0:
                for direction in range(self.current_angles[id], target_angle, 1):
                    self.setDirection(channel, direction, break_time)
            else:
                for direction in range(self.current_angles[id], target_angle, -1):
                    self.setDirection(channel, direction, break_time)
        self.current_angles[id] = target_angle
        self.setDuty(channel, 0)
        
    def setDirections(self, channel, direction):
        duty = self.a / 180 * direction + self.b
        self.setDuty(channel, duty)  
        
    # target_angles must be in same order as channels!
    def moveServoConcurrent(self, speed, target_angles):
        if len(self.channels) != len(target_angles):
            raise ValueError('Less target_angles then channels!')
        else:
            if speed < self.minSpeed:
                speed = self.minSpeed
            if speed > self.maxSpeed:
                speed = self.maxSpeed
            
            # get smallest DeltaAngle
            delta0 = abs(target_angles[0] - self.current_angles[0])
            delta1 = abs(target_angles[1] - self.current_angles[1])
            smallestDelta = delta0
            if delta0 >= delta1:
                smallestDelta = delta1
                
            print("smallestDelta" + str(smallestDelta))

            # get directions
            steps = []
            factor = 1
            for i in range(len(target_angles)):
                if smallestDelta > 1:
                    factor = abs(target_angles[i] - self.current_angles[i])/smallestDelta
                if target_angles[i] - self.current_angles[i] >= 0:
                    steps.append(int(1 * factor))
                else:
                    steps.append(int(-1 * factor))
                    
            print("steps " + str(steps))
            
            # move motors to position concurrent
            break_time = abs((abs(target_angles[0] - self.current_angles[0])/speed - 0.1706)/181)
            for j in range(smallestDelta):
                for i in range(len(target_angles)):
                    target_angle = self.current_angles[i] + steps[i]
                    if steps[i] > 0:
                        for direction in range(self.current_angles[i], target_angle, 1):
                                self.setDirections(self.channels[i], direction)
                    else:
                        for direction in range(self.current_angles[i], target_angle, -1):
                                self.setDirections(self.channels[i], direction)
                    self.current_angles[i] = target_angle
                time.sleep(break_time)

            # check if all motors on target_position, else correct it
            for i in range(len(target_angles)):
                if target_angles[i] != self.current_angles[i]:
                    self.moveServo(speed, self.channels[i], target_angles[i])
                self.setDuty(self.channels[i], 0)                

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