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
    ('慢投垒球规则-给队员.html', '慢投垒球规则-给队员.html'),
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

# ---- 发群版：只装队员要看的，不含大纲、单页、放映台 ----
SEND = '慢投垒球规则-发群.zip'
SEND_ROOT = '慢投垒球规则'
SEND_ITEMS = [
    ('慢投垒球规则-给队员.html',     '慢投垒球规则.html'),
    ('课后发给队员/速查卡.html',     '速查卡.html'),
    ('怎么看.txt',                   '怎么看.txt'),
]
if os.path.exists(SEND):
    os.remove(SEND)
zs = zipfile.ZipFile(SEND, 'w', zipfile.ZIP_DEFLATED)
for src, dst in SEND_ITEMS:
    zs.write(src, os.path.join(SEND_ROOT, dst))
zs.close()
print('%s 已生成，%d 个文件，%.0f KB' % (SEND, len(SEND_ITEMS), os.path.getsize(SEND) / 1024.0))

bad = [i.filename for i in zipfile.ZipFile(out).infolist() if not i.flag_bits & 0x800]
bad += [i.filename for i in zipfile.ZipFile(SEND).infolist() if not i.flag_bits & 0x800]
print('%s 已生成，%d 个文件，%.0f KB' % (out, n, os.path.getsize(out) / 1024.0))
if bad:
    print('警告：以下条目缺 UTF-8 文件名标志：', bad)
