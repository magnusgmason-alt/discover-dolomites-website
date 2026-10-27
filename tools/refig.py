import json,re,html,sys
from PIL import Image
S="/tmp/claude-0/-home-claude/96b13b95-0569-5aee-a6f2-66753673bd63/scratchpad/"; R="/home/claude/gh-site/"
arts=json.load(open(S+"articles.json")); by={a["slug"]:a for a in arts}
def dims(i): return Image.open(f"{R}assets/img/{i}-1800.jpg").size
def fig(img,alt,place,cap,flip):
    w,h=dims(img); c=("portrait" if h>w else "wide")+(" flip" if flip else "")
    return (f'\n        <figure class="{c}"><img src="/assets/img/{img}-1800.jpg" srcset="/assets/img/{img}-800.jpg 800w, /assets/img/{img}-1800.jpg 1800w" '
            f'sizes="(min-width: 760px) 720px, 100vw" alt="{html.escape(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async">'
            f'<figcaption><span class="fig-place">{html.escape(place)}</span>{html.escape(cap)}</figcaption></figure>')
def place_after(body,head):
    m=re.search(r'<h[23]>'+re.escape(html.escape(head,quote=False)).replace("'","(?:'|&#x27;)")+r'</h[23]>',body); assert m,head
    np_=body.find("</p>",m.end()); nu=body.find("<ul>",m.end())
    return np_+4 if (nu<0 or np_<nu) else body.index("</ul>",m.end())+5
SPEC=json.load(open(S+"figspec.json"))
for slug,sp in SPEC.items():
    a=by[slug]
    body=re.sub(r'\n        <figure class="[^"]*">.*?</figure>','',a["body_html"],flags=re.S)
    for i,(head,img,alt,place,cap) in enumerate(sp["figs"]):
        p=place_after(body,head); body=body[:p]+fig(img,alt,place,cap,i%2==1)+body[p:]
    a["body_html"]=body
    if "header" in sp:
        img,alt=sp["header"]; w,h=dims(img); a.update(image=img,image_alt=alt,image_w=w,image_h=h)
json.dump(arts,open(S+"articles.json","w"),ensure_ascii=False,indent=1)
for s in SPEC: print(s, by[s]["body_html"].count("<figure"))
