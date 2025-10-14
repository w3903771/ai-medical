# 树结构工具
# 迁移自 py_tools.utils.tree_util.py
from typing import List, Dict, Any

def build_tree(data: List[Dict[str, Any]], id_key: str = 'id', parent_id_key: str = 'parent_id') -> List[Dict[str, Any]]:
    tree = []
    lookup = {item[id_key]: item for item in data}
    for item in data:
        parent_id = item.get(parent_id_key)
        if parent_id and parent_id in lookup:
            parent = lookup[parent_id]
            parent.setdefault('children', []).append(item)
        else:
            tree.append(item)
    return tree