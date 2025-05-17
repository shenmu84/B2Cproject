import pickle
import base64
from django_redis import get_redis_connection



def getCartFromCook(request):
    cookie_carts = request.COOKIES.get('carts')
    if cookie_carts is not None:
        # 对加密的数据解密
        try:
            return  pickle.loads(base64.b64decode(cookie_carts))
        except:
            return {}
    else:
        # 有cookie字典
        return {}
def setCartToCookie(response, carts, max_age=14*24*3600):
    encoded = base64.b64encode(pickle.dumps(carts)).decode()
    response.set_cookie('carts', encoded, max_age=max_age)
    return response

def merge_cookie_to_redis(request,response):
    carts=getCartFromCook(request)
    if carts is not None and carts != {}:
        countDict,selected,unselected = {},[],[]
        # TODO 执行这里出错
        for sku_id,dict in carts.items():
            countDict[sku_id]=dict.get('count')
            if dict.get('selected'):
                selected.append(sku_id)
            else:
                unselected.append(sku_id)
        user=request.user
        redis_cli=get_redis_connection('carts')
        pipeline=redis_cli.pipeline()
        pipeline.hmset('carts_%s'%user.id,countDict)
        if len(selected) > 0:
            # *selected_ids  对列表数据进行解包
            pipeline.sadd('selected_%s' % user.id, *selected)
        # unselected_id [4,5,6]
        if len(unselected) > 0:
            pipeline.srem('selected_%s' % user.id, *unselected)
        pipeline.execute()
        response.delete_cookie('carts')
    return response