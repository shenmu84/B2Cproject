from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_mall import settings

#加密
def makeToken(openid,expires_in):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=expires_in)
    access_token = s.dumps({'openid': openid})
    # 将bytes类型的数据转换为 str
    return access_token.decode()
# 解密
def checkToken(token,expires_in):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=expires_in)
    try:
        result=s.loads(token)
    except Exception:
        return None
    else:
        return result.get('openid')