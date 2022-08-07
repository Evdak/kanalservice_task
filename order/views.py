from django.shortcuts import render
from django.http import HttpRequest, JsonResponse

from .services.services import refresh_file
from order.models import Order

import json


def index(request: HttpRequest):
    refresh_file()
    return render(request, 'index.html', {"data": Order.objects.all().order_by('pk')})
