# Docker-Controller

## Описание

Проект для копирования докер-контейнеров из репозиториев и их контроля

## Структура проекта

- `repo/` — репозитории
- `models/` — модели
- `db/` — модуль работы с бд
- `core/config/` — конфиг
- `api/` — роутеры
- `adapters/` — адаптеры

## Установка

```bash
git clone https://github.com/Dedushka-Lenin/Docker-Controller
cd Docker-Controller
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Настройка

1. Если не созданна беза данных и нужные таблицы настройте файл db.ipynb и запустите предварительно создав и указав пользователя.

2. Укажите настройки подключения к бд в файле 'app/core/config/connect_conf.toml'

3. Укажите настройки jwt-токена в файле 'app/core/config/jwt_conf.toml'

## Работа программы

1. Запуск докера — ```bash sudo systemctl start docker```

2. Запуск api — ```bash uvicorn app.main:app --reload```

3. Тестовая ссылка — <https://github.com/alpinelinux/docker-alpine>




///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

сделать файлы миграций