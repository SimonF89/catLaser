# ServoController.py
# ============================================================================
# Most code from Adafruit PCA9685 16-Channel PWM Servo Driver, 
# with thanks to the author
# ============================================================================

from .PCA9685 import PCA9685
import time

class AngleMap:
    def __init__(self, min, minAngle, mid, midAngle, max, maxAngle):
        self.min = min
        self.minAngle = minAngle
        self.mid = mid
        self.midAngle = midAngle
        self.max = max
        self.maxAngle = maxAngle

class ServoController:
    decimalResolution = 1
    maxBreakTime = 0.2
    breakTime = 0.2
    currentPositions = [2.4, 2.0]
    InitPosition = [6.0, 5.3]
    AngleMaps = [
        AngleMap(11,-90,   6.0,0,    2.4, 90),
        AngleMap(10,-90,   5.3,0,    2.0, 90),
    ]
    
    def __init__(self):
        self.pca9685 = PCA9685()
        #self.start()
    
    def start(self):
        self.moveToDuty(self.InitPosition)
    
    # Sets speed in percent between min == 0 and  max == 100
    def setSpeed(self, speed):
        if speed > 100:
            speed = 100
        if speed < 1:
            speed = 1
        self.breakTime = self.maxBreakTime / speed
        
    def moveToAngle(self, angles):
        angles = self.adjustAngles(angles)
        dutys = self.calcDutys(angles)
        self.moveToDuty(dutys)
    
    # calcs Dutys according to predefined AngleMaps
    def calcDutys(self, angles):
        dutys = []
        for i in range(len(angles)):
            if self.AngleMaps[i].midAngle == None:
                a = self.AngleMaps[i].max - self.AngleMaps[i].min
                b = angles[i] - self.AngleMaps[i].minAngle
                c = self.AngleMaps[i].maxAngle - self.AngleMaps[i].minAngle
                d = self.AngleMaps[i].min + a*b/c
                dutys.append(d)
            elif angles[i] < self.AngleMaps[i].midAngle:
                a = self.AngleMaps[i].mid - self.AngleMaps[i].min
                b = angles[i] - self.AngleMaps[i].minAngle
                c = self.AngleMaps[i].midAngle - self.AngleMaps[i].minAngle
                d = self.AngleMaps[i].min + a*b/c
                dutys.append(d)
            else:
                a = self.AngleMaps[i].max - self.AngleMaps[i].mid
                b = angles[i] - self.AngleMaps[i].midAngle
                c = self.AngleMaps[i].maxAngle - self.AngleMaps[i].midAngle
                d = self.AngleMaps[i].mid + a*b/c
                dutys.append(d)
        return dutys
    
    # adjusts angles according to min and max values to prevent incorrect motions
    def adjustAngles(self, angles):
        for i in range(len(angles)):
            if angles[i] < self.AngleMaps[i].minAngle:
                angles[i] = self.AngleMaps[i].minAngle
            if angles[i] > self.AngleMaps[i].maxAngle:
                angles[i] = self.AngleMaps[i].maxAngle
        return angles
        
    def moveToDuty(self, positions):
        arrived = False
        while not arrived:
            positions = self.roundTargets(positions)
            for i in range(len(positions)):
                if positions[i] > self.currentPositions[i]:
                    self.currentPositions[i] = round(self.currentPositions[i] + 1 / (self.decimalResolution * 10), 1)
                    self.pca9685.setDuty(i, self.currentPositions[i])
                elif positions[i] < self.currentPositions[i]:
                    self.currentPositions[i] = round(self.currentPositions[i] - 1 / (self.decimalResolution * 10), 1)
                    self.pca9685.setDuty(i, self.currentPositions[i])
                else:
                    self.pca9685.setDuty(i, self.currentPositions[i])
            arrived = self.arrived(positions)
            time.sleep(self.breakTime)
            
    def roundTargets(self, positions):
        for i in range(len(positions)):
            positions[i] = round(positions[i], self.decimalResolution)
        return positions
            
    def turnOff(self):
        for i in range(len(self.currentPositions)):
            self.pca9685.setDuty(i, 0)
            
    def arrived(self, positions):
        for i in range(len(positions)):
            if positions[i] != self.currentPositions[i]:
                return False
        return True