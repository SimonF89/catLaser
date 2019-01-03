"""
Definition of views.
"""
from django.core import serializers
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

from .models import Playground, Edge, Point, PointTypes

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    point_types = PointTypes.CHOICES

    data = []
    playgrounds = Playground.objects.all().order_by('name')

    for playground in playgrounds:
        data.append({
            "ID":playground.id,
            "active":playground.active,
            "name":playground.name,
            "minX":playground.minX,
            "maxX":playground.maxX,
            "minY":playground.minY,
            "maxY":playground.maxY,
            "edges":[],
            "run_points":[],
            })
        for edge in playground.edges:
            data[-1]["edges"].append({
                "ID":edge.id,
                "A":{
                    "x":edge.A.x,
                    "y":edge.A.y,
                    },
                "B":{
                    "x":edge.B.x,
                    "y":edge.B.y,
                    },
                "M":{
                    "x":edge.M.x,
                    "y":edge.M.y,
                    },
                "Vr":{
                    "x":edge.Vr.x,
                    "y":edge.Vr.y,
                    },
                "Nr":{
                    "x":edge.Nr.x,
                    "y":edge.Nr.y,
                    },
            })
        for runPoint in playground.run_points:
            data[-1]["run_points"].append({
                "ID":runPoint.id,
                "x":runPoint.x,
                "y":runPoint.y,
            })

    return render(
        request,
        'app/index.html',
        {
            'title':'Cat-Laser-Config',
            'year':datetime.now().year,
            'playgrounds': playgrounds,
            'point_types': point_types,
            'data':data,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
