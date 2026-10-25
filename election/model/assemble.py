# 把模型資料與地圖形狀填入網頁範本
# 輸出：election-2026.html（Artifact 用，無 HTML 外殼）與 ../index.html（GitHub Pages 用，完整 HTML）
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
t = open('template.html', encoding='utf-8').read()
t = t.replace('__DATA__', open('data.json', encoding='utf-8').read()).replace('__SHAPES__', open('shapes.json', encoding='utf-8').read())
open('election-2026.html', 'w', encoding='utf-8').write(t)
# 標題、字型與樣式放進 <head>，其餘內容放進 <body>
head, body = t.split('<div class="wrap">', 1)
page = ('<!doctype html>\n<html lang="zh-Hant-TW">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + '</head>\n<body>\n<div class="wrap">' + body + '\n</body>\n</html>\n')
open('../index.html', 'w', encoding='utf-8').write(page)
