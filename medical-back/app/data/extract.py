# 读取category.json文件
import os
import numpy as np
import json

# 切换目录到代码所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# unique list
name_list_category = []

with open(r'category.json', 'r', encoding='utf-8') as f:
    data = json.load(f)['categories']
    # 打印所有的类别名称
    for category in data:
        members = category['indicators']
        for member in members:
            name_list_category.append(member['name_cn'])

name_list_category = np.unique(name_list_category)

# order by name
name_list_category = sorted(name_list_category)
print(name_list_category)

# save
with open(r'category_names.json', 'w', encoding='utf-8') as f:
    json.dump(name_list_category, f, ensure_ascii=False, indent=4)


# unique list
name_list_indicator = []

with open(r'indicators.json', 'r', encoding='utf-8') as f:
    data = json.load(f)['indicators']
    # 打印所有的类别名称
    for indicator in data:
        name = indicator['name_cn']
        name_list_indicator.append(name)

name_list_indicator = np.unique(name_list_indicator)

# order by name
name_list_indicator = sorted(name_list_indicator)

diff = set(name_list_category) - set(name_list_indicator)

diff = list(diff)   

# save
with open(r'indicator_names_implement.json', 'w', encoding='utf-8') as f:
    json.dump(diff, f, ensure_ascii=False, indent=4)
