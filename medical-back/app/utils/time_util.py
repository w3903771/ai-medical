# 时间工具
# 迁移自 py_tools.utils.time_util.py
import datetime

def now() -> datetime.datetime:
    return datetime.datetime.now()

def format_datetime(dt: datetime.datetime, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    return dt.strftime(fmt)