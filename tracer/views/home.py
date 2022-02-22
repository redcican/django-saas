from django.shortcuts import redirect, render
from tracer import models


def index(request):
    return render(request, 'index.html')


def price(request):
    price_list = models.PricePolicy.objects.filter(category=2)
    return render(request, 'price.html',{'price_list': price_list})
