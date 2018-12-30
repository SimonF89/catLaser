from django.contrib import admin

from .models import Point, Edge, Playground
from .forms import EdgeForm, PlaygroundForm


class EdgeAdmin(admin.ModelAdmin):
    form = EdgeForm

class PlaygroundAdmin(admin.ModelAdmin):
    form = PlaygroundForm

# Registered models
admin.site.register(Point)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(Playground, PlaygroundAdmin)