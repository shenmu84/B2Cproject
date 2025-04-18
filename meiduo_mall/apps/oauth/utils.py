
from urllib.parse import urlencode, parse_qs
import json
import requests


class OAuthGITEE(object):
    """
    认证辅助工具类
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state   # 用于保存登录成功后的跳转页面路径

    def get_gitee_url(self):
        # 登录url参数组建
        data_dict = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }

        # 构建url
        gitee_url = 'https://gitee.com/oauth/authorize?' + urlencode(data_dict)

        return gitee_url

    # 获取access_token值
    def get_access_token(self, code):
        # 构建参数数据
        data_dict = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        # 构建url
        access_url = 'https://gitee.com/oauth/token?' + urlencode(data_dict)

        # 发送请求
        try:
            response = requests.post(access_url)

            # 提取数据
            # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14
            data = response.text

        except:
            raise Exception('请求失败')

        # 提取access_token db88
        data=json.loads(data)
        access_token = data.get('access_token', None)

        if not access_token:
            raise Exception('access_token获取失败')

        return access_token

    # 获取open_id值

    def get_open_id(self, access_token):

        # 构建请求url
        #https://gitee.com/api/v5/user?access_token='46ea64dd3bfe20a52e6753669f58289f'
        url = 'https://gitee.com/api/v5/user?access_token=' +access_token
#'ddeb0c2623c27e4d99281880f004f0a9'
        # 发送请求
        try:
            response = requests.get(url)

            # 提取数据
            data = response.text
        except:
            raise Exception('请求失败')
        # 转化为字典
        try:
            data_dict = json.loads(data)
            # 获取openid
            openid = data_dict.get('id')
            #unresolved attribute reference get for str
        except:
            raise Exception('openid获取失败')

        return openid
