from django.contrib import admin

from .models import Point, Edge, Playground, PointTypes
from .forms import EdgeForm



class PointInline(admin.TabularInline):
    model = Point
    extra = 0
    min_num = 3

    def get_queryset(self, request):
        qs = super(PointInline, self).get_queryset(request)
        return qs.filter(type=PointTypes.corner) | qs.filter(type=PointTypes.run_point)
    
class EdgeInline(admin.TabularInline):
    model = Edge
    readonly_fields = ["A", "B", "M", "Vr", "Nr"]
    extra = 0

class PlaygroundAdmin(admin.ModelAdmin):
    search_fields = ['name']
    readonly_fields = ('active','minX','minY','maxX','maxY')
    list_display = ('name','active','minX','minY','maxX','maxY')
    inlines = [PointInline,EdgeInline]

    def response_add(self, request, playground_obj):
        playground_obj.customInit(playground_obj)
        return super(PlaygroundAdmin, self).response_add(request, playground_obj)

    def response_change(self, request, playground_obj):
        playground_obj.customInit(playground_obj)
        return super(PlaygroundAdmin, self).response_change(request, playground_obj)

class EdgeAdmin(admin.ModelAdmin):
    form = EdgeForm

# Registered models
admin.site.register(Point)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(Playground, PlaygroundAdmin)


#http://igorsobreira.com/2011/02/12/change-object-after-saving-all-inlines-in-django-admin.html
#class FooAdmin(admin.ModelAdmin):
#    inlines = [RelatedInline]

#    def response_add(self, request, new_object):
#        obj = self.after_saving_model_and_related_inlines(new_object)
#        return super(FooAdmin, self).response_add(request, obj)

#    def response_change(self, request, obj):
#        obj = self.after_saving_model_and_related_inlines(obj)
#        return super(FooAdmin, self).response_change(request, obj)

#    def after_saving_model_and_related_inlines(self, obj):
#        print obj.related_set.all()
#        # now we have what we need here... :)
#        return obj





#class StepInline(admin.TabularInline):
#    """Choice objects can be edited inline in the Poll editor."""
#    model = Step
#    extra = 3
#
#
#class TodoAdmin(admin.ModelAdmin):
#    """Definition of the Poll editor."""
#    fieldsets = [
#        (None, {'fields': ['name', 'description', 'status']}),
#        ('Date information', {'fields': ['creationDate']}),
#        ('Additional Information', {'fields': ['author', 'executor', 'reviewer']})
#    ]
#    inlines = [StepInline]
#    list_display = ('name', 'description', 'status', 'creationDate', 'author', 'executor', 'reviewer')
#    list_filter = ['creationDate']
#    search_fields = ['name']
#    date_hierarchy = 'creationDate'
#
#admin.site.register(Todo, TodoAdmin)






