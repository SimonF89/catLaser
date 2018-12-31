"""
Definition of models.
"""

from django.db import models


POINT_TYPE=(
    ('corner', 'Playground Corner'),
    ('run_point', 'Point inside the Playground'),
    ('vector', 'Vector or Direction'),
    )

class Playground(models.Model):
    name = models.CharField(verbose_name="Name",default="Playground",max_length=50,)
    minX = models.IntegerField(verbose_name="Min X",default=0)
    minY = models.IntegerField(verbose_name="Min Y",default=0)
    maxX = models.IntegerField(verbose_name="Max X",default=0)
    maxY = models.IntegerField(verbose_name="Max Y",default=0)

    def calcMinMax(self, points):
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
        self.minX = _minx
        self.maxX = _maxx
        self.minY = _miny
        self.maxY = _maxy

    def save(self, *args, **kwargs):
        points = Point.objects.filter(type=POINT_TYPE[0][0])
        for element in points:
            print(element)
        for element in kwargs:
            print(element)
        for element in args:
            print(element)
        super(Playground, self).save(*args, **kwargs)

class Point(models.Model):
    x = models.IntegerField(verbose_name="X-Value")
    y = models.IntegerField(verbose_name="Y-Value")
    type = models.CharField(choices=POINT_TYPE,verbose_name="Point Type",default=POINT_TYPE[0],max_length=50,)
    playground = models.ForeignKey(Playground,verbose_name="Playground",on_delete=models.CASCADE,)

class Edge(models.Model):
    A = models.ForeignKey(Point,verbose_name="Point A",related_name='A',on_delete=models.CASCADE,limit_choices_to={'type':str(POINT_TYPE[0])},)
    B = models.ForeignKey(Point,verbose_name="Point B",related_name='B',on_delete=models.CASCADE,limit_choices_to={'type':POINT_TYPE[0]},)
    Vr = models.ForeignKey(Point,verbose_name="Direction Vector",related_name='Vr',on_delete=models.CASCADE,limit_choices_to={'type':POINT_TYPE[2]},)
    Nr = models.ForeignKey(Point,verbose_name="Normal Vector",related_name='Nr',on_delete=models.CASCADE,limit_choices_to={'type':POINT_TYPE[2]},)
    playground = models.ForeignKey(Playground,verbose_name="Playground",on_delete=models.CASCADE,)

    def isHitten(self, currentPosition, direction):
        #if p1-p2 hits edge return true
        #else return false
        pass
