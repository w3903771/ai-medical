# 读取category.json文件
import os
import numpy as np
import json

# 切换目录到代码所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# unique list
name_list = []

with open(r'category.json', 'r', encoding='utf-8') as f:
    data = json.load(f)['categories']
    # 打印所有的类别名称
    for category in data:
        members = category['members']
        for member in members:
            name_list.append(member['name_cn'])

name_list = np.unique(name_list)

# order by name
name_list = sorted(name_list)
print(name_list)

# save
with open(r'category_names.json', 'w', encoding='utf-8') as f:
    json.dump(name_list, f, ensure_ascii=False, indent=4)
