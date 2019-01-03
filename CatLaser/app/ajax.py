from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Playground

@csrf_exempt
def change_active(request):

    activePlayground_name = request.POST.get("playground_name", None)

    print("got new_status: " + str(activePlayground_name))

    playgrounds = Playground.objects.all()

    for playground in playgrounds:
        if playground.name == activePlayground_name:
            playground.active = True
        else:
            playground.active = False
        playground.save()

    data = {}
    return JsonResponse(data)

