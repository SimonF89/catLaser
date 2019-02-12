from threading import Thread
import math
import time
from random import randint
from app.models import Playground, Point, Edge, PointTypes, point
from CatLaser.hardware.ServoController import ServoController
import RPi.GPIO as GPIO


class MinMax:
    MIN_SPEED = 1
    MAX_SPEED = 1     # all max is 100
    MIN_DURATION = 5                # [targets/feature]
    MAX_DURATION = 20               # [targets/feature]
    MAX_DISTANCE = 300              # [mm]
    MIN_BREAK = 1                   # [s]
    MAX_BREAK = 4                   # [s]
    MIN_BLINKS = 2
    MAX_BLINKS = 5

class Target:
    # x,y = planar coordinates of laser-point
    # speed = speed for Feature to move to Target
    # isON = is LaserPointer ON or OFF while moving to target
    # duration = time to wait on this Target till next Target. Initialy its 0. But for blink-events duration can be set > 0
    def __init__(self, x, y, speed, isON=True, Break=0, isBreak=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.isOn = isON
        self.Break = Break
        self.isBreak = isBreak

class Runner(Thread):
    FEATURE_COUNT = 2
    
    servo = ServoController()
    playgorund = None
    Targets = []

    laser = None
    ledPin = 4
    run_points = None
    currentPos = None
    edges = None
    current_speed = 10

    def __init__(self):
        Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ledPin, GPIO.OUT)

    def run(self):
        while True:
            if self.playgorund:
                if self.playgorund.active:
                    self.execute()
            else:
                self.playgorund = self.getRunningPlayground()
                if self.playgorund:
                    self.initPlayground(self.playgorund)
                print("active playground: " + self.playgorund.name)

    def initPlayground(self, playground):
        self.laser = playground.laser
        self.edges = playground.edges
        self.run_points = playground.run_points
        self.currentPos = Target(self.run_points[0].x, self.run_points[0].y, self.current_speed)
        self.Targets.append(self.currentPos)

    def getRunningPlayground(self):
        return Playground.objects.select_related().get(active=True)

    def debugAllTargets(self):
        for t in self.Targets:
            self.debugTarget(t)
            
    def debugTargets(self, targets):
        for t in targets:
            self.debugTarget(t)
            
    def debugTarget(self, target):
        print("x=" + str(target.x) + ", y=" + str(target.y))
    
    def execute(self):
        if len(self.Targets) > 0:
            self.moveTo(self.Targets.pop(0))
        else:
            featureID = randint(1,self.FEATURE_COUNT)
            self.current_speed = randint(MinMax.MIN_SPEED, MinMax.MAX_SPEED)
            # get random amount of new targets to calculate
            targetCount = randint(MinMax.MIN_DURATION, MinMax.MAX_DURATION)
            newTargets = []
            for i in range(targetCount):
                if featureID == 1:
                    if len(self.Targets) > 0:
                        target = self.FeatureABC()
                        newTargets = self.calcIntersteps(target, self.Targets[-1])
                    else:
                        newTargets = self.calcIntersteps(self.FeatureABC(), self.currentPos)
                elif featureID == 2:
                    if len(self.Targets) > 0:
                        newTargets = self.calcIntersteps(self.FeatureZickZack(), self.Targets[-1])
                    else:
                        newTargets = self.calcIntersteps(self.FeatureZickZack(), self.currentPos)
                else:
                    raise ValueError('Feature: ' + str(featureID) + ", does not exist!")
                # add newTargets to target list
                if isinstance(newTargets, list):
                    self.Targets = self.Targets + newTargets
                else:
                    self.Targets.append(newTargets)

            # add random breaks
            if randint(0,10) >= 7:
                breakTime = randint(MinMax.MIN_BREAK, MinMax.MAX_BREAK)
                self.Targets.append(Target(0, 0, self.current_speed, Break=1/breakTime, isBreak=True))

            # add random blinks
            if randint(0,10) >= 7:
                blinkCount = randint(MinMax.MIN_BLINKS, MinMax.MAX_BLINKS)
                blinkSpeed = randint(MinMax.MIN_BREAK, MinMax.MAX_BREAK)
                for i in range(blinkCount):
                    self.Targets.append(Target(0, 0, self.current_speed, isON=False, Break=1/blinkSpeed, isBreak=True))
                    self.Targets.append(Target(0, 0, self.current_speed, isON=True, Break=1/blinkSpeed, isBreak=True))

    def calcIntersteps(self, newTarget, oldTarget):
        print("oldTarget")
        self.debugTarget(oldTarget)
        print("newTarget")
        self.debugTarget(newTarget)
        
        distance = self.getDistance(newTarget, oldTarget)
        stepsCount = math.floor(distance / MinMax.MAX_DISTANCE)
        if stepsCount > 0:
            interstep = distance / stepsCount
            # calc direction from oldTarget to newTarget
            direction = point(newTarget.x - oldTarget.x, newTarget.y - oldTarget.y)
            newSteps = []
            print("stepscount: " + str(stepsCount))
            for i in range(stepsCount):
                newX = oldTarget.x + direction.x / distance * interstep * i
                newY = oldTarget.y + direction.y / distance * interstep * i
                newStep = Target(newX, newY, self.current_speed)
                newSteps.append(newStep)
            newSteps.append(newTarget)  
            return newSteps
        else:
            return newTarget

    def moveTo(self, target):
        print("moveto: x=" + str(target.x) + ", y=" + str(target.y))
        if target.isOn:
                self.setLaserOn()
        else:
            self.setLaserOff()
        # check if target is a break, if so --> start break
        if target.isBreak:
            time.sleep(target.Break)
        else:
            alpha, beta = self.getAngles(target)
            self.servo.setSpeed(self.current_speed)
            self.servo.moveToAngle([int(alpha), int(beta)])
            self.currentPos = target

    def setLaserOn(self):
        GPIO.output(self.ledPin, GPIO.HIGH)

    def setLaserOff(self):
        GPIO.output(self.ledPin, GPIO.LOW)

    def getAngles(self, target):
        alpha = self.toDegree(math.atan((self.laser.x - target.x)/(self.laser.y - target.y))) + 90
        beta = self.toDegree(math.atan(self.laser.z / math.sqrt(math.pow(self.laser.x - target.x, 2) + math.pow(self.laser.y - target.y, 2))))
        
        # convert beta so 90degree == middle of 180degree
        if target.y < self.laser.y:
            beta = beta + 90
        else:
            beta = 90 - beta
        return alpha, beta

    ####################################################
    ##################### Features #####################
    ####################################################

    ABCcounter = -1
    ABCstep = 1
    def FeatureABC(self):
        self.ABCcounter = self.ABCcounter + self.ABCstep
        if self.ABCcounter >= len(self.run_points):
            self.ABCstep = -self.ABCstep
            self.ABCcounter = self.ABCcounter + self.ABCstep
        elif self.ABCcounter < 0:
            self.ABCstep = -self.ABCstep
            self.ABCcounter = self.ABCcounter + self.ABCstep
        return Target(self.run_points[self.ABCcounter].x, self.run_points[self.ABCcounter].y, self.current_speed)

    ZickZackcurrentDir = point(1, 1)
    def FeatureZickZack(self):
        M = 0
        if len(self.Targets) > 0:
            M = self.Targets[len(self.Targets) - 1]
        else:
            M = self.currentPos
        Dir = self.ZickZackcurrentDir
        # calculate all hits of 2D Raycast with edges
        # AND calculate the distance to nearest edge (shortestDistance)
        shortestDistance = 1000000
        for i in range(len(self.edges)):
            _x = M.x + Dir.x * 1000000
            _y = M.y + Dir.y * 1000000
            pointer = point(_x, _y)
            P = self.get_line_intersection(M, pointer, self.edges[i].A, self.edges[i].B)

            if P.x != -6666 and P.y != -6666:
                distance = self.getDistance(M, P)
                if distance < shortestDistance:
                    shortestDistance = distance
        # catch error - if shortestDistance is still the init value, something went wrong!
        if shortestDistance == 1000000:
            print("something went wrong in FeatureZickZack.")
            #raise ValueError("something went wrong in FeatureZickZack.")
            return self.currentPos
            # if this happens, maybe the currentPos wasent in the Playground anymore!
        # calculate new Position according to Dir and distance to next edge (shortestDistance)
        offset = randint(int(shortestDistance / 20), int(shortestDistance))
        DirAbs = math.sqrt(math.pow(Dir.x, 2) + math.pow(Dir.y, 2))
        factor = (shortestDistance - offset) / DirAbs
        newX = M.x + Dir.x * factor
        newY = M.y + Dir.y * factor

        # rotate Dir Vector Randomly
        randomX = randint(-100, 100) / 100
        randomY = randint(-100, 100) / 100
        ZickZackcurrentDir = point(randomX, randomY)

        return Target(newX, newY, self.current_speed)

    def getDistance(self, A, B):
        return math.sqrt(math.pow(A.x - B.x, 2) + math.pow(A.y - B.y, 2))

    def get_line_intersection(self, A1, A2, B1, B2):
        a = A2.y - A1.y
        b = -B2.y + B1.y
        c = A2.x - A1.x
        d = -B2.x + B1.x
        C1 = B1.y - A1.y
        C2 = B1.x - A1.x

        tmp = a * d - b * c
        if tmp:
            invMa = d / tmp
            invMb = -b / tmp
            invMc = -c / tmp
            invMd = a / tmp

            m = invMa * C1 + invMb * C2
            n = invMc * C1 + invMd * C2
            if 0 <= m and m <= 1 and 0 <= n and n <= 1:
                x = A1.x + m * (A2.x - A1.x)
                y = A1.y + m * (A2.y - A1.y)
                return point(x, y)
            else:
                return point(-6666, -6666)
        else:
            return point(-6666, -6666)

    def toRadians(self, angle):
        return angle * math.pi / 180

    def toDegree(self, radian):
        return radian * 180 / math.pi