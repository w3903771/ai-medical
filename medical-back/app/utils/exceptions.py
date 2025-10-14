# 异常工具
# 迁移自 py_tools.exceptions.base.py
class BizException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class NotFoundException(BizException):
    pass

class AuthException(BizException):
    pass