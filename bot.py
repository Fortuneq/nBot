#!/usr/bin/env python3
"""
Telegram Bot для сбора данных (фото, диалог, описание сцены)
и отправки их в n8n webhook.

Автор: Backend Engineer
Дата: 2025-12-08
"""

import os
import logging
import asyncio
import base64
from io import BytesIO
from typing import Dict, Any

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import aiohttp


# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для состояний ConversationHandler
PHOTO, DIALOG, SCENE_DESCRIPTION = range(3)

# Конфигурация
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')

# Проверка наличия обязательных переменных
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не установлен в .env файле")
if not N8N_WEBHOOK_URL:
    raise ValueError("N8N_WEBHOOK_URL не установлен в .env файле")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start.
    Приветствует пользователя и показывает доступные команды.
    """
    user = update.effective_user

    # Создаем клавиатуру с кнопкой
    keyboard = [
        ['Начать генерацию'],
        ['Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    welcome_text = (
        f"Привет, {user.first_name}!\n\n"
        f"Я бот для генерации контента на основе ваших данных.\n\n"
        f"Доступные команды:\n"
        f"/start - Показать это сообщение\n"
        f"/generate - Начать процесс сбора данных\n"
        f"/cancel - Отменить текущую операцию\n\n"
        f"Используй кнопки ниже или введи команду вручную."
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )

    logger.info(f"Пользователь {user.id} ({user.username}) запустил команду /start")


async def start_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начало процесса сбора данных.
    Просит пользователя отправить фото.
    """
    user = update.effective_user

    await update.message.reply_text(
        "Отлично! Начинаем процесс сбора данных.\n\n"
        "Шаг 1/3: Пожалуйста, отправь мне фото.\n\n"
        "Для отмены операции используй команду /cancel",
        reply_markup=ReplyKeyboardRemove()
    )

    logger.info(f"Пользователь {user.id} начал процесс генерации")

    # Инициализируем хранилище данных для этого пользователя
    context.user_data['generation_data'] = {}

    return PHOTO


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Получение фото от пользователя.
    Сохраняет file_id и переходит к запросу диалога.
    """
    user = update.effective_user
    photo = update.message.photo[-1]  # Берем самое большое фото

    try:
        # Получаем файл
        photo_file = await context.bot.get_file(photo.file_id)

        # Скачиваем файл в память
        photo_bytes = BytesIO()
        await photo_file.download_to_memory(photo_bytes)
        photo_bytes.seek(0)

        # Конвертируем в base64
        photo_base64 = base64.b64encode(photo_bytes.read()).decode('utf-8')

        # Сохраняем данные
        context.user_data['generation_data']['photo_file_id'] = photo.file_id
        context.user_data['generation_data']['photo_base64'] = photo_base64

        await update.message.reply_text(
            "Отлично! Фото получено.\n\n"
            "Шаг 2/3: Теперь отправь мне диалог (текст)."
        )

        logger.info(f"Пользователь {user.id} отправил фото (file_id: {photo.file_id})")

        return DIALOG

    except Exception as e:
        logger.error(f"Ошибка при обработке фото от пользователя {user.id}: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке фото. Попробуй отправить другое фото."
        )
        return PHOTO


async def receive_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Получение диалога от пользователя.
    Сохраняет текст и переходит к запросу описания сцены.
    """
    user = update.effective_user
    dialog_text = update.message.text

    # Сохраняем диалог
    context.user_data['generation_data']['dialog'] = dialog_text

    await update.message.reply_text(
        "Отлично! Диалог получен.\n\n"
        "Шаг 3/3: Теперь отправь мне описание сцены (текст)."
    )

    logger.info(f"Пользователь {user.id} отправил диалог (длина: {len(dialog_text)} символов)")

    return SCENE_DESCRIPTION


async def receive_scene_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Получение описания сцены от пользователя.
    Сохраняет текст, отправляет все данные в webhook и завершает диалог.
    """
    user = update.effective_user
    scene_description = update.message.text

    # Сохраняем описание сцены
    context.user_data['generation_data']['scene_description'] = scene_description

    await update.message.reply_text(
        "Отлично! Все данные получены.\n\n"
        "Отправляю данные в обработку..."
    )

    logger.info(f"Пользователь {user.id} отправил описание сцены (длина: {len(scene_description)} символов)")

    # Отправляем данные в webhook
    success = await send_to_webhook(
        user_id=user.id,
        username=user.username,
        data=context.user_data['generation_data']
    )

    if success:
        await update.message.reply_text(
            "Данные успешно отправлены в обработку!\n\n"
            "Для новой генерации используй команду /generate",
            reply_markup=ReplyKeyboardMarkup(
                [['Начать генерацию'], ['Помощь']],
                resize_keyboard=True
            )
        )
    else:
        await update.message.reply_text(
            "Произошла ошибка при отправке данных в обработку.\n"
            "Пожалуйста, попробуй еще раз позже или обратись к администратору.",
            reply_markup=ReplyKeyboardMarkup(
                [['Начать генерацию'], ['Помощь']],
                resize_keyboard=True
            )
        )

    # Очищаем данные пользователя
    context.user_data['generation_data'] = {}

    return ConversationHandler.END


async def send_to_webhook(user_id: int, username: str, data: Dict[str, Any]) -> bool:
    """
    Отправляет собранные данные в n8n webhook.

    Args:
        user_id: ID пользователя Telegram
        username: Username пользователя Telegram
        data: Словарь с данными (photo_file_id, photo_base64, dialog, scene_description)

    Returns:
        bool: True если отправка успешна, False в случае ошибки
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "photo_file_id": data.get('photo_file_id'),
        "photo_base64": data.get('photo_base64'),
        "dialog": data.get('dialog'),
        "scene_description": data.get('scene_description')
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                N8N_WEBHOOK_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    logger.info(f"Данные пользователя {user_id} успешно отправлены в webhook")
                    response_data = await response.text()
                    logger.debug(f"Ответ от webhook: {response_data}")
                    return True
                else:
                    logger.error(
                        f"Ошибка при отправке в webhook. "
                        f"Статус: {response.status}, "
                        f"Ответ: {await response.text()}"
                    )
                    return False

    except asyncio.TimeoutError:
        logger.error(f"Timeout при отправке данных пользователя {user_id} в webhook")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке в webhook: {e}")
        return False


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отмена текущей операции.
    """
    user = update.effective_user

    # Очищаем данные пользователя
    if 'generation_data' in context.user_data:
        context.user_data['generation_data'] = {}

    await update.message.reply_text(
        "Операция отменена.\n\n"
        "Для новой генерации используй команду /generate",
        reply_markup=ReplyKeyboardMarkup(
            [['Начать генерацию'], ['Помощь']],
            resize_keyboard=True
        )
    )

    logger.info(f"Пользователь {user.id} отменил операцию")

    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды помощи.
    """
    help_text = (
        "Помощь по использованию бота:\n\n"
        "1. Используй команду /generate (или кнопку 'Начать генерацию')\n"
        "2. Отправь фото\n"
        "3. Отправь диалог (текст)\n"
        "4. Отправь описание сцены (текст)\n\n"
        "После отправки всех данных они будут обработаны системой.\n\n"
        "Команды:\n"
        "/start - Главное меню\n"
        "/generate - Начать сбор данных\n"
        "/cancel - Отменить текущую операцию\n"
        "/help - Показать эту справку"
    )

    await update.message.reply_text(help_text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик нажатий на кнопки.
    """
    text = update.message.text

    if text == 'Начать генерацию':
        return await start_generate(update, context)
    elif text == 'Помощь':
        await help_command(update, context)
        return ConversationHandler.END

    return ConversationHandler.END


def main() -> None:
    """
    Основная функция запуска бота.
    """
    logger.info("Запуск бота...")

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Определяем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('generate', start_generate),
            MessageHandler(filters.Regex('^Начать генерацию$'), button_handler)
        ],
        states={
            PHOTO: [
                MessageHandler(filters.PHOTO, receive_photo),
            ],
            DIALOG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_dialog),
            ],
            SCENE_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_scene_description),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
        ],
    )

    # Регистрируем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.Regex('^Помощь$'), help_command))
    application.add_handler(conv_handler)

    # Запускаем бота
    logger.info("Бот успешно запущен и готов к работе")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
