from threading import Thread
import math
from random import randint
from app.models import Playground, Point, Edge, PointTypes, point
from CatLaser.hardware.pca9685 import PCA9685


class MinMax:
    MIN_SPEED = 100                 # [mm/s]
    MAX_SPEED = 4000                # [mm/s]

class Target:
    # x,y = planar coordinates of laser-point
    # speed = speed for Feature to move to Target
    # isON = is LaserPointer ON or OFF while moving to target
    # duration = time to wait on this Target till next Target. Initialy its 0. But for blink-events duration can be set > 0
    def __init__(self, x, y, speed, isON=True):
        self.x = x
        self.y = y
        self.speed = speed
        self.isOn = isON

class Runner(Thread):
    pca = PCA9685(channels=[0,1])
    playgorund = None
    Targets = []

    laser = None
    run_points = None
    currentPos = None
    edges = None
    current_speed = None

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            if self.playgorund:
                if self.playgorund.active:
                    self.execute()
            else:
                self.playgorund = self.getRunningPlayground()
                if self.playgorund:
                    self.initPlayground(self.playgorund)
                # for debuging, delete
                # for debuging, delete
                # for debuging, delete
                print("active playground: " + self.playgorund)
                # for debuging, delete
                # for debuging, delete
                # for debuging, delete

    def initPlayground(self, playground):
        self.laser = playground.laser
        self.edges = playgorund.edges
        self.run_points = playgorund.run_points
        self.currentPos = self.run_points[0]

    def getRunningPlayground(self):
        return Playground.objects.filter(active=True)

    def execute(self):
        if len(self.Targets) > 0:
            self.moveTo(self.Targets.pop(0))
        else:
            featureID = randint(1,FEATURE_COUNT)
            self.current_speed = randint(MinMax.MIN_SPEED, MinMax.MAX_SPEED)
            newTargets = []
            if featureID == 1:
                newTargets = self.FeatureABC()
            elif featureID == 2:
                newTargets = self.FeatureZickZack()
            else:
                raise ValueError('Feature: ' + str(featureID) + ", does not exist!")
            self.Targets = self.Targets + newTargets

    def moveTo(self, target):
        alpha = toDegree(math.atan((self.laser.x - target.x)/(self.laser.y - target.y)))
        beta = toDegree(math.atan(self.laser.z / math.sqrt(math.pow(self.laser.x - target.x, 2) + math.pow(self.laser.y - target.y, 2))))
        self.pca.moveServoConcurrent([alpha, beta])
        self.currentPos = target

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
        M
        if len(self.Targets) > 0:
            M = self.Targets[len(self.Targets) - 1]
        else:
            M = self.currentPos
        Dir = ZickZackcurrentDir
        # calculate all hits of 2D Raycast with edges
        # AND calculate the distance to nearest edge (shortestDistance)
        shortestDistance = 1000000
        for i in range(len(self.edges)):
            _x = M.x + Dir.x * 1000000
            _y = M.y + Dir.y * 1000000
            pointer = point(_x, _y)
            P = self.get_line_intersection(M, pointer, edges[i].A, edges[i].B)

            if P.x != -6666 and P.y != -6666:
                distance = Math.sqrt(Math.pow(M.x - P.x, 2) + Math.pow(M.y - P.y, 2))
                if distance < shortestDistance:
                    shortestDistance = distance
        # catch error - if shortestDistance is still the init value, something went wrong!
        if shortestDistance == 1000000:
            raise ValueError("something went wrong in FeatureZickZack.")
            return self.currentPos
            # if this happens, maybe the currentPos wasent in the Playground anymore!
        # calculate new Position according to Dir and distance to next edge (shortestDistance)
        offset = randint(shortestDistance / 20, shortestDistance)
        DirAbs = math.sqrt(math.pow(Dir.x, 2) + math.pow(Dir.y, 2))
        factor = (shortestDistance - offset) / DirAbs
        newX = M.x + Dir.x * factor
        newY = M.y + Dir.y * factor

        # rotate Dir Vector Randomly
        randomX = randint(-100, 100) / 100
        randomY = randint(-100, 100) / 100
        ZickZackcurrentDir = point(randomX, randomY)

        return Target(newX, newY, self.current_speed)

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