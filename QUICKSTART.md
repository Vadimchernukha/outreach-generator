# Быстрый старт

## ✅ Локальная установка завершена

Все зависимости установлены. Проект готов к использованию.

## 🚀 Локальный запуск

```powershell
# Установите API ключ (выберите один способ):

# Способ 1: Переменная окружения PowerShell
$env:GEMINI_API_KEY="ваш_ключ_от_aistudio.google.com"

# Способ 2: Создайте файл .env в корне проекта
# GEMINI_API_KEY=ваш_ключ_от_aistudio.google.com

# Запуск Streamlit приложения
streamlit run app.py
```

Приложение откроется в браузере по адресу `http://localhost:8501`

## ☁️ Развертывание на Streamlit Cloud

1. **Закоммитьте проект в Git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <ваш_репозиторий>
   git push -u origin main
   ```

2. **Развертывание:**
   - Перейдите на https://share.streamlit.io
   - Войдите через GitHub/GitLab
   - Нажмите "New app"
   - Выберите репозиторий и ветку
   - **Main file path:** `app.py`
   - Нажмите "Deploy"

3. **Настройка секретов в Streamlit Cloud:**
   - В настройках приложения: **Settings → Secrets**
   - Добавьте:
   ```toml
   GEMINI_API_KEY = "ваш_ключ_от_aistudio.google.com"
   ```

4. **Готово!** Приложение будет доступно по ссылке вида:
   `https://your-app-name.streamlit.app`

## 📝 Использование

1. Выберите клиента в боковой панели
2. Загрузите CSV файл с контактами
3. Нажмите "Generate Outreach Messages"
4. Дождитесь завершения обработки
5. Скачайте результаты

## ⚙️ CLI версия (опционально)

Если нужна командная строка вместо веб-интерфейса:

```bash
python main.py --client lionwood --input contacts.csv
```

## 📚 Дополнительная информация

- Подробная инструкция: `DEPLOYMENT.md`
- Структура проекта: `README.md`
