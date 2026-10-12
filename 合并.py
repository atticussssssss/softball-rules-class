# -*- coding: utf-8 -*-
"""把速查卡和自学版合成一个文件：python3 合并.py

生成 慢投垒球规则-给队员.html —— 发群里的那一个。
打开先是速查卡（赶时间就看这一屏），往下是完整规则和动画。
速查卡的 CSS 全部加 #card 前缀作用域，再加一道栅栏挡住自学版的
通用元素样式（section、h2、p 那些）漏进卡片。
"""
import io, re

CARD  = '课后发给队员/速查卡.html'
STUDY = '课后发给队员/慢投垒球规则课.html'
OUT   = '慢投垒球规则-给队员.html'
SCOPE = '#card'

FONTS = ('https://fonts.googleapis.com/css2?'
         'family=Archivo:wght@400;500;600;700;800;900'
         '&family=Noto+Sans+SC:wght@400;500;700;900'
         '&family=Noto+Serif+SC:wght@400;600&display=swap')


def split_head(src):
    """拆成 (<style> 里的 CSS, </style> 之后的正文)"""
    i = src.index('<style>') + len('<style>')
    j = src.index('</style>')
    return src[i:j], src[j + len('</style>'):]


def scope(css, pre):
    """给每条规则的选择器加前缀。@media 递归处理，@page 原样留着。"""
    out, i, n = [], 0, len(css)
    while i < n:
        br = css.find('{', i)
        if br < 0:
            out.append(css[i:]); break
        head = css[i:br].strip()

        if head.startswith('@'):
            name = head.split()[0] if head.split() else head
            # 找到配对的右花括号
            depth, k = 1, br + 1
            while k < n and depth:
                if css[k] == '{': depth += 1
                elif css[k] == '}': depth -= 1
                k += 1
            body = css[br + 1:k - 1]
            if name in ('@media', '@supports'):
                out.append('%s{%s}' % (head, scope(body, pre)))
            else:                      # @page / @keyframes / @font-face 原样
                out.append('%s{%s}' % (head, body))
            i = k
            continue

        end = css.find('}', br)
        body = css[br + 1:end]
        sels = []
        for one in [s.strip() for s in head.split(',') if s.strip()]:
            if one in (':root', 'body', 'html'):
                sels.append(pre)
            elif one == '*':
                sels.append(pre + ' *')
            elif one.startswith('body'):
                sels.append(pre + one[4:])
            elif one.startswith('html'):
                sels.append(pre + one[4:])
            else:
                sels.append(pre + ' ' + one)
        out.append('%s{%s}' % (','.join(sels), body))
        i = end + 1
    return '\n'.join(out)


card_css,  card_body  = split_head(io.open(CARD,  encoding='utf-8').read())
study_css, study_body = split_head(io.open(STUDY, encoding='utf-8').read())

# 正文切成 masthead / shell+footer / script 三段
m = re.search(r'(<header class="masthead">.*?</header>)(.*?)(<script>.*)',
              study_body, re.S)
masthead, shell, study_script = m.group(1), m.group(2), m.group(3)

# 目录栏最前面插一条「速查卡」
shell = shell.replace('<li><a href="#s1">',
                      '<li><a href="#card"><i>00</i>速查卡</a></li>\n      <li><a href="#s1">', 1)

card_script = re.search(r'<script>(.*?)</script>', card_body, re.S).group(1)
card_body   = re.sub(r'<script>.*?</script>', '', card_body, flags=re.S).strip()

FENCE = """
/* 栅栏：自学版的通用元素样式（section、h2、p 那些）不要漏进速查卡。
   必须排在速查卡样式之前 —— 同权重时后面的赢。 */
#card h1,#card h2,#card h3,#card h4,#card p,#card ul,#card ol,#card li,
#card section,#card div{
  margin:0;padding:0;border:0;background:none;color:inherit;font:inherit;
  letter-spacing:normal;text-transform:none;text-wrap:wrap;scroll-margin-top:0
}
#card ul,#card ol{list-style:none}
#card a{color:inherit;text-decoration:none}
"""

GLUE = """
/* 卡片外壳与跳转条 */
#card{max-width:62rem;margin:0 auto;scroll-margin-top:8px}
#jump{max-width:62rem;margin:0 auto 6px;padding:0 1.4rem 1.6rem;
  display:flex;align-items:center;gap:.7rem;
  font-family:var(--font-ui);font-size:.86rem;color:var(--ink-3)}
#jump a{color:var(--turf);font-weight:700;text-decoration:none;
  border-bottom:1px solid var(--turf-soft);padding-bottom:1px}
#jump a:hover{border-bottom-color:var(--turf)}
#jump hr{flex:1;border:0;border-top:1px solid var(--line);margin:0}
@media (max-width:820px){ #jump{padding:0 .8rem 1.2rem} }

/* 打印时只出速查卡 */
@media print{
  .masthead,.shell,footer,#jump{display:none!important}
  #card{max-width:none}
}
"""

OUTDOC = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>慢投垒球规则 · 给队员</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="%s">

<style>
/* ========== 自学版样式（原样） ========== */
%s
%s
%s
/* ========== 速查卡样式（作用域 #card） ========== */
%s
</style>

%s

<div id="card">
%s
</div>

<div id="jump">
  <hr><a href="#s1">往下是完整规则，一条一条讲 ↓</a><hr>
</div>

%s

%s
<script>
%s
</script>
""" % (FONTS, study_css, FENCE, GLUE, scope(card_css, SCOPE),
       masthead, card_body, shell, study_script, card_script)

io.open(OUT, 'w', encoding='utf-8').write(OUTDOC)
print('%s 已生成，%.0f KB' % (OUT, len(OUTDOC.encode('utf-8')) / 1024.0))
