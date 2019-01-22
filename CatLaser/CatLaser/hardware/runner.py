from threading import Thread
import math
from random import randint
from app.models import Playground, Point, Edge, PointTypes, point
from CatLaser.hardware.pca9685 import PCA9685


class MinMax:
    MIN_SPEED = 100                 # [mm/s]
    MAX_SPEED = 4000                # [mm/s]
    MIN_FEATURE_DURATION = 10000    # [ms]
    MAX_FEATURE_DURATION = 30000    # [ms]
    MIN_EVENT_DURATION = 500        # [ms]
    MAX_EVENT_DURATION = 5000       # [ms]

class Target:
    # x,y = planar coordinates of laser-point
    # speed = speed for Feature to move to Target
    # isON = is LaserPointer ON or OFF while moving to target
    # duration = time to wait on this Target till next Target. Initialy its 0. But for blink-events duration can be set > 0
    def __init__(self, x, y, speed, isON, duration=0):
        self.x = x
        self.y = y
        self.speed = speed
        self.isOn = isON
        self.duration = duration

class Runner(Thread):
    pca = PCA9685(channels=[0,1])

    EVENT_PROPABILITY = 20      # in %
    INIT_FEATURE_ID = 0
    FEATURE_COUNT = 2
    INIT_EVENT_ID = 0
    INIT_SPEED = 0

    playgorund = None
    running = False
    
    current_Feature_ID  = INIT_FEATURE_ID
    featureDuration = 0
    current_Event_ID = INIT_EVENT_ID
    eventDuration = 0
    current_speed = INIT_SPEED              # needed? Or better Targets[0].speed
    Targets = []
    tmpTargets = []
    arrived = False

    def __init__(self, playground):
        Thread.__init__(self)
        self.setNewPlayground(playground)

    def setNewPlayground(self, playground):
        self.playgorund = playground
        self.laser = self.playgorund.laser
        self.edges = playground.edges
        self.run_points = playgorund.run_points

        P0 = playground.run_points[0]
        firstTarget = Target(P0.x, P0.y, MinMax.MAX_SPEED, True)

        self.moveTo(firstTarget)

        self.currentPos = firstTarget
        self.running = False
        self.current_Feature_ID  = INIT_FEATURE_ID
        self.current_Event_ID = INIT_EVENT_ID
        self.current_speed = INIT_SPEED              # needed? Or better Targets[0].speed
        self.Targets = [firstTarget]
        self.tmpTargets = []
        self.arrived = False

    def run(self):
        while True:
            if self.running:
                if len(self.Targets) > 0:
                    self.moveTo(self.Targets.pop(0))
                else:
                    featureID = randint(1,FEATURE_COUNT)
                    newTargets = []
                    if featureID == 1:
                        newTargets = self.FeatureABC()
                    elif featureID == 2:
                        newTargets = self.FeatureZickZack()
                    else:
                        raise ValueError('Feature: ' + str(featureID) + ", does not exist!")
                    self.Targets = self.Targets + newTargets
            else:
                self.playgorund = self.getRunningPlayground()
                if self.playgorund:

    #def start(self):
    #    pass

    #def stop(self):
    #    pass


    def moveTo(self, target):
        alpha = toDegree(math.atan((self.laser.x - target.x)/(self.laser.y - target.y)))
        beta = toDegree(math.atan(self.laser.z / math.sqrt(math.pow(self.laser.x - target.x, 2) + math.pow(self.laser.y - target.y, 2))))
        self.pca.moveServoConcurrent([alpha, beta])
        pass

    ABCcounter = -1
    ABCstep = 1
    def FeatureABC(self):
        if len(self.run_points) == 0:
            self.featureDuration = 0
            raise ValueError('no Run-Points defined! Simulation stoped!')
            self.running = False
            return None
        else:
            self.ABCcounter = self.ABCcounter + self.ABCstep
            if self.ABCcounter >= len(self.run_points):
                self.ABCstep = -self.ABCstep
                self.ABCcounter = self.ABCcounter + self.ABCstep
            elif self.ABCcounter < 0:
                self.ABCstep = -self.ABCstep
                self.ABCcounter = self.ABCcounter + self.ABCstep
            return Target(self.run_points[self.ABCcounter].x, self.run_points[self.ABCcounter].y, self.current_speed, True)

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

        return Target(newX, newY, self.current_speed, True)

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