# 数据脱敏工具
# 迁移自 py_tools.utils.mask_util.py

def mask_phone(phone: str) -> str:
    if len(phone) == 11:
        return phone[:3] + '****' + phone[-4:]
    return phone

def mask_id_card(id_card: str) -> str:
    if len(id_card) == 18:
        return id_card[:6] + '********' + id_card[-4:]
    return id_card