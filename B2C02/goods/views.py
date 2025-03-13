from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render
from goods.models import GoodInfo
def index(request):
    books=GoodInfo.objects.all()
    print(books)
    return HttpResponse("Hello, world. You're at the polls index.")
# Create your views here.
'''
增加数据
'''
#方式一
from goods.models import GoodInfo
book=GoodInfo(
    name='Django',
    pub_date='2000-1-1',
    readcount=10
)
book.save()

#方式二
GoodInfo.objects.create(
    name="测试卡法入门",
    pub_date="2000-1-1",
    readcount=100
)
'''
修改数据
'''
#方式一
book=GoodInfo.objects.get(id=2)
book.name="运维开发"

#方式2
GoodInfo.objects.filter(id=3).update(name="爬虫入门",commentcount=666)
'''
删除数据
'''
#物理删除delete()和逻辑删除
book=GoodInfo.objects.get(id=2)
book.delete()
GoodInfo.objects.filter(id=2).delete()

'''
查询
'''
#查询一个
try:
    book=GoodInfo.objects.get(id=2)
except GoodInfo.DoesNotExist:
    print("GoodInfo.DoesNotExist")

#查询多个
GoodInfo.objects.all()
'''
过滤查询
id=1
包含某个字
以X字结尾
书名为空
id在几个范围之内的
id大于3，小于3
great gt
litte lt
id不等于3

'''
GoodInfo.objects.get(id=1)#id=pk=primary key
GoodInfo.objects.filter(name_contains="爬")
GoodInfo.objects.filter(name_endswith="程")
GoodInfo.objects.filter(name_isnull=True)
GoodInfo.objects.get(id_in=[1,3,5])
GoodInfo.objects.filter(id_gt=3)
GoodInfo.objects.exclude(id=3)

'''
F对象
'''
from django.db.models import F, Q

#阅读量大于评论量
GoodInfo.objects.filter(readcount_gte=F('commentcount'))
#并且查询
GoodInfo.objects.filter(readcount_gt=20).filter(id_lt=3)
GoodInfo.objects.filter(readcount_gt=20,id_lt=3)#上下等价
#或者查询
GoodInfo.objects.filter(Q(readcount_gt=20) | Q(readcount_lt=20)|Q(readcount_gt=20))
#并且查询
GoodInfo.objects.filter(Q(readcount_gt=20) | Q(readcount_lt=20)& Q(readcount_gt=20))
#非
GoodInfo.objects.filter(~Q(readcount_gt=20))