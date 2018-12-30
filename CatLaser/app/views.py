"""
Definition of views.
"""
from django.core import serializers
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

from .models import Point, POINT_TYPE

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    points = Point.objects.all().order_by('type')
    json_serializer = serializers.get_serializer('json')()
    points_json = json_serializer.serialize(points,ensure_ascii=False)
    point_types = POINT_TYPE

    return render(
        request,
        'app/index.html',
        {
            'title':'Cat-Laser-Config',
            'year':datetime.now().year,
            'points': points_json,
            'point_types': point_types,
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
