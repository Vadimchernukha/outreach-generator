# AI Cold Outreach Generator

Генерирует персонализированные цепочки из 5 Telegram-сообщений для каждого контакта.
Использует Google Gemini 1.5 Pro. Поддерживает любое количество клиентов.

## Структура проекта

```
outreach-generator/
├── main.py                    # точка входа
├── core/
│   ├── config_loader.py       # загрузка YAML конфига
│   ├── csv_handler.py         # чтение CSV, детект колонок, сохранение
│   ├── generator.py           # генерация цепочки через Gemini
│   └── humanizer.py           # очеловечивание сообщений
└── clients/
    ├── _template.yaml         # шаблон для нового клиента
    └── lionwood.yaml          # конфиг Lionwood Software
```

## Установка

```bash
pip install google-generativeai pandas openpyxl pyyaml
```

## Настройка API ключа

```bash
export GEMINI_API_KEY="твой_ключ_от_aistudio.google.com"
```

## Запуск

```bash
# Для Lionwood
python main.py --client lionwood --input contacts.csv

# С указанием файла вывода
python main.py --client lionwood --input contacts.csv --output results.csv

# Для другого клиента
python main.py --client myclient --input data.csv
```

## Добавить нового клиента

1. Скопируй `clients/_template.yaml` → `clients/ИМЯ.yaml`
2. Заполни:
   - `client_name` — название компании
   - `company_context` — описание компании для промпта
   - `csv_columns` — маппинг твоих колонок CSV на внутренние ключи
   - `dynamic_fields_after` — имя колонки, после которой всё идёт в AI как доп. инфо
   - `generation_prompt` / `humanize_prompt` — можно менять под стиль клиента
3. Запусти: `python main.py --client ИМЯ --input файл.csv`

## Формат входного CSV

Обязательные колонки (названия настраиваются в YAML):
- Имя контакта
- Должность
- Название компании
- Сайт
- Индустрия
- Размер компании
- Страна и город

Всё что стоит **после** колонки-границы (`dynamic_fields_after`) — автоматически
передаётся в AI как дополнительная информация о компании. Названия этих колонок
не важны — AI разберётся сам.

## Формат выходного CSV

На каждый контакт — 5 строк (по одной на каждое сообщение):
- Данные контакта
- `strategy` — логика воронки от AI
- `message_step` — номер сообщения (1–5)
- `send_after` — когда отправлять (Day 1, Day 3, ...)
- `angle` — угол атаки этого сообщения
- `original_message` — сырой текст от AI
- `final_message` — очеловеченная версия
