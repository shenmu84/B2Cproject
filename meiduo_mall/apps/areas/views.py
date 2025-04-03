from django.views import View
from apps.areas.models import Area
from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
# Create your views here.
class AreasView(View):
    def get(self, request):
        province=cache.get('province')
        if province is None:
            provinces = Area.objects.filter(parent__isnull=True)
            province=[]
            for i in provinces:
                province.append({'id':i.id,'name':i.name})
            cache.set('province',province,24*60*60)
        return JsonResponse({'code':0,'errmsg':'ok','province_list':province})
class SubAreasView(View):
    def get(self, request,id):
        city=cache.get('city%s'%id)
        if city is None:
            parent=Area.objects.get(id=id)
            child=parent.subs.all()
            city=[]
            for i in child:
                city.append({'id':i.id,'name':i.name})
                cache.get('city%s'%id,24*60*60)
        return JsonResponse({'code':0,'errmsg':'ok','sub_data':{'subs':city}})
