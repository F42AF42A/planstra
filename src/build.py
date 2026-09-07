# -*- coding: utf-8 -*-
"""Собирает обе версии Планстры из одного источника.

Источник правды — planstra-src.html (русский). Английская версия получается
подстановкой переводов по точным позициям из i18n/units.json: слепой
заменой строк по всему файлу можно испортить код, поэтому режем по спанам.

    python3 build.py            → dist/ru/ и dist/en/
    python3 build.py ru         → только русская
"""
import json, re, os, sys, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, 'planstra-src.html')

# ─────────────────────────────────────────── локали

L = {
 'ru': dict(
   lang='ru',
   title='Планстра — конструктор бренд-стратегии',
   site='Планстра',
   desc='Планстра — конструктор бренд-стратегии: 45 слайдов от SWOT и PESTLE '
        'до позиционирования, миссии и голубого океана. С примерами, '
        'подсказками и выгрузкой в PDF.',
   ogdesc='45 слайдов: SWOT, PESTLE, аудитории, позиционирование, миссия, '
          'голубой океан. Примеры, подсказки, выгрузка в PDF.',
   domain='planstra.ru',
   home='https://planstra.ru/',
   cur='RUB',
   altlabel='English version',
   features=['45 разделов бренд-стратегии','PESTLE-анализ и SWOT',
             'Расчёт ёмкости рынка','Сегментация целевой аудитории',
             'Разработка УТП','Карта позиционирования',
             'Разработка миссии и карты бренда',
             'Стратегическая канва голубого океана и решётка ERRC',
             'Примеры на каждом шаге','Выгрузка в PDF и Markdown',
             'Без регистрации, данные хранятся в браузере'],
 ),
 'en': dict(
   lang='en',
   title='Planstra — brand strategy builder',
   site='Planstra',
   desc='Planstra is a brand strategy builder: 45 slides from SWOT and PESTLE '
        'through positioning and mission to blue ocean. With examples, '
        'guidance and PDF export.',
   ogdesc='45 slides: SWOT, PESTLE, audiences, positioning, mission, blue '
          'ocean. Examples, guidance, PDF export.',
   domain='planstra.pro',
   home='https://planstra.pro/',
   cur='USD',
   altlabel='Русская версия',
   features=['45 brand strategy sections','PESTLE analysis and SWOT',
             'Market size calculation','Target audience segmentation',
             'USP development','Positioning map',
             'Mission and brand map',
             'Blue ocean strategy canvas and ERRC grid',
             'A worked example on every step','PDF and Markdown export',
             'No sign-up, data stays in your browser'],
 ),
}

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#08090A">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{site}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{ogdesc}">
<meta property="og:image" content="og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{ogdesc}">
<meta name="twitter:image" content="og.png">
<title>{title}</title>
<style>html,body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Onest:wght@500;700&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
"""

# ─────────────────────────────────────────── шаги сборки

def script_ranges(s):
    return [(m.start(1), m.end(1))
            for m in re.finditer(r'<script\b[^>]*>(.*?)</script>', s, re.S | re.I)]


def in_js(pos, ranges):
    return any(a <= pos < b for a, b in ranges)


def esc_js(t):
    """Русский текст не содержал кавычек — они были границами фрагмента.
    Значит любая кавычка в переводе новая и обязана быть экранирована,
    иначе она закроет строку. В JS такое экранирование безопасно в любом
    типе строк, поэтому не гадаем, в какие кавычки нас положили."""
    t = t.replace('\\', '\\\\')
    for ch in ('`', '"', "'"):
        t = t.replace(ch, '\\' + ch)
    return t.replace('${', '\\${')


def esc_html(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def translate(src, units, en):
    """Подставляет переводы, идя с конца, чтобы позиции не поехали."""
    out = src
    ranges = script_ranges(src)
    miss = 0
    for u in sorted(units, key=lambda x: x['parts'][0][0], reverse=True):
        tr = en.get(u['text'])
        if tr is None:
            miss += 1
            continue
        esc = esc_js if in_js(u['parts'][0][0], ranges) else esc_html
        # экранируем только текст, разметку в разделителях не трогаем
        pieces = re.split(r'\{\d+\}', tr)
        if len(pieces) != len(u['seps']) + 1:
            miss += 1
            continue
        txt = esc(pieces[0])
        for k, sep in enumerate(u['seps']):
            txt += sep + esc(pieces[k + 1])
        a, b = u['parts'][0][0], u['parts'][-1][1]
        out = out[:a] + txt + out[b:]
    return out, miss


def patch_download(s):
    """Автономная выгрузка вместо capability артефакта."""
    old = ('let saver = null;\n'
           'claude.use("downloads").then(x=>{ saver = x; }).catch(()=>{});')
    new = ('let saver = null;\n'
           'try{ if(typeof claude!=="undefined" && claude.use) '
           'claude.use("downloads").then(x=>{ saver = x; }).catch(()=>{}); }catch(e){}\n'
           'function localSave(name, text){\n'
           '  const a = document.createElement("a");\n'
           '  a.href = URL.createObjectURL(new Blob([text], '
           '{type:"text/markdown;charset=utf-8"}));\n'
           '  a.download = name; document.body.appendChild(a); a.click(); a.remove();\n'
           '  setTimeout(()=>URL.revokeObjectURL(a.href), 1000);\n'
           '}')
    assert old in s, 'не найден блок claude.use("downloads")'
    s = s.replace(old, new, 1)

    # Запасной путь. В артефакте выгрузку делает saver, а без него нужен
    # обычный скачиваемый файл — не буфер обмена: пользователь жмёт
    # «Экспорт MD» и ждёт файл. Забираем текст тоста из ветки saver, чтобы
    # не хардкодить язык.
    m = re.search(
        r'if\(saver\)\{\s*try\{ await saver\.save\(\{filename:fileName\(\), '
        r'data:md\}\); toast\("([^"]+)"\); return; \}', s)
    assert m, 'не найдена ветка saver'
    ok = m.group(1)
    old_fb = re.search(
        r'  try\{\n    await navigator\.clipboard\.writeText\(md\);\n'
        r'    toast\("[^"]*"\);\n  \}catch\(e\)\{ toast\("([^"]*)"\); \}', s)
    assert old_fb, 'не найден запасной путь экспорта'
    s = s[:old_fb.start()] + (
        '  try{\n'
        '    localSave(fileName(), md);\n'
        '    toast("%s");\n'
        '  }catch(e){ toast("%s"); }' % (ok, old_fb.group(1))
    ) + s[old_fb.end():]
    return s


def patch_locale_en(s):
    """Числительные и форматы, которые переводом не решаются."""
    plural = ('k%10===1 && k%100!==11 ? "slide" : (k%10>=2 && k%10<=4 '
              '&& (k%100<10||k%100>=20) ? "slides" : "slides")')
    assert plural in s, 'не найден блок склонения'
    s = s.replace(plural, 'k===1 ? "slide" : "slides"', 1)

    s = s.replace('(x/1e6).toFixed(1).replace(".",",")+" bn ₽"',
                  '(x/1e6).toFixed(1)+" bn ₽"', 1)
    s = s.replace('Math.round(x).toLocaleString("ru-RU")',
                  'Math.round(x).toLocaleString("en-US")', 1)
    return s


def jsonld(body, loc):
    """Разметка Schema.org. Вопросы и ответы вынимаем из уже собранной
    страницы, а не пишем повторно: две копии одного текста разойдутся
    на первой же правке, и поисковик увидит разметку, не совпадающую
    с содержимым, — за это он наказывает."""
    def clean(t):
        t = re.sub(r'<[^>]+>', '', t)
        return re.sub(r'\s+', ' ', t).strip()

    qa = []
    for m in re.finditer(r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>',
                         body, re.S):
        qa.append((clean(m.group(1)), clean(m.group(2))))

    site = loc['home']
    app = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": loc['site'],
        "url": site,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Any",
        "browserRequirements": "Requires JavaScript",
        "description": loc['desc'],
        "inLanguage": loc['lang'],
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0",
                   "priceCurrency": loc['cur'], "availability":
                   "https://schema.org/InStock"},
        "featureList": loc['features'],
    }
    out = ['<script type="application/ld+json">'
           + json.dumps(app, ensure_ascii=False, separators=(',', ':'))
           + '</script>']
    if qa:
        faq = {"@context": "https://schema.org", "@type": "FAQPage",
               "mainEntity": [{"@type": "Question", "name": q,
                               "acceptedAnswer": {"@type": "Answer", "text": a}}
                              for q, a in qa]}
        out.append('<script type="application/ld+json">'
                   + json.dumps(faq, ensure_ascii=False, separators=(',', ':'))
                   + '</script>')
    return '\n'.join(out), len(qa)


def altlang(body, lang):
    """Ссылка на другую языковую версию. В исходнике она одна на оба языка,
    поэтому английская сборка иначе ссылалась бы сама на себя."""
    other = 'en' if lang == 'ru' else 'ru'
    o = L[other]
    html = (f'<p class="alang">{L[lang]["altlabel"]}: '
            f'<a href="{o["home"]}" hreflang="{o["lang"]}">{o["domain"]}</a></p>')
    new, n = re.subn(r'<p class="alang">.*?</p>', html, body, count=1, flags=re.S)
    assert n == 1, 'не найден блок ссылки на другую версию'
    return new


def wrap(body, loc):
    ld, n = jsonld(body, loc)
    alt = '\n'.join(
        f'<link rel="alternate" hreflang="{L[k]["lang"]}" href="{L[k]["home"]}">'
        for k in ('ru', 'en'))
    alt += f'\n<link rel="alternate" hreflang="x-default" href="{L["en"]["home"]}">'
    alt += f'\n<link rel="canonical" href="{loc["home"]}">'
    head = HEAD.format(**loc) + alt + '\n' + ld + '\n'
    print(f'      разметка: {n} вопросов в FAQPage')
    return head + body + '\n</body>\n</html>\n'


ROBOTS = """User-agent: *
Allow: /

# Краулеры генеративных поисковиков пускаем явно: страница описывает
# бесплатный инструмент, и цитирование нам на пользу.
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-Web
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: YandexBot
Allow: /

Sitemap: {home}sitemap.xml
"""

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>{home}</loc>
    <xhtml:link rel="alternate" hreflang="ru" href="{ru}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""


def reextract():
    """Позиции строк привязаны к байтам источника: любая правка
    planstra-src.html их сдвигает. Поэтому извлекаем заново каждую сборку —
    иначе перевод вставится не туда и молча испортит код."""
    import subprocess
    subprocess.run(['python3', os.path.join(ROOT, 'i18n/extract.py')],
                   check=True, capture_output=True)


def build(lang):
    src = open(SRC, encoding='utf-8').read()
    if lang == 'en':
        units = json.load(open(os.path.join(ROOT, 'i18n/units.json'), encoding='utf-8'))
        en    = json.load(open(os.path.join(ROOT, 'i18n/en.json'), encoding='utf-8'))
        src, miss = translate(src, units, en)
        if miss:
            print('  ! без перевода:', miss, 'единиц')
        src = patch_download(src)
        src = patch_locale_en(src)
    else:
        src = patch_download(src)

    src = altlang(src, lang)
    html = wrap(src, L[lang])

    out = os.path.join(ROOT, 'dist', lang)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(html)
    for asset in ('favicon.svg', 'og.png'):
        for cand in ('assets', 'deploy', '.'):
            src_a = os.path.join(ROOT, cand, asset)
            if os.path.exists(src_a):
                shutil.copy(src_a, os.path.join(out, asset)); break
    open(os.path.join(out, '.nojekyll'), 'w').close()
    open(os.path.join(out, 'CNAME'), 'w').write(L[lang]['domain'] + '\n')
    open(os.path.join(out, 'robots.txt'), 'w', encoding='utf-8').write(
        ROBOTS.format(home=L[lang]['home']))
    open(os.path.join(out, 'sitemap.xml'), 'w', encoding='utf-8').write(
        SITEMAP.format(home=L[lang]['home'], ru=L['ru']['home'], en=L['en']['home']))

    left = len(re.findall(r'[А-Яа-яЁё]', html))
    print(f'  {lang}: {len(html):,} знаков, кириллицы осталось {left}')
    return html


if __name__ == '__main__':
    langs = sys.argv[1:] or ['ru', 'en']
    print('Сборка Планстры')
    reextract()
    # непереведённое не должно тихо утечь в английскую сборку
    ru = json.load(open(os.path.join(ROOT, 'i18n/ru_strings.json'), encoding='utf-8'))
    en = json.load(open(os.path.join(ROOT, 'i18n/en.json'), encoding='utf-8'))
    gap = [t for t in ru if t not in en]
    if gap:
        print(f'  ! новых строк без перевода: {len(gap)}')
        for t in gap[:10]:
            print('    •', t[:90])
        if 'en' in langs:
            sys.exit('  остановлено: сначала допишите переводы в i18n/en.json')
    for l in langs:
        build(l)
    print('готово → dist/')
