from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
#接受请求，给予相应
def index(request):
    #对指定的请求添加对应的模板，这里是具体的模板名字
    context={
        'name':'测试'
    }
    return render(request, "goods/index.html",context=context)