# -*- coding: utf-8 -*-

import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

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
    logger.info(f"--- یک رویداد جدید از تلگرام دریافت شد ---\n{update}\n--------------------------------------")

def run_bot():
    """ربات را در حالت دیباگ اجرا می‌کند."""
    if not TOKEN:
        logger.error("خطا: توکن ربات (TOKEN) در متغیرهای محیطی تنظیم نشده است.")
        return

    # ساخت یک اپلیکیشن ساده
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن فقط یک handler که همه چیز را لاگ کند
    application.add_handler(MessageHandler(filters.ALL, log_everything))

    logger.info("ربات در حالت دیباگ در حال اجراست و منتظر هرگونه رویدادی است...")
    
    # اجرای ربات
    application.run_polling()

if __name__ == "__main__":
    # اجرای وب‌سرور در یک نخ (thread) جداگانه
    webserver_thread = threading.Thread(target=run_webserver)
    webserver_thread.start()
    
    # اجرای ربات در نخ اصلی
    run_bot()
