
from enum import Enum

class ResultCode(Enum):
    SUCCESS = (200, "操作成功")
    FAILED = (500, "操作失败")
    VALIDATE_FAILED = (404, "参数检验失败")
    UNAUTHORIZED = (401, "暂未登录或token已经过期")
    FORBIDDEN = (403, "没有相关权限")

    def __init__(self, code, message):
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message


# 通用返回封装方法
def common_result(code_enum: ResultCode, data=None):
    return {
        "code": code_enum.code,
        "message": code_enum.message,
        "data": data
    }
