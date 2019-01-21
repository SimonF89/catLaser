"""
Definition of models.
"""

from django.db import models
import math

# TODO
# TODO
#
# - add StartPoint -- check if inside the Playground!
# - add LaserPosition -- needed for calculating alpha and beta angles!
# - check if run_points sit outside or directly on a edge!
#   - points directly on a edge generate errors on ZickZack!
#
#
# - Einschraenken der rotation bei ZickZackFeature -> koennte besser sein wenn es nicht so stark variiert??? Testen! eig ja sehr gut!
#
#
#
#
#
#
# - add WifiConfig -- textinput for wifi pw etc.
#                     make pw unreadable afterwards!
#                     if not connected retry!
#                     if connected - kill hotspot!
#                     on Start check for wifi-config - if not connected than hotspot!
# - add Room - calculate Playground automaticaly according to laser-position
#
# TODO
# TODO



class PointTypes(models.Model):
    corner = 'corner'
    run_point = 'run_point'
    direction = 'direction'
    normal = 'normal'
    middle = 'middle'
    CHOICES = (
        (corner, 'Playground Corner'),
        (run_point, 'Point inside the Playground'),
        (direction, 'Directional Vector'),
        (normal, 'Normal Vector'),
        (middle, 'Middle Point on Edge'),
    )
    POINT_CHOICES = (
        (corner, 'Playground Corner'),
        (run_point, 'Point inside the Playground'),
    )

class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Playground(models.Model):
    name = models.CharField(verbose_name="Name",default="Playground",max_length=50,)
    active = models.BooleanField(verbose_name="active",default=False)
    minX = models.FloatField(verbose_name="Min X",default=0.0)
    maxX = models.FloatField(verbose_name="Max X",default=0.0)
    minY = models.FloatField(verbose_name="Min Y",default=0.0)
    maxY = models.FloatField(verbose_name="Max Y",default=0.0)

    def getLaser(self):
        return LaserPosition.objects.filter(playground=self)
    def getEdges(self):
        return Edge.objects.filter(playground=self)
    def getPoints(self):
        return Point.objects.filter(playground=self)
    def getCorners(self):
        return Point.objects.filter(playground=self,type=PointTypes.corner)
    def getRunPoints(self):
        return Point.objects.filter(playground=self,type=PointTypes.run_point)

    laser = property(getLaser)
    edges = property(getEdges)
    points = property(getPoints)
    corners = property(getCorners)
    run_points = property(getRunPoints)

    ###############################################################################
    #############################      functions      #############################
    ###############################################################################

    def customInit(self, playground_instance):
        #### TODO verhindere Duplikate Namen
        #### TODO verhindere Duplikate Namen
        #### TODO verhindere Duplikate Namen
        #### TODO verhindere Duplikate Namen
        #### TODO verhindere Duplikate Namen
        if self.name == "Playground":
            self.name = self.name + ' ' + str(self.id)
            self.save()
        # delete all edges and recalculate them
        self.deleteEdges(self.edges)
        if len(self.corners) > 2:
            obj = Playground.objects.select_related().filter(id=self.id)
            # calc all Min an Max Values of Playground
            self.calcMinMax(self.corners, obj)
            # calc all Edges
            _edges = self.calcEdges(self.corners, obj, playground_instance)
            # calculate correct direction of normals and replace normals with correct once
            self.calcNormals(_edges, playground_instance)

    def deleteEdges(self, edges):
        for edge in edges:
            m = edge.M
            vr = edge.Vr
            nr = edge.Nr
            edge.delete()
            m.delete()
            vr.delete()
            nr.delete()

    def calcMinMax(self, points, obj):
        _minx = points[0].x
        _maxx = points[0].x
        _miny = points[0].y
        _maxy = points[0].y
        for i in range(1,len(points)):
            if points[i].x < _minx:
                _minx = points[i].x
            if points[i].x > _maxx:
                _maxx = points[i].x
            if points[i].y < _miny:
                _miny = points[i].y
            if points[i].y > _maxy:
                _maxy = points[i].y
        obj.update(minX=_minx)
        obj.update(maxX=_maxx)
        obj.update(minY=_miny)
        obj.update(maxY=_maxy)

    def calcEdges(self, points, obj, playground_instance):
        edges = []
        for i in range(1,len(points)):
            edge = self.initEdge(points[i-1],points[i], playground_instance)
            edges.append(edge)
        edge = self.initEdge(points[len(points)-1],points[0], playground_instance)
        edges.append(edge)
        return edges

    def initEdge(self, _A, _B, playground_instance):
        _x = _B.x - _A.x
        _y = _B.y - _A.y
        vr = Point(x=_x, y=_y, type=PointTypes.direction, playground=playground_instance)
        vr.save()
        nr = Point(x=-_y, y=_x, type=PointTypes.normal, playground=playground_instance)
        nr.save()
        _x = _A.x + vr.x * 0.5
        _y = _A.y + vr.y * 0.5
        m = Point(x=_x, y=_y, type=PointTypes.middle, playground=playground_instance)
        m.save()
        edge = Edge(A=_A, B=_B, Vr=vr, Nr=nr, M=m, playground=playground_instance)
        edge.save()
        return edge

    # checks for bad-Intersections see self.badIntersection()
    def calcNormals(self, edges, playground_instance):
        for i in range(len(edges)):
            hits = {"pos":[], "neg":[]}
            j=0
            M = point(edges[i].M.x,edges[i].M.y)
            while j < len(edges):
                if edges[j] != edges[i]:
                    intersect, pos, bad, distance = self.get_hits(M, edges[i].Nr, edges[j].A, edges[j].B)
                    if intersect:
                        if bad:
                            x = M.x + 0.2*edges[i].Vr.x
                            y = M.y + 0.2*edges[i].Vr.y
                            hits = {"pos":[], "neg":[]}
                            M=point(x,y)
                            j=-1
                        elif pos:
                            hits["pos"].append({"edgeID":j, "distance":distance})
                        else:
                            hits["neg"].append({"edgeID":j, "distance":distance})
                j+=1
            if len(hits["neg"])%2 == 1:
                nr = edges[i].Nr
                Point.objects.filter(id=nr.id).update(x=-nr.x, y=-nr.y)

    # returns: intersect, pos, parallel, distance
    def get_hits(self, M, Nr, A, B):
        x = B.x - A.x
        y = B.y - A.y
        vr = point(x,y)
        if self.badIntersection(M, Nr, A, vr):
            return True, False, True, 0
        # calc positive hits
        _x = M.x + Nr.x * 1000000;
        _y = M.y + Nr.y * 1000000;
        Mpos = point(_x,_y)
        P = self.get_line_intersection(M, Mpos, A, B)
        if P.x != -6666 and P.y != -6666:
            distance = math.sqrt((M.x - P.x)**2 + (M.y - P.y)**2)
            return True, True, False, distance
        # calc negative hits
        _x = M.x - Nr.x * 1000000;
        _y = M.y - Nr.y * 1000000;
        Mneg = point(_x,_y)
        P = self.get_line_intersection(M, Mneg, A, B)
        if P.x != -6666 and P.y != -6666:
            distance = math.sqrt((M.x - P.x)**2 + (M.y - P.y)**2)
            return True, False, False, distance
        else:
            return False, False, False, 0
    
    # checks if there is any bad intersection e.g. intersect with a corner or colinear to a line
    def badIntersection(self, M, Nr, A, Vr,tol=1e-3):
        if self.areparallel(Nr,Vr,tol=tol):
            if -tol <= Vr.x <= tol:
                if A.x-tol <= M.x <= A.x+tol:
                    return True
                else:
                    return False
            elif -tol <= Vr.y <= tol:
                if A.y-tol <= M.y <= A.y+tol:
                    return True
                else:
                    return False
            else:
                k1 = (A.x-M.x)/Nr.x
                k2 = (A.y-M.y)/Nr.y
                if k1-tol <= k2 <= k1+tol:
                    return True
                else:
                    return False
        else:
            if -tol <= Nr.x <= tol:
                if A.x-tol <= M.x <= A.x+tol:
                    return True
                else:
                    return False
            elif -tol <= Nr.y <= tol:
                if A.y-tol <= M.y <= A.y+tol:
                    return True
                else:
                    return False
            else:
                k1 = (A.x-M.x)/Nr.x
                k2 = (A.y-M.y)/Nr.y
                if k1-tol <= k2 <= k1+tol:
                    return True
                else:
                    B = point(A.x+Vr.x,A.y+Vr.y)
                    k1 = (B.x-M.x)/Nr.x
                    k2 = (B.y-M.y)/Nr.y
                    if k1-tol <= k2 <= k1+tol:
                        return True
                    else:
                        return False

    def areparallel(self, X, Y, tol=1e-10):
        if -tol<=X.x<=tol and -tol<=Y.x<=tol:
            if X.y-tol <= Y.y <= X.y+tol:
                return True
            else:
                return False
        elif -tol<=X.y<=tol and -tol<=Y.y<=tol:
            if X.x-tol <= Y.x <= X.x+tol:
                return True
            else:
                return False
        elif -tol<=X.x<=tol or -tol<=Y.x<=tol or -tol<=X.y<=tol or -tol<=Y.y<=tol:
            return False
        else:
            k1 = X.x/Y.x
            k2 = X.y/Y.y
            if k1 == k2:
                return True
            else:
                return False

    def get_line_intersection(self, A1, A2, B1, B2):
        a = A2.y - A1.y
        b = -B2.y + B1.y
        c = A2.x - A1.x
        d = -B2.x + B1.x
        C1 = B1.y - A1.y
        C2 = B1.x - A1.x
    
        tmp = a * d - b * c
        if tmp:
            invMa = d  / tmp
            invMb = -b / tmp
            invMc = -c / tmp
            invMd = a  / tmp
        
            m = invMa * C1 + invMb * C2
            n = invMc * C1 + invMd * C2

            if 0<=m<=1 and 0<=n<=1:
                return point(A1.x + m * (A2.x - A1.x), A1.y + m * (A2.y - A1.y))
            else:
                return point(-6666,-6666)
        else:
            return point(-6666,-6666)

class Point(models.Model):
    x = models.FloatField(verbose_name="X-Value")
    y = models.FloatField(verbose_name="Y-Value")
    type = models.CharField(choices=PointTypes.CHOICES,verbose_name="Point Type",default=PointTypes.corner,max_length=50,)
    playground = models.ForeignKey(Playground,verbose_name="Playground",on_delete=models.CASCADE,)

    def __str__(self):
        return 'x: ' + str(self.x) + ', y: ' + str(self.y) + ', Type: ' + self.type

class LaserPosition(models.Model):
    x = models.FloatField(verbose_name="X-Value")
    y = models.FloatField(verbose_name="Y-Value")
    z = models.FloatField(verbose_name="Z-Value")
    playground = models.OneToOneField(Playground,verbose_name="Laser",on_delete=models.CASCADE)
    
    def __str__(self):
        return 'x: ' + str(self.x) + ', y: ' + str(self.y) + ', z: ' + str(self.z)

class Edge(models.Model):
    A = models.ForeignKey(Point,verbose_name="Point A",related_name='A',on_delete=models.CASCADE)
    B = models.ForeignKey(Point,verbose_name="Point B",related_name='B',on_delete=models.CASCADE)
    M = models.ForeignKey(Point,verbose_name="Middle Point",related_name='M',on_delete=models.CASCADE,blank=True, null=True)
    Vr = models.ForeignKey(Point,verbose_name="Direction Vector",related_name='Vr',on_delete=models.CASCADE)
    Nr = models.ForeignKey(Point,verbose_name="Normal Vector",related_name='Nr',on_delete=models.CASCADE)
    playground = models.ForeignKey(Playground,verbose_name="Playground",on_delete=models.CASCADE,)

    def isHitten(self, currentPosition, direction):
        #if p1-p2 hits edge return true
        #else return false
        pass

    def __str__(self):
        return 'A: ' + str(self.A) + ', B: ' + str(self.B) + ' , Playground: ' + self.playground.name


######################
#### nice to know ####
######################

# self.model._meta.get_all_field_names()


            


                # calculate shortest distance to all intersecting edges! --> for simulation!!!
                #id = hits["neg"][0]["edgeID"]
                #distance = hits["neg"][0]["distance"]
                #for j in range(1,len(hits["neg"])):
                #    if distance < hits["neg"][j]["distance"]:
                #        id = hits["neg"][j]["edgeID"]
                #        distance = hits["neg"][j]["distance"]