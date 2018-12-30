"""
Definition of models.
"""

from django.db import models


POINT_TYPE=(
    ('corner', 'Playground Corner'),
    ('run_point', 'Point inside the Playground'),
    ('vector', 'Vector or Direction'),
    )

class Point(models.Model):
    x = models.IntegerField(verbose_name="X-Value")
    y = models.IntegerField(verbose_name="Y-Value")
    type = models.CharField(choices=POINT_TYPE,verbose_name="Point Type",default=POINT_TYPE[0],max_length=50,)

class Edge(models.Model):
    A = models.ForeignKey(Point,verbose_name="Point A",related_name='A',on_delete=models.CASCADE,limit_choices_to={'type':str(POINT_TYPE[0])},)
    B = models.ForeignKey(Point,verbose_name="Point B",related_name='B',on_delete=models.CASCADE,limit_choices_to={'type':POINT_TYPE[0]},)
    Vr = models.ForeignKey(Point,verbose_name="Direction Vector",related_name='Vr',on_delete=models.CASCADE,limit_choices_to={'type':POINT_TYPE[2]},)
    Nr = models.ForeignKey(Point,verbose_name="Normal Vector",related_name='Nr',on_delete=models.CASCADE,limit_choices_to={'type':POINT_TYPE[2]},)

    def isHitten(self, currentPosition, direction):
        #if p1-p2 hits edge return true
        #else return false
        pass

class Playground(models.Model):
    minX = models.IntegerField(verbose_name="Min X")
    minY = models.IntegerField(verbose_name="Min Y")
    maxX = models.IntegerField(verbose_name="Max X")
    maxY = models.IntegerField(verbose_name="Max Y")
    corners = models.ForeignKey(Point,verbose_name="Corners of Playground",related_name='corners',on_delete=models.CASCADE,limit_choices_to={'type':POINT_TYPE[0]},)
    run_points = models.ForeignKey(Point,verbose_name="Running Points",related_name='run_points',on_delete=models.CASCADE,limit_choices_to={'type':POINT_TYPE[1]},)
    edges = models.ForeignKey(Edge,verbose_name="Edges",related_name='edges',on_delete=models.CASCADE,)

    def Init(self):
        self.calcMinMax(self.corners)

    def calcMinMax(self, points):
        _minx = points[0].x
        _maxx = points[0].x
        _miny = points[0].y
        _maxy = points[0].y
        for i in range(1,len(points)):
            if points[i].x > self.maxx:
                self.maxx = points[i].x
            if points[i].x < self.minx:
                self.maxx = points[i].x
            if points[i].y > self.maxy:
                self.maxy = points[i].y
            if points[i].y < self.miny:
                self.miny = points[i].y
        