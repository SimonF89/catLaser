
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

class Runner:
    EVENT_PROPABILITY = 20      # in %
    INIT_FEATURE_ID = 0
    INIT_EVENT_ID = 0
    INIT_SPEED = 0

    running = False
    current_Feature_ID  = INIT_FEATURE_ID
    current_Event_ID = INIT_EVENT_ID
    current_speed = INIT_SPEED              # needed? Or better Targets[0].speed
    Targets = []
    tmpTargets = []
    arrived = False

    def __init__(self, playground):
        self.setNewPlayground(playground)

    def setNewPlayground(self, playground):
        self.playgorund = playground
        #self.edges = playground.edges
        #self.run_points = playgorund.run_points

        P0 = playground.run_points[0]
        firstTarget = Target(P0.x, P0.y, MinMax.MAX_SPEED, True)

        self.running = False
        self.current_Feature_ID  = INIT_FEATURE_ID
        self.current_Event_ID = INIT_EVENT_ID
        self.current_speed = INIT_SPEED              # needed? Or better Targets[0].speed
        self.Targets = [firstTarget]
        self.tmpTargets = []
        self.arrived = False

    def start(self):
        pass

    def stop(self):
        pass

    def run(self):
        pass

