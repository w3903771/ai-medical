# 序列化工具
# 迁移自 py_tools.utils.serializer_util.py
import json
from typing import Any

def to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)

def from_json(data: str) -> Any:
    return json.loads(data)