# Примеры использования

Практические примеры работы с Telegram-ботом.

## Содержание

1. [Базовое использование](#базовое-использование)
2. [Примеры диалогов](#примеры-диалогов)
3. [Тестирование webhook](#тестирование-webhook)
4. [Отладка](#отладка)
5. [Кастомизация](#кастомизация)

---

## Базовое использование

### Пример 1: Полный цикл сбора данных

```
Пользователь: /start
Бот: Привет, Владислав!

     Я бот для генерации контента на основе ваших данных.

     Доступные команды:
     /start - Показать это сообщение
     /generate - Начать процесс сбора данных
     /cancel - Отменить текущую операцию

     Используй кнопки ниже или введи команду вручную.

     [Кнопка: Начать генерацию] [Кнопка: Помощь]

Пользователь: /generate
Бот: Отлично! Начинаем процесс сбора данных.

     Шаг 1/3: Пожалуйста, отправь мне фото.

     Для отмены операции используй команду /cancel

Пользователь: [отправляет фото]
Бот: Отлично! Фото получено.

     Шаг 2/3: Теперь отправь мне диалог (текст).

Пользователь: - Здравствуйте!
               - Добрый день! Как дела?
               - Отлично, спасибо!
Бот: Отлично! Диалог получен.

     Шаг 3/3: Теперь отправь мне описание сцены (текст).

Пользователь: Солнечный день в парке, два человека беседуют на скамейке
Бот: Отлично! Все данные получены.

     Отправляю данные в обработку...

Бот: Данные успешно отправлены в обработку!

     Для новой генерации используй команду /generate

     [Кнопка: Начать генерацию] [Кнопка: Помощь]
```

### Пример 2: Отмена операции

```
Пользователь: /generate
Бот: Отлично! Начинаем процесс сбора данных.

     Шаг 1/3: Пожалуйста, отправь мне фото.

     Для отмены операции используй команду /cancel

Пользователь: [отправляет фото]
Бот: Отлично! Фото получено.

     Шаг 2/3: Теперь отправь мне диалог (текст).

Пользователь: /cancel
Бот: Операция отменена.

     Для новой генерации используй команду /generate

     [Кнопка: Начать генерацию] [Кнопка: Помощь]
```

### Пример 3: Использование кнопок

```
Пользователь: /start
Бот: [Показывает приветствие с кнопками]

Пользователь: [Нажимает кнопку "Помощь"]
Бот: Помощь по использованию бота:

     1. Используй команду /generate (или кнопку 'Начать генерацию')
     2. Отправь фото
     3. Отправь диалог (текст)
     4. Отправь описание сцены (текст)

     После отправки всех данных они будут обработаны системой.

     Команды:
     /start - Главное меню
     /generate - Начать сбор данных
     /cancel - Отменить текущую операцию
     /help - Показать эту справку

Пользователь: [Нажимает кнопку "Начать генерацию"]
Бот: [Запускается процесс сбора данных]
```

---

## Примеры диалогов

### Сценарий 1: Создание рекламного контента

```
Фото: Изображение продукта (кофемашина)
Диалог:
  - Что это за кофемашина?
  - Это новая модель DeluxeCoffee Pro 3000!
  - Какие у нее особенности?
  - Автоматическое приготовление 20 видов кофе и молочная пенка одним нажатием!

Описание сцены:
  Современная кухня, утро, на столе стоит кофемашина,
  рядом чашка с ароматным кофе, солнечный свет из окна
```

### Сценарий 2: Создание обучающего материала

```
Фото: Схема или диаграмма
Диалог:
  - Объясни, как работает этот процесс
  - Сначала данные поступают на сервер
  - Затем они обрабатываются?
  - Да, обрабатываются и сохраняются в базу данных

Описание сцены:
  Офисное помещение, презентация на проекторе,
  спикер объясняет техническую схему
```

### Сценарий 3: Создание сториз для социальных сетей

```
Фото: Селфи или lifestyle фото
Диалог:
  - Какие планы на сегодня?
  - Иду на фитнес, потом встреча с друзьями
  - Звучит отлично!
  - Да, жду с нетерпением!

Описание сцены:
  Фитнес-зал, яркое освещение, энергичная атмосфера,
  человек в спортивной одежде готовится к тренировке
```

---

## Тестирование webhook

### Ручное тестирование с curl

Проверка n8n webhook напрямую:

```bash
curl -X POST https://n8n.true-scale.ru/webhook/***REMOVED*** \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456789,
    "username": "test_user",
    "photo_file_id": "AgACAgIAAxkBAAIBCGY...",
    "photo_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
    "dialog": "Тестовый диалог",
    "scene_description": "Тестовое описание сцены"
  }'
```

### Проверка response

Ожидаемый ответ от n8n:

```json
{
  "status": "success",
  "message": "Data received"
}
```

### Тестирование с Python

Скрипт для тестирования webhook:

```python
import aiohttp
import asyncio
import base64

async def test_webhook():
    url = "https://n8n.true-scale.ru/webhook/***REMOVED***"

    # Тестовые данные
    with open("test_image.jpg", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

    payload = {
        "user_id": 999999999,
        "username": "test_user",
        "photo_file_id": "TEST_FILE_ID",
        "photo_base64": image_base64,
        "dialog": "Тестовый диалог для проверки webhook",
        "scene_description": "Тестовая сцена"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            print(f"Status: {response.status}")
            print(f"Response: {await response.text()}")

asyncio.run(test_webhook())
```

---

## Отладка

### Включение debug логирования

Измените уровень логирования в `bot.py`:

```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Было: logging.INFO
)
```

### Просмотр подробных логов

```bash
# Запуск с подробным выводом
python bot.py 2>&1 | tee bot_debug.log

# Фильтрация только ошибок
python bot.py 2>&1 | grep -i error

# Просмотр логов в реальном времени (systemd)
sudo journalctl -u telegram-bot -f
```

### Отладка webhook запросов

Добавьте в функцию `send_to_webhook()`:

```python
async def send_to_webhook(user_id: int, username: str, data: Dict[str, Any]) -> bool:
    payload = {
        "user_id": user_id,
        "username": username,
        "photo_file_id": data.get('photo_file_id'),
        "photo_base64": data.get('photo_base64'),
        "dialog": data.get('dialog'),
        "scene_description": data.get('scene_description')
    }

    # DEBUG: Вывод payload
    logger.debug(f"Sending payload: {json.dumps(payload, indent=2)}")

    # ... остальной код
```

### Тестирование без реального Telegram

Создайте mock для тестирования:

```python
from unittest.mock import Mock, AsyncMock

# Mock Update
update = Mock()
update.effective_user = Mock(id=123, username="test", first_name="Test")
update.message = AsyncMock()

# Mock Context
context = Mock()
context.user_data = {}
context.bot = AsyncMock()

# Тест функции
await start(update, context)
```

---

## Кастомизация

### Изменение текстов приветствия

В `bot.py`, функция `start()`:

```python
welcome_text = (
    f"Привет, {user.first_name}!\n\n"
    f"Я помогу тебе создать контент. Просто следуй инструкциям!\n\n"  # Изменено
    f"Доступные команды:\n"
    # ... остальное
)
```

### Добавление дополнительных кнопок

```python
keyboard = [
    ['Начать генерацию'],
    ['Помощь', 'О боте'],  # Добавлена кнопка "О боте"
    ['Мои данные']         # Новая кнопка
]
```

### Изменение порядка сбора данных

Если нужно сначала собрать текст, потом фото:

1. Измените состояния:
```python
TEXT, PHOTO, SCENE_DESCRIPTION = range(3)
```

2. Измените ConversationHandler:
```python
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('generate', start_generate),
    ],
    states={
        TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text),
        ],
        PHOTO: [
            MessageHandler(filters.PHOTO, receive_photo),
        ],
        SCENE_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_scene_description),
        ],
    },
    # ...
)
```

### Добавление валидации

Пример валидации длины текста:

```python
async def receive_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dialog_text = update.message.text

    # Валидация
    if len(dialog_text) < 10:
        await update.message.reply_text(
            "Диалог слишком короткий. Пожалуйста, отправь текст длиной минимум 10 символов."
        )
        return DIALOG  # Остаемся в том же состоянии

    if len(dialog_text) > 1000:
        await update.message.reply_text(
            "Диалог слишком длинный. Максимальная длина - 1000 символов."
        )
        return DIALOG

    # Продолжаем как обычно
    context.user_data['generation_data']['dialog'] = dialog_text
    # ...
```

### Добавление rate limiting

Ограничение частоты запросов:

```python
from collections import defaultdict
from datetime import datetime, timedelta

# Хранилище последних запросов
user_last_request = defaultdict(lambda: None)
COOLDOWN_SECONDS = 60  # 1 минута между запросами

async def start_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user

    # Проверка cooldown
    if user_last_request[user.id]:
        time_passed = datetime.now() - user_last_request[user.id]
        if time_passed < timedelta(seconds=COOLDOWN_SECONDS):
            remaining = COOLDOWN_SECONDS - time_passed.seconds
            await update.message.reply_text(
                f"Пожалуйста, подожди {remaining} секунд перед следующим запросом."
            )
            return ConversationHandler.END

    # Обновляем время последнего запроса
    user_last_request[user.id] = datetime.now()

    # Продолжаем как обычно
    # ...
```

### Сохранение истории в файл

Добавление логирования в файл:

```python
import json
from datetime import datetime

async def receive_scene_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... после успешной отправки в webhook

    # Сохранение в файл
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user.id,
        "username": user.username,
        "data": context.user_data['generation_data']
    }

    with open('history.jsonl', 'a') as f:
        f.write(json.dumps(history_entry) + '\n')

    # ...
```

---

## Интеграция с другими сервисами

### Отправка в несколько webhooks

```python
WEBHOOKS = [
    "https://n8n.true-scale.ru/webhook/***REMOVED***",
    "https://backup-webhook.example.com/data"
]

async def send_to_webhooks(user_id: int, username: str, data: Dict[str, Any]) -> List[bool]:
    results = []
    for webhook_url in WEBHOOKS:
        success = await send_to_webhook_single(webhook_url, user_id, username, data)
        results.append(success)
    return results
```

### Интеграция с базой данных

```python
import asyncpg

async def save_to_database(user_id: int, data: Dict[str, Any]):
    conn = await asyncpg.connect('postgresql://user:password@localhost/dbname')
    try:
        await conn.execute('''
            INSERT INTO generations (user_id, photo_file_id, dialog, scene_description, created_at)
            VALUES ($1, $2, $3, $4, NOW())
        ''', user_id, data['photo_file_id'], data['dialog'], data['scene_description'])
    finally:
        await conn.close()
```

---

## Примеры запуска

### Разработка (локально)

```bash
# С виртуальным окружением
source .venv/bin/activate
python bot.py

# Без виртуального окружения (не рекомендуется)
python3 bot.py
```

### Продакшн (systemd)

```bash
# Запуск
sudo systemctl start telegram-bot

# Статус
sudo systemctl status telegram-bot

# Логи
sudo journalctl -u telegram-bot -f
```

### Продакшн (Docker)

```bash
# С docker-compose
docker-compose up -d

# Без compose
docker build -t nbot .
docker run -d --name nbot --env-file .env nbot
```

### Продакшн (nohup)

```bash
# Запуск в фоне
nohup python bot.py > bot.log 2>&1 &

# Проверка
ps aux | grep bot.py

# Остановка
pkill -f bot.py
```

---

Готово! Эти примеры помогут быстро начать работу сботом и кастомизировать его под свои нужды.
