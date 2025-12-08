# Deployment Guide

Руководство по развертыванию Telegram-бота в продакшн.

## Содержание

1. [Развертывание с Docker](#развертывание-с-docker)
2. [Развертывание на сервере (systemd)](#развертывание-на-сервере-systemd)
3. [Мониторинг и логирование](#мониторинг-и-логирование)
4. [Backup и восстановление](#backup-и-восстановление)
5. [Обновление и CI/CD](#обновление-и-cicd)

---

## Развертывание с Docker

### Подготовка

1. Установите Docker и Docker Compose на сервере:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker
```

2. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd nBot
```

3. Настройте `.env` файл:

```bash
cp .env.example .env
nano .env  # Укажите TELEGRAM_TOKEN
```

### Сборка и запуск

```bash
# Сборка образа
docker-compose build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f telegram-bot

# Остановка
docker-compose down
```

### Управление контейнером

```bash
# Проверка статуса
docker-compose ps

# Рестарт
docker-compose restart

# Просмотр логов (последние 100 строк)
docker-compose logs --tail=100 telegram-bot

# Вход в контейнер
docker-compose exec telegram-bot /bin/bash

# Удаление контейнера и образа
docker-compose down --rmi all -v
```

---

## Развертывание на сервере (systemd)

### 1. Подготовка окружения

```bash
# Создание директории
sudo mkdir -p /opt/nbot
sudo chown $USER:$USER /opt/nbot

# Копирование файлов
cp -r * /opt/nbot/
cd /opt/nbot

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Создание systemd service

Создайте файл `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=your_username
Group=your_username
WorkingDirectory=/opt/nbot
Environment="PATH=/opt/nbot/.venv/bin"
ExecStart=/opt/nbot/.venv/bin/python /opt/nbot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/nbot/logs

[Install]
WantedBy=multi-user.target
```

### 3. Управление сервисом

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Запуск сервиса
sudo systemctl start telegram-bot

# Включение автозапуска
sudo systemctl enable telegram-bot

# Проверка статуса
sudo systemctl status telegram-bot

# Просмотр логов
sudo journalctl -u telegram-bot -f

# Остановка
sudo systemctl stop telegram-bot

# Рестарт
sudo systemctl restart telegram-bot
```

---

## Мониторинг и логирование

### Настройка ротации логов

Создайте `/etc/logrotate.d/telegram-bot`:

```
/opt/nbot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 your_username your_username
}
```

### Мониторинг через Prometheus + Grafana (опционально)

1. Установите prometheus_client:

```bash
pip install prometheus-client
```

2. Добавьте метрики в `bot.py`:

```python
from prometheus_client import start_http_server, Counter, Gauge

# Метрики
messages_total = Counter('bot_messages_total', 'Total messages processed')
active_users = Gauge('bot_active_users', 'Number of active users')
webhook_requests = Counter('bot_webhook_requests_total', 'Webhook requests', ['status'])

# Запуск metrics сервера
start_http_server(8000)
```

3. Настройте Prometheus для сбора метрик:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'telegram-bot'
    static_configs:
      - targets: ['localhost:8000']
```

### Мониторинг здоровья бота

Создайте скрипт `/opt/nbot/healthcheck.sh`:

```bash
#!/bin/bash

# Проверка процесса
if systemctl is-active --quiet telegram-bot; then
    echo "Bot is running"
    exit 0
else
    echo "Bot is not running"
    # Отправка уведомления (например, в Telegram)
    curl -X POST "https://api.telegram.org/bot<ADMIN_BOT_TOKEN>/sendMessage" \
         -d "chat_id=<ADMIN_CHAT_ID>" \
         -d "text=Bot is down!"
    exit 1
fi
```

Добавьте в crontab:

```bash
# Проверка каждые 5 минут
*/5 * * * * /opt/nbot/healthcheck.sh
```

---

## Backup и восстановление

### Backup данных

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/nbot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup конфигурации
tar -czf $BACKUP_DIR/nbot-config-$DATE.tar.gz \
    /opt/nbot/.env \
    /opt/nbot/bot.py

# Backup логов (опционально)
tar -czf $BACKUP_DIR/nbot-logs-$DATE.tar.gz /opt/nbot/logs/

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Автоматизация бэкапов через cron:

```bash
# Ежедневный backup в 2:00
0 2 * * * /opt/nbot/backup.sh
```

### Восстановление

```bash
# Остановка сервиса
sudo systemctl stop telegram-bot

# Восстановление конфигурации
cd /
tar -xzf /backup/nbot/nbot-config-YYYYMMDD_HHMMSS.tar.gz

# Запуск сервиса
sudo systemctl start telegram-bot
```

---

## Обновление и CI/CD

### Ручное обновление

```bash
# Остановка сервиса
sudo systemctl stop telegram-bot

# Обновление кода
cd /opt/nbot
git pull origin main

# Обновление зависимостей
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# Запуск сервиса
sudo systemctl start telegram-bot

# Проверка статуса
sudo systemctl status telegram-bot
```

### Автоматизация через GitHub Actions

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/nbot
            git pull origin main
            source .venv/bin/activate
            pip install -r requirements.txt --upgrade
            sudo systemctl restart telegram-bot
            sleep 5
            sudo systemctl status telegram-bot
```

### Blue-Green Deployment (для нулевого downtime)

```bash
# Структура
/opt/nbot-blue/
/opt/nbot-green/

# Скрипт деплоя
#!/bin/bash
ACTIVE=$(readlink /opt/nbot-current)
if [ "$ACTIVE" == "/opt/nbot-blue" ]; then
    DEPLOY_TO="/opt/nbot-green"
else
    DEPLOY_TO="/opt/nbot-blue"
fi

# Обновление неактивной версии
cd $DEPLOY_TO
git pull
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# Переключение symlink
ln -sfn $DEPLOY_TO /opt/nbot-current

# Рестарт сервиса
sudo systemctl restart telegram-bot
```

---

## Безопасность

### Firewall настройки

```bash
# Разрешить только исходящие соединения
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
```

### Обновления безопасности

```bash
# Автоматические обновления системы
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### Ограничение ресурсов (systemd)

Добавьте в service файл:

```ini
[Service]
# Ограничения памяти
MemoryLimit=512M
MemoryMax=1G

# Ограничения CPU
CPUQuota=50%

# Ограничения файловых дескрипторов
LimitNOFILE=1024
```

---

## Troubleshooting в продакшне

### Проверка логов

```bash
# Логи systemd
sudo journalctl -u telegram-bot -n 100 --no-pager

# Логи в реальном времени
sudo journalctl -u telegram-bot -f

# Логи с фильтром по уровню
sudo journalctl -u telegram-bot -p err

# Логи за последний час
sudo journalctl -u telegram-bot --since "1 hour ago"
```

### Диагностика проблем

```bash
# Проверка процесса
ps aux | grep bot.py

# Проверка портов (если используется)
sudo netstat -tulpn | grep python

# Проверка использования ресурсов
top -p $(pgrep -f bot.py)

# Проверка дискового пространства
df -h
```

### Аварийное восстановление

```bash
# Принудительная остановка
sudo systemctl kill telegram-bot

# Очистка логов
sudo journalctl --vacuum-time=1d

# Перезапуск с новыми настройками
sudo systemctl daemon-reload
sudo systemctl restart telegram-bot
```

---

## Checklist для продакшн деплоя

- [ ] Сервер настроен и обновлен
- [ ] Python 3.10+ установлен
- [ ] Виртуальное окружение создано
- [ ] Все зависимости установлены
- [ ] .env файл настроен с корректными значениями
- [ ] Systemd service создан и включен
- [ ] Firewall настроен
- [ ] Логирование настроено
- [ ] Мониторинг настроен
- [ ] Backup настроен
- [ ] Тестирование проведено
- [ ] Документация обновлена
- [ ] Контакты для экстренной связи подготовлены

---

Готово! Бот развернут в продакшн и готов к работе.
