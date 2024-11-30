# Веб-приложение для управления страницами

Это веб-приложение позволяет создавать и управлять страницами с контентом.

## Функциональность

- Авторизация пользователей
- Создание новых страниц
- Редактирование существующих страниц
- Управление контентом
- Адаптивный дизайн

## Технологии

- Python/Flask
- SQLAlchemy
- JavaScript
- HTML/CSS
- Bootstrap
- Gunicorn (для production)

## Установка для разработки

1. Клонируйте репозиторий: 
```bash
git clone https://github.com/rix70/dashboard.git
```
2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```
3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env на основе .env.example и настройте переменные окружения

5. Запустите приложение для разработки:
```bash
flask run
```

## Установка для production

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте systemd сервис (для Linux):
```bash
sudo nano /etc/systemd/system/dashboard.service
```

Содержимое файла:
```ini
[Unit]
Description=Gunicorn instance to serve dashboard application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/app/venv/bin"
ExecStart=/path/to/your/app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

3. Запустите и включите сервис:
```bash
sudo systemctl start dashboard
sudo systemctl enable dashboard
```

## Быстрый запуск в production

Если вы не хотите использовать systemd, можно запустить приложение напрямую через Gunicorn:

```bash
gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app
```

## Команды для управления production сервером

Просмотр логов:
```bash
sudo journalctl -u dashboard
```

Перезапуск сервиса:
```bash
sudo systemctl restart dashboard
```

Проверка статуса:
```bash
sudo systemctl status dashboard
```

## Структура проекта
app/
├── templates/    # HTML шаблоны
├── static/       # Статические файлы (CSS, JS)
├── models/       # Модели данных
└── routes/       # Маршруты приложения


## Лицензия

MIT