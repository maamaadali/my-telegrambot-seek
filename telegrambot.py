# -*- coding: utf-8 -*-

import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, ContextTypes
from telegram.constants import UpdateType

# --- بخش وب‌سرور برای آنلاین نگه داشتن ربات در Render ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Minimalist Debug Bot is running."

def run_webserver():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --------------------------------------------------

# تنظیمات لاگ‌گیری
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن از متغیرهای محیطی
TOKEN = os.environ.get("TOKEN")

async def chat_member_update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """این تابع هر تغییری در وضعیت اعضای چت را به صورت واضح در لاگ ثبت می‌کند."""
    logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    logger.info("!!! یک رویداد ورود/خروج عضو دریافت شد !!!")
    logger.info(update.to_json())
    logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

def main() -> None:
    """تابع اصلی برای راه‌اندازی ربات در حالت تست."""
    if not TOKEN:
        logger.error("خطای مرگبار: متغیر محیطی توکن (TOKEN) تنظیم نشده است.")
        return

    # به طور صریح فقط منتظر رویدادهای مربوط به اعضا می‌مانیم
    allowed_updates = [UpdateType.CHAT_MEMBER]

    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .build()
    )

    # اضافه کردن فقط یک handler برای رصد اعضا
    application.add_handler(ChatMemberHandler(chat_member_update_handler))

    logger.info("ربات تست نهایی شروع به کار کرد. فقط منتظر رویدادهای ورود/خروج است...")
    application.run_polling(allowed_updates=allowed_updates)

if __name__ == "__main__":
    # اجرای وب‌سرور در یک نخ (thread) جداگانه
    webserver_thread = threading.Thread(target=run_webserver)
    webserver_thread.start()
    
    # اجرای ربات در نخ اصلی
    main()
