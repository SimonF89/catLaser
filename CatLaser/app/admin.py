from django.contrib import admin

from .models import Point, Edge, Playground
from .forms import EdgeForm, PlaygroundForm


class PointInline(admin.TabularInline):
    """Choice objects can be edited inline in the Poll editor."""
    model = Point
    extra = 3

class EdgeAdmin(admin.ModelAdmin):
    form = EdgeForm

class PlaygroundAdmin(admin.ModelAdmin):
    form = PlaygroundForm
   # inlines = [PointInline]

# Registered models
admin.site.register(Point)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(Playground, PlaygroundAdmin)