# -*- coding: utf-8 -*-
"""把四个页面合并成单文件的放映台。改过任何一页之后重跑：python3 build_console.py"""
import re, io

PAGES = [
    ('pane1', '开场.html',           '开场',          '一场比赛怎么进行'),
    ('pane2', '双方基础.html',       '双方基础',      '被迫、封杀触杀、补踩'),
    ('pane3', '打者眼中的球场.html', '打者眼中的球场', '站在本垒看全场'),
    ('pane4', '打席.html',           '打席',          '从投球到结果'),
    ('pane5', '情景.html',           '情景',          '十三个情景，两边怎么做'),
    ('pane6', '单方面补充.html',     '单方面补充',    '守备独有、跑者独有'),
    ('pane7', '场上场下.html',       '场上场下',      '手势、死球、联赛规则'),
    ('pane8', '收尾.html',           '收尾',          '下场前三件事'),
]

def split_blocks(css):
    out, i, n, start = [], 0, len(css), 0
    while i < n:
        if css[i] == '{':
            sel = css[start:i]
            depth, j = 1, i + 1
            while j < n and depth:
                if css[j] == '{': depth += 1
                elif css[j] == '}': depth -= 1
                j += 1
            out.append((sel, css[i+1:j-1]))
            i = start = j
        else:
            i += 1
    return out

def scope_css(css, root):
    parts = []
    for sel, body in split_blocks(css):
        s = sel.strip()
        if s.startswith('@keyframes') or s.startswith('@font-face'):
            parts.append(s + '{' + body + '}')
        elif s.startswith('@media') or s.startswith('@supports'):
            if 'max-width' in s:      # 各页的窄屏排版在放映台里会让列表塌成零高度，去掉
                continue
            parts.append(s + '{' + scope_css(body, root) + '}')
        else:
            sels = []
            for one in s.split(','):
                one = one.strip()
                if not one: continue
                if one in (':root', 'html', 'body'): sels.append(root)
                elif one == '*': sels.append(root + ',' + root + ' *')
                elif one.startswith(':root'): sels.append(root + one[5:])
                elif one.startswith('body'): sels.append(root + one[4:])
                elif one.startswith('html'): sels.append(root + one[4:])
                else: sels.append(root + ' ' + one)
            parts.append(','.join(sels) + '{' + body + '}')
    return '\n'.join(parts)

PROXY = """
  var __root=window.document.getElementById('%s');
  var __live=function(){ return __root.classList.contains('on'); };
  var document={
    getElementById:function(id){ return __root.querySelector('[id="'+id+'"]'); },
    querySelector:function(s){ return __root.querySelector(s); },
    querySelectorAll:function(s){ return __root.querySelectorAll(s); },
    createElement:function(t){ return window.document.createElement(t); },
    createElementNS:function(ns,t){ return window.document.createElementNS(ns,t); },
    createTextNode:function(t){ return window.document.createTextNode(t); },
    addEventListener:function(type,fn,opt){
      window.document.addEventListener(type,function(e){ if(__live()) fn(e); },opt);
    }
  };
"""

styles, bodies, scripts = [], [], []
for pid, fn, title, sub in PAGES:
    src = io.open(fn, encoding='utf-8').read()
    css = src.split('<style>')[1].split('</style>')[0]
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    styles.append('/* ===== %s ===== */\n%s' % (title, scope_css(css, '#' + pid)))
    markup = src.split('</style>')[1].split('<script>')[0].strip()
    bodies.append('<section class="pane" id="%s">\n%s\n</section>' % (pid, markup))
    js = src.split('<script>')[1].split('</script>')[0]
    js = js.replace('"use strict";', '"use strict";' + (PROXY % pid), 1)
    scripts.append('<script>%s</script>' % js)

menu = '\n'.join(
    '    <button class="item" data-i="%d" aria-current="%s">\n'
    '      <i>%d</i><span><b>%s</b><small>%s</small></span>\n'
    '    </button>' % (k, 'true' if k == 0 else 'false', k + 1, t, sub)
    for k, (pid, fn, t, sub) in enumerate(PAGES))

TPL = u'''<meta charset="utf-8">
<title>规则课放映台</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&family=Noto+Sans+SC:wght@400;500;700;900&family=Noto+Serif+SC:wght@400&display=swap">

<style>
html{font-size:clamp(13px, 0.52vw + 0.78vh, 19px)}
*{box-sizing:border-box}
html,body{height:100%;margin:0;overflow:hidden}
body{
  display:grid;grid-template-columns:16rem minmax(0,1fr);
  background:#F3F4EE;color:#1A2119;
  font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif;
  -webkit-font-smoothing:antialiased
}
#nav{background:#E8EBE1;border-right:1px solid #CBD1C1;display:flex;flex-direction:column;min-height:0;overflow:auto}
#nav .brand{padding:1.3rem 1.2rem 1rem}
#nav .brand small{display:block;font-family:'Archivo','Noto Sans SC',sans-serif;font-size:.66rem;font-weight:700;letter-spacing:.2em;color:#B4573C;margin-bottom:.2rem}
#nav .brand b{font-family:'Archivo','Noto Sans SC',sans-serif;font-weight:900;font-size:1.15rem;line-height:1.25;letter-spacing:-.01em}
#menu{display:flex;flex-direction:column;flex:0 0 auto;gap:.3rem;padding:.8rem .7rem 1rem;border-top:1px solid #CBD1C1}
.item{display:grid;grid-template-columns:1.7rem 1fr;gap:.6rem;align-items:start;text-align:left;
  font-family:inherit;background:transparent;border:1px solid transparent;border-radius:4px;padding:.7rem;cursor:pointer;color:#4B564A}
.item i{font-style:normal;font-family:'Archivo',sans-serif;font-weight:900;font-size:.8rem;
  width:1.7rem;height:1.7rem;border-radius:50%;display:grid;place-items:center;background:#CBD1C1;color:#4B564A}
.item b{display:block;font-family:'Archivo','Noto Sans SC',sans-serif;font-weight:800;font-size:1.02rem;line-height:1.3;color:#1A2119}
.item small{display:block;font-size:.8rem;color:#7A8477;line-height:1.45;margin-top:.15rem}
.item:hover{background:#FFFFFF;border-color:#CBD1C1}
.item[aria-current="true"]{background:#FFFFFF;border-color:#1F5E36}
.item[aria-current="true"] i{background:#1F5E36;color:#FFFFFF}
#nav .foot{margin-top:auto;padding:.9rem 1.2rem 1.1rem;border-top:1px solid #CBD1C1;font-family:'Archivo','Noto Sans SC',sans-serif;font-size:.72rem;color:#7A8477;line-height:1.7}
#nav .foot kbd{font-family:'Archivo',sans-serif;font-size:.7rem;border:1px solid #CBD1C1;border-radius:3px;padding:.05rem .35rem;background:#F3F4EE;color:#4B564A;margin-right:.2rem}
#panes{position:relative;min-width:0}
.pane{position:absolute;inset:0;display:none;overflow:hidden}
.pane.on{display:block}
@media (max-width:860px){
  html,body{overflow:auto;height:auto}
  body{grid-template-columns:minmax(0,1fr)}
  #nav{border-right:0;border-bottom:1px solid #CBD1C1;overflow:visible}
  .item{flex:0 0 auto}
  #nav .foot{margin-top:0}
  #panes{height:88vh;min-height:520px}
}

@@STYLES@@
</style>

<nav id="nav">
  <div class="brand">
    <small>慢投垒球</small>
    <b>新队员规则课</b>
  </div>
  <div id="menu">
@@MENU@@
  </div>
  <div class="foot"><kbd>Option</kbd>加数字 切换页面<br>各页的播放和翻页按键不变</div>
</nav>

<main id="panes">
@@PANES@@
</main>

<script>
(function(){
  "use strict";
  var items=Array.prototype.slice.call(document.querySelectorAll('.item'));
  var panes=Array.prototype.slice.call(document.querySelectorAll('.pane'));
  function show(i){
    items.forEach(function(it,k){ it.setAttribute('aria-current', String(k===i)); });
    panes.forEach(function(p,k){ p.classList.toggle('on', k===i); });
  }
  items.forEach(function(it,i){ it.addEventListener('click',function(){ show(i); }); });
  document.addEventListener('keydown',function(e){
    if(!e.altKey) return;
    var m=/^Digit([1-9])$/.exec(e.code||'');
    if(!m) return;
    var n=parseInt(m[1],10);
    if(n>=1 && n<=items.length){ e.preventDefault(); show(n-1); }
  });
  show(0);
})();
</script>

@@SCRIPTS@@
'''

OUT = (TPL.replace('@@STYLES@@', '\n\n'.join(styles))
          .replace('@@MENU@@', menu)
          .replace('@@PANES@@', '\n\n'.join(bodies))
          .replace('@@SCRIPTS@@', '\n'.join(scripts)))

io.open('../放映台.html', 'w', encoding='utf-8').write(OUT)
print('../放映台.html 已生成，%d 页' % len(PAGES))
