# Развертывание на Streamlit Cloud

## Быстрый старт

1. **Подготовка репозитория:**
   - Убедитесь, что проект в Git репозитории (GitHub, GitLab, Bitbucket)
   - Все файлы закоммичены

2. **Развертывание на Streamlit Cloud:**
   - Перейдите на https://share.streamlit.io
   - Войдите через GitHub/GitLab
   - Нажмите "New app"
   - Выберите репозиторий и ветку
   - **Main file path:** `app.py`
   - Нажмите "Deploy"

3. **Настройка секретов:**
   - В настройках приложения: Settings → Secrets
   - Добавьте:
   ```toml
   ANTHROPIC_API_KEY = "ваш_ключ_от_console.anthropic.com"
   ```

4. **Готово!** Приложение будет доступно по ссылке вида:
   `https://your-app-name.streamlit.app`

## Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка API ключа (выберите один способ):
# Способ 1: Создайте .env файл
echo ANTHROPIC_API_KEY=ваш_ключ > .env

# Способ 2: Переменная окружения
export ANTHROPIC_API_KEY=ваш_ключ  # Linux/Mac
set ANTHROPIC_API_KEY=ваш_ключ     # Windows CMD
$env:ANTHROPIC_API_KEY="ваш_ключ"  # Windows PowerShell

# Способ 3: Streamlit secrets (для локального тестирования)
# Скопируйте .streamlit/secrets.toml.example в .streamlit/secrets.toml
# и заполните ключ

# Запуск
streamlit run app.py
```

## Структура для Streamlit Cloud

```
outreach-generator/
├── app.py                    # Главный файл Streamlit приложения
├── main.py                   # CLI версия (опционально)
├── requirements.txt          # Python зависимости
├── packages.txt              # Системные пакеты (если нужны)
├── .streamlit/
│   ├── config.toml           # Конфигурация Streamlit
│   └── secrets.toml.example  # Пример секретов
├── core/                     # Основная логика
└── clients/                  # Конфиги клиентов
```

## Важные замечания

- **API ключ:** Никогда не коммитьте `.env` или `.streamlit/secrets.toml` в Git
- **Файлы:** Временные CSV файлы создаются и удаляются автоматически
- **Лимиты:** Учитывайте лимиты API Anthropic при обработке больших объемов
- **Задержки:** Настройте delay в интерфейсе для соблюдения rate limits
