from unicodedata import category

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
#导入图片
#from fdfs_client.client import Fdfs_client
#client=Fdfs_client('utils/fastdfs/client.conf')
#client.upload_by_filename('/home/B2Cproject/meiduo_mall/static/images/logo.png')


from django.shortcuts import render
from django.views import View

from apps.contents.models import ContentCategory
from apps.goods.models import GoodsCategory

from utils.goods import get_categories
# Create your views here.
class IndexView(View):
    def get(self, request):
        # 1.商品分类数据
        categories = get_categories()
        # 2.广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key]=cat.content_set.filter(status=True).order_by('sequence')
        context = {
            'categories':categories,
            'contents': contents,
        }
        return render(request,'index.html',context)
from utils.goods import get_breadcrumb
from apps.goods.models import SKU
class ListView(View):
    def get(self, request,category_id):
        # 1.接收参数
        # 排序字段
        ordering = request.GET.get('ordering')
        # 每页多少条数据
        page_size = request.GET.get('page_size')
        # 要第几页数据
        page = request.GET.get('page')
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        breadcrumbs = get_breadcrumb(category)
        # 5.查询分类对应的sku数据，然后排序，然后分页
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)
        #分页
        from django.core.paginator import Paginator
        paginator = Paginator(skus, page_size)
        page_skus=paginator.page(page)
        sku_list=[]
        for sku in page_skus.object_list:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            }
            )
        total_num=paginator.num_pages
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'list': sku_list, 'count': total_num, 'breadcrumb': breadcrumbs})

class HotView(View):
    def get(self,request,category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'参数缺失'})
        hot_skus = SKU.objects.filter(category=category, is_launched=True).order_by('-sales')[:2]
        hot_goods_data = []
        for sku in hot_skus:
            hot_goods_data.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })

        return  JsonResponse({'code': 0, 'errmsg': 'ok', 'hot_skus': hot_goods_data})
from haystack.views import SearchView
from django.http import JsonResponse
from haystack.views import SearchView
from django.http import JsonResponse


class SKUSearchView(SearchView):

    def create_response(self):
        # 获取搜索的结果
        context = self.get_context()
        # 我们该如何知道里边有什么数据呢？？？
        # 添加断点来分析
        sku_list=[]
        for sku in context['page'].object_list:
            sku_list.append({
                'id':sku.object.id,
                'name':sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url,
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count
            })

        return JsonResponse(sku_list,safe=False)
