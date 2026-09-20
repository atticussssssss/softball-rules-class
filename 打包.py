# -*- coding: utf-8 -*-
"""把仓库打包成发给自己 Windows 电脑用的压缩包：python3 打包.py

生成 慢投垒球规则课.zip，顶层是一个 慢投垒球规则课/ 文件夹。
每个条目都带 UTF-8 文件名标志，Win10/11 资源管理器解压后中文名不会乱码。
存档/ 不打进去。
"""
import os, zipfile

ROOT = '慢投垒球规则课'
ITEMS = [
    ('放映台.html',   '放映台.html'),
    ('使用说明.txt',  '使用说明.txt'),
    ('规则课大纲.md', '规则课大纲.md'),
]
DIRS = ['课后发给队员', '单页']

out = '慢投垒球规则课.zip'
if os.path.exists(out):
    os.remove(out)

z = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
n = 0
for src, dst in ITEMS:
    z.write(src, os.path.join(ROOT, dst)); n += 1
for d in DIRS:
    for fn in sorted(os.listdir(d)):
        if fn.startswith('.'):
            continue
        z.write(os.path.join(d, fn), os.path.join(ROOT, d, fn)); n += 1
z.close()

bad = [i.filename for i in zipfile.ZipFile(out).infolist() if not i.flag_bits & 0x800]
print('%s 已生成，%d 个文件，%.0f KB' % (out, n, os.path.getsize(out) / 1024.0))
if bad:
    print('警告：以下条目缺 UTF-8 文件名标志：', bad)
