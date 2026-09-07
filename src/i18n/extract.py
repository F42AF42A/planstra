# -*- coding: utf-8 -*-
"""Извлекает переводимые единицы из strategos.html.

JS не парсим: файл состоит из вложенных шаблонных строк, наивный разбор
кавычек ошибётся. Берём максимальные куски текста, ограниченные символами,
которых в человеческом тексте не бывает. Экранированные пары (\\n, \\") —
тоже граница, иначе буква escape-последовательности утечёт в перевод.
Соседние куски, разделённые только HTML-разметкой, склеиваем в одну
единицу с плейсхолдерами {0}: переводить нужно предложение целиком,
иначе порядок слов в английском развалит фразу.
"""
import re, json

import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, 'strategos.html')
s=open(SRC,encoding='utf-8').read()
CYR=re.compile(r'[А-Яа-яЁё]')
BOUND=set('<>"\'`{}$\n\\')
MARKUP=re.compile(r'^(?:</?[a-zA-Z][^<>]*>|\s)+$')

# --- шаг 1: атомарные куски
raw=[]
i=0; n=len(s)
while i<n:
    ch=s[i]
    if ch=='\\': i+=2; continue          # экранированная пара целиком
    if ch in BOUND: i+=1; continue
    j=i
    while j<n and s[j] not in BOUND and s[j]!='\\': j+=1
    chunk=s[i:j]
    if CYR.search(chunk):
        a=i+len(chunk)-len(chunk.lstrip())
        b=j-(len(chunk)-len(chunk.rstrip()))
        if b>a: raw.append([a,b])
    i=j

# --- шаг 2: склейка через чистую разметку
units=[]           # {parts:[[a,b],...], seps:[str], text:"...{0}..."}
cur=[raw[0]]
for k in range(1,len(raw)):
    gap=s[raw[k-1][1]:raw[k][0]]
    if gap and len(gap)<=60 and MARKUP.match(gap):
        cur.append(raw[k])
    else:
        units.append(cur); cur=[raw[k]]
units.append(cur)

out=[]
for parts in units:
    seps=[s[parts[k][1]:parts[k+1][0]] for k in range(len(parts)-1)]
    txt=s[parts[0][0]:parts[0][1]]
    for k,sep in enumerate(seps):
        txt += '{%d}'%k + s[parts[k+1][0]:parts[k+1][1]]
    out.append({'parts':parts,'seps':seps,'text':txt})

# --- шаг 3: выбросить комментарии в коде — они не для пользователя
import bisect
cspans=[]
for m in re.finditer(r'/\*.*?\*/', s, re.S): cspans.append((m.start(), m.end()))
for m in re.finditer(r'(?m)^[ \t]*//[^\n]*', s): cspans.append((m.start(), m.end()))
cspans.sort(); cstart=[a for a, _ in cspans]
def in_comment(p):
    i = bisect.bisect_right(cstart, p) - 1
    return i >= 0 and cspans[i][0] <= p < cspans[i][1]
out = [u for u in out if not in_comment(u['parts'][0][0])]

json.dump(out,open(os.path.join(HERE,'units.json'),'w',encoding='utf-8'),ensure_ascii=False)
uniq=sorted({u['text'] for u in out})
json.dump(uniq,open(os.path.join(HERE,'ru_strings.json'),'w',encoding='utf-8'),
          ensure_ascii=False,indent=1)
print('атомов:',len(raw),'| единиц:',len(out),'| уникальных:',len(uniq))
print('знаков:',sum(len(x) for x in uniq))
print('со склейкой:',sum(1 for u in out if len(u['parts'])>1))
print('\n-- склеенные примеры --')
for u in out:
    if len(u['parts'])>1: print(repr(u['text'][:120])); 
    if len([1 for x in out[:0]])>0: break
