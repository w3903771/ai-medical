# JWT 工具
# 迁移自 py_tools.utils.jwt_util.py
# 用于生成和校验 JWT Token

import jwt
import datetime
from typing import Any, Dict

SECRET_KEY = 'your-secret-key'  # 请根据实际项目配置调整
ALGORITHM = 'HS256'


def create_jwt_token(user_id: int, expire_minutes: int = 10) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expire_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token已过期')
    except jwt.InvalidTokenError:
        raise Exception('无效Token')