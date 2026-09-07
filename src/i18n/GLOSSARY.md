# Planstra EN — translation glossary and rules

Planstra is a brand-strategy workbook: 45 slides a founder or marketer fills in,
from environment scanning through positioning to a blue-ocean strategy canvas.
Register: precise, plain, confident. Think Basecamp or Stripe docs — short
sentences, concrete nouns, no marketing fluff, no exclamation marks, no em-dash
padding. Address the reader as "you". American spelling.

## Fixed terms — always translate these exactly this way

| Russian | English |
|---|---|
| Планстра | Planstra |
| Конструктор бренд-стратегии | Brand strategy builder |
| Открытая бета-версия | Open beta |
| Обзор | Overview |
| Подробнее | Learn more |
| Пример | Example |
| Заполнить этим примером | Fill in this example |
| Очистить слайд | Clear slide |
| Стереть всё | Erase everything |
| Импорт MD / Экспорт MD | Import MD / Export MD |
| слайд / слайды | slide / slides |
| раздел | section |
| заполнено | filled in |
| ЦА, целевая аудитория | target audience |
| Ядро ЦА | Audience core |
| Типажи ЦА | Audience personas |
| Требования к ЦА | Audience requirements |
| УТП | USP |
| Позиционирование | Positioning |
| Точка дифференциации | Point of difference |
| Карта позиционирования | Positioning map |
| Голубой океан | Blue ocean |
| Стратегическая канва | Strategy canvas |
| Карта бренда | Brand map |
| Продуктовый мост | Product bridge |
| Сила мотива | Motive strength |
| Мотив | Motive |
| Критерий выбора | Choice criterion |
| Ключевые факторы успеха | Key success factors |
| Конъюнктура рынка | Market conditions |
| Ёмкость рынка | Market size |
| Сегменты по цене | Price segments |
| План исследования | Research plan |
| Проверка SWOT | SWOT check |
| Выводы SWOT | SWOT conclusions |
| SWOT-матрица | SWOT matrix |
| PESTLE-анализ | PESTLE analysis |
| SMART-цель | SMART goal |
| Имеющиеся ресурсы | Resources on hand |
| Достижимые ресурсы | Reachable resources |
| Миссия | Mission |
| Гипотеза | Hypothesis |
| Работает, если | Works if |
| Сильные стороны / Слабые стороны | Strengths / Weaknesses |
| Возможности / Угрозы | Opportunities / Threats |
| Кабинетное (исследование) | Desk research |
| Полевое (исследование) | Field research |
| Фактическая / Потенциальная / Доступная (ёмкость) | Actual / Potential / Available |
| Да / Нет | Yes / No |

## Hard rules

1. **Placeholders `{0}`, `{1}`, … are immovable fences.** They mark where HTML
   markup sits inside the sentence. Translate the text on each side of a
   placeholder independently and keep every placeholder, in the same order, with
   no text moved across it. If `Мотив{0}— самая сильная причина.` becomes
   `Motive{0}— the strongest reason.`, that is correct. Never merge two sides,
   never drop a placeholder, never add one.

2. **Return the same number of items, in the same order.** The output is a JSON
   object mapping each source string to its translation. Every input key must
   appear exactly once, byte-identical to the input.

3. **Keep proper nouns as they are**: Volvo, IKEA, Netflix, Cirque du Soleil,
   Avis, Hertz, Tesla, Dyson, Airbnb, Nike, Apple, Kennedy, and so on. Russian
   companies keep their Latin brand name if they have one (Яндекс → Yandex,
   Тинькофф → Tinkoff, Точка → Tochka, Авито → Avito, Вкусвилл → VkusVill,
   Додо Пицца → Dodo Pizza, Сбер → Sber).

4. **Keep numbers, percentages, years, currency figures and units.** Convert ₽
   amounts to the same figure with "₽" kept — do not invent dollar conversions.

5. **Quotes and dashes.** Russian «ёлочки» become English "double quotes".
   Keep the em dash — it is used the same way in the source.

6. **Length discipline.** These strings sit in a fixed UI: sidebar items,
   buttons, table headers, field labels. Keep short strings short — a 12-character
   Russian label must not become a 30-character English one. Prose paragraphs may
   run their natural length.

7. **Case.** Russian sentence case stays sentence case in English; do not switch
   to Title Case for headings and buttons.

8. **A fragment stays a fragment.** Some inputs are not full sentences (they were
   cut at a markup boundary). Translate what is there without completing it.

9. **Never output explanation, comments or markdown fences** — the file must be
   valid JSON and nothing else.
