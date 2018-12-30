"""
Definition of models.
"""

from django.db import models


class Point(models.Model):
    x = models.IntegerField(
        verbose_name="X-Value",
        related_name='x',
        on_delete=models.CASCADE,
        )
    y = models.IntegerField(
        verbose_name="Y-Value",
        related_name='y',
        on_delete=models.CASCADE,
        )

class Edge(models.Model):
    A = models.ForeignKey(
        Point,
        verbose_name="Point A",
        related_name='A',
        on_delete=models.CASCADE,
        )
    B = models.ForeignKey(
        Point,
        verbose_name="Point B",
        related_name='B',
        on_delete=models.CASCADE,
        )
    Vr = models.ForeignKey(
        Point,
        verbose_name="Direction Vector",
        related_name='Vr',
        on_delete=models.CASCADE,
        )
    N = models.ForeignKey(
        Point,
        verbose_name="Normal Vector",
        related_name='N',
        on_delete=models.CASCADE,
        )

    def calcNorm(self, edges):
        pass
    
    def isHitting(self, currentPosition, direction):
        #if p1-p2 hits edge return true
        #else return false
        pass

    def get_line_intersection(A1, A2, B1, B2):
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
                return point(0, 0)
        else:
            return point(0, 0)

    ################################## Plot Init

    def initAxes(self, _plt):
        self.axR = _plt.axes([0.25, 0.1 * self.ID, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        self.axT = _plt.axes([0.25, 0.05 + 0.1 * self.ID, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        
    def initSlider(self):
        self.R = Slider(self.axR, 'Radius_' + str(self.ID), 0.0, 20.0, valinit=5.0)
        self.T = Slider(self.axT, 'Theta_' + str(self.ID), 0.0, 4 * pi, valinit=pi/2)
    
    def update(self):
        self.plot.set_xdata([self.A.x, self.A.x + self.R.val * cos(self.T.val)])
        self.plot.set_ydata([self.A.y, self.A.y + self.R.val * sin(self.T.val)])

class Playground(models.Model):
    minX = models.IntegerField(
        verbose_name="Min X",
        related_name='minX',
        on_delete=models.CASCADE,
        )
    minY = models.IntegerField(
        verbose_name="Min Y",
        related_name='minY',
        on_delete=models.CASCADE,
        )
    maxX = models.IntegerField(
        verbose_name="Max X",
        related_name='maxX',
        on_delete=models.CASCADE,
        )
    maxY = models.IntegerField(
        verbose_name="Max Y",
        related_name='maxY',
        on_delete=models.CASCADE,
        )
    corners = models.ForeignKey(
        Point,
        verbose_name="Corners of Playground",
        related_name='corners',
        on_delete=models.CASCADE,
        )
    run_points = models.ForeignKey(
        Point,
        verbose_name="Running Points",
        related_name='run_points',
        on_delete=models.CASCADE,
        )
    edges = models.ForeignKey(
        Edge,
        verbose_name="Edges",
        related_name='edges',
        on_delete=models.CASCADE,
        )

    def catInit(self):
