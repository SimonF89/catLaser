from threading import Thread
import math
from app.models import Playground, Point, Edge, PointTypes
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
    INIT_EVENT_ID = 0
    INIT_SPEED = 0

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
        pass

    #def start(self):
    #    pass

    #def stop(self):
    #    pass


    def moveTo(self, target):

        Laser = 0          # TODO
        alpha = math.atan((Laser.x - target.x)/(Laser.y - target.y))
        beta = math.atan(Laser.z / math.sqrt(math.pow(Laser.x - target.x, 2) + math.pow(Laser.y - target.y, 2)))
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

    ZickZackcurrentDir = { 'x': 1, 'y': 1 }
    def FeatureZickZack(self):
        M
        if len(self.Targets) > 0:
            M = self.Targets[len(self.Targets) - 1]
        else:
            M = self.currentPos
        }
        var Dir = ZickZackcurrentDir;
        // calculate all hits of 2D Raycast with edges
        // AND calculate the distance to nearest edge (shortestDistance)
        var shortestDistance = 1000000;
        for (i = 0; i < edges.length; i++) {
            var _x = M.x + Dir.x * 1000000;
            var _y = M.y + Dir.y * 1000000;
            var pointer = { 'x': _x, 'y': _y };
            var P = get_line_intersection(M, pointer, edges[i].A, edges[i].B);

            if (P.x !== -6666 && P.y !== -6666) {
                var distance = Math.sqrt(Math.pow(M.x - P.x, 2) + Math.pow(M.y - P.y, 2));
                if (distance < shortestDistance) {
                    shortestDistance = distance;
                }
            }
        }
        // catch error - if shortestDistance is still the init value, something went wrong!
        if (shortestDistance === 1000000) {
            alert("something went wrong in FeatureZickZack.");
            return currentPos;
            // if this happens, maybe the currentPos wasent in the Playground anymore!
        }
        // calculate new Position according to Dir and distance to next edge (shortestDistance)
        var offset = getRndInteger(shortestDistance / 20, shortestDistance);
        var DirAbs = Math.sqrt(Math.pow(Dir.x, 2) + Math.pow(Dir.y, 2));
        var factor = (shortestDistance - offset) / DirAbs;
        var newX = M.x + Dir.x * factor;
        var newY = M.y + Dir.y * factor;

        // rotate Dir Vector Randomly
        var randomX = getRndInteger(-100, 100) / 100;
        var randomY = getRndInteger(-100, 100) / 100;
        ZickZackcurrentDir = { 'x': randomX, 'y': randomY };

        return { 'x': newX, 'y': newY, 'speed': SimulationCurrentSpeed, 'OnOff': true };
    }