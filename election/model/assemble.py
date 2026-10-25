# 把模型資料填入兩個網頁範本（GitHub Pages 用，輸出完整 HTML）
#   ../index.html：一頁看懂（simple.html，資料精簡）
#   ../full.html ：完整數據版（template.html＋地圖形狀）
import os, json
os.chdir(os.path.dirname(os.path.abspath(__file__)))
d = open('data.json', encoding='utf-8').read()
def wrap(t, split):
    head, body = t.split(split, 1)
    return ('<!doctype html>\n<html lang="zh-Hant-TW">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + '</head>\n<body>\n' + split + body + '\n</body>\n</html>\n')
j = json.loads(d)
for r in j['races'].values():
    r['npolls'] = len(r['polls'])
    for k in ('buzz', 'base_ref', 'note', 'proj'): r.pop(k, None)
    for x in r['series']:
        for k in ('adj', 'pa'): x.pop(k, None)
simple = open('simple.html', encoding='utf-8').read().replace('__SHAPES__', open('shapes.json', encoding='utf-8').read()).replace('__DATA__', json.dumps(j, ensure_ascii=False, separators=(',', ':')))
open('../index.html', 'w', encoding='utf-8').write(wrap(simple, '<div class="wrap">'))
full = open('template.html', encoding='utf-8').read().replace('__DATA__', d).replace('__SHAPES__', open('shapes.json', encoding='utf-8').read())
open('../full.html', 'w', encoding='utf-8').write(wrap(full, '<div class="wrap">'))
