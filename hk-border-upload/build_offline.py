#!/usr/bin/env python3
"""
将 data.json 打包进 index.html，生成独立离线版本 index-offline.html
双击即可打开，无需本地 HTTP 服务器
"""
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))

# 读取 data.json
with open(os.path.join(DIR, 'data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取 index.html
with open(os.path.join(DIR, 'index.html'), 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 把 `let DATA = {};` 替换为内联数据
old_init = "let DATA = {};"
new_init = f"let DATA = {json.dumps(data, ensure_ascii=False, separators=(',', ':'))};"

if old_init in html:
    html = html.replace(old_init, new_init)
else:
    # 备份：如果没找到精确匹配
    html = re.sub(r'let\s+DATA\s*=\s*\{\s*\};', new_init, html)

# 2. 删除 fetch 数据加载块
fetch_block = """// 先尝试加载一次，失败则用轮询
fetch('data.json?_v=2&_t='+Date.now(),{cache:'no-store'})
  .then(function(r) { return r.json(); })
  .then(function(d) {
    DATA = d;
    tryRender();
  })
  .catch(function() { tryRender(); });"""

if fetch_block in html:
    html = html.replace(fetch_block, "// offline: data embedded\ntryRender();")
else:
    # fallback with regex
    pattern = r"fetch\('data\.json[^']*'\)[\s\S]*?\.catch\(function\(\)\s*\{\s*tryRender\(\);\s*\}\);"
    html = re.sub(pattern, "// offline: data embedded\ntryRender();", html)

# 写入 index-offline.html
output_path = os.path.join(DIR, 'index-offline.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

file_size = os.path.getsize(output_path) / 1024 / 1024
print(f"Generated: {output_path}")
print(f"Size: {file_size:.2f} MB")
