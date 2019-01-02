"""
Definition of views.
"""
from django.core import serializers
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

from .models import Playground, PointTypes

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    playgrounds = Playground.objects.all().order_by('name')
    json_serializer = serializers.get_serializer('json')()
    playgrounds_json = json_serializer.serialize(playgrounds, ensure_ascii=False)
    point_types = PointTypes.CHOICES

    print(playgrounds_json)

    return render(
        request,
        'app/index.html',
        {
            'title':'Cat-Laser-Config',
            'year':datetime.now().year,
            'playgrounds': playgrounds,
            'playgrounds_json': playgrounds_json,
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
