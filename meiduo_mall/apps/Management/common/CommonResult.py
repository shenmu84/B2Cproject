
from .ResultCode import ResultCode


class CommonResult:
    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.message = message
        self.data = data

    @classmethod
    def success(cls, data=None, message=None):
        """成功返回结果"""
        msg = message if message else ResultCode.SUCCESS.message
        return cls(ResultCode.SUCCESS.code, msg, data)

    @classmethod
    def failed(cls, message=None, error_code=None):
        """失败返回结果"""
        if error_code:
            return cls(error_code.code, message or error_code.message, None)
        return cls(ResultCode.FAILED.code, message or ResultCode.FAILED.message, None)

    @classmethod
    def validate_failed(cls, message=None):
        """参数验证失败返回结果"""
        return cls(ResultCode.VALIDATE_FAILED.code,
                   message or ResultCode.VALIDATE_FAILED.message, None)

    @classmethod
    def unauthorized(cls, data=None):
        """未登录返回结果"""
        return cls(ResultCode.UNAUTHORIZED.code,
                   ResultCode.UNAUTHORIZED.message, data)

    @classmethod
    def forbidden(cls, data=None):
        """未授权返回结果"""
        return cls(ResultCode.FORBIDDEN.code,
                   ResultCode.FORBIDDEN.message, data)

    def to_dict(self):
        """将结果对象转为字典返回给前端"""
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }
