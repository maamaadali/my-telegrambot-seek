# -*- coding: utf-8 -*-

import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import UpdateType

# --- بخش وب‌سرور ساختگی برای راضی کردن Render ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Debug Bot is running!"

def run_webserver():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --------------------------------------------------

# فعال کردن لاگ‌گیری برای دیباگ کردن بهتر
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن از متغیرهای محیطی
TOKEN = os.environ.get("TOKEN")

async def log_everything(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    این تابع هر رویدادی که از تلگرام دریافت شود را به صورت کامل در لاگ چاپ می‌کند.
    """
    logger.info(f"--- یک رویداد جدید از تلگرام دریافت شد ---\n{update.to_json(indent=2)}\n--------------------------------------")

async def check_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    این تابع دسترسی‌های ربات را در چت فعلی بررسی و اعلام می‌کند.
    """
    if not update.message or not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    try:
        # دریافت اطلاعات ربات به عنوان یک عضو در این چت
        bot_member = await context.bot.get_chat_member(chat_id=chat_id, user_id=context.bot.id)
        
        # پیامی که در کانال ارسال می‌شود
        await update.message.reply_text(f"وضعیت من در این چت: {bot_member.status}")
        
        # لاگ کردن دسترسی‌ها برای بررسی دقیق‌تر
        logger.info(f"بررسی دسترسی در چت {chat_id}: وضعیت ربات {bot_member.status}")
        if bot_member.status == 'administrator':
            logger.info(f"دسترسی‌های ادمین: {bot_member.to_json()}")

    except Exception as e:
        logger.error(f"خطا در بررسی دسترسی‌ها: {e}")
        await update.message.reply_text(f"خطا در بررسی دسترسی‌ها: {e}")

def run_bot():
    """ربات را در حالت دیباگ اجرا می‌کند."""
    if not TOKEN:
        logger.error("خطا: توکن ربات (TOKEN) در متغیرهای محیطی تنظیم نشده است.")
        return

    # مشخص کردن آپدیت‌های مجاز
    allowed_updates = [UpdateType.MESSAGE, UpdateType.CHAT_MEMBER]

    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .build()
    )

    # اضافه کردن handlerها
    application.add_handler(CommandHandler("check", check_permissions))
    application.add_handler(MessageHandler(filters.ALL, log_everything))

    logger.info("ربات در حالت دیباگ در حال اجراست و منتظر هرگونه رویدادی است...")
    
    # --- تغییر مهم: انتقال allowed_updates به اینجا ---
    application.run_polling(allowed_updates=allowed_updates)

if __name__ == "__main__":
    webserver_thread = threading.Thread(target=run_webserver)
    webserver_thread.start()
    run_bot()
