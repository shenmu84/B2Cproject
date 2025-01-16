from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
#接受请求，给予相应
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
# Create your views here.
