# -*- coding: utf-8 -*-

import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

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

def main() -> None:
    """ربات را در حالت دیباگ اجرا می‌کند."""
    if not TOKEN:
        logger.error("خطا: توکن ربات (TOKEN) در متغیرهای محیطی تنظیم نشده است.")
        return

    # ساخت یک اپلیکیشن ساده بدون هیچ تنظیمات اضافی
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن فقط یک handler که همه چیز را لاگ کند
    application.add_handler(MessageHandler(filters.ALL, log_everything))

    logger.info("ربات در حالت دیباگ در حال اجراست و منتظر هرگونه رویدادی است...")
    
    # اجرای ربات
    application.run_polling()

if __name__ == "__main__":
    main()
