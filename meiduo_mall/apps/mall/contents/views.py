from django.shortcuts import render
from django.views import View

from apps.mall.contents.models import ContentCategory


# Create your views here.
class IndexView(View):
    def get(self, request):
        # 广告
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key]=cat.content_set.filter(status=True).order_by('sequence')
        context = {
            'categories': content_categories,
            'contents': contents,
        }
        return render(request,'index.html',context)