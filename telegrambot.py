# -*- coding: utf-8 -*-

import logging
import os
import threading
import html
import json
import traceback
from flask import Flask
from telegram import Update, ChatMember, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, ChatMemberHandler, ContextTypes
from telegram.constants import ParseMode, UpdateType

# --- بخش وب‌سرور برای آنلاین نگه داشتن ربات در Render ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running successfully!"

def run_webserver():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --------------------------------------------------

# تنظیمات لاگ‌گیری
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن متغیرهای محیطی
TOKEN = os.environ.get("TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """این تابع خطاها را ثبت کرده و برای ادمین ارسال می‌کند."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    if ADMIN_CHAT_ID:
        for i in range(0, len(message), 4096):
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID, text=message[i:i+4096], parse_mode=ParseMode.HTML
            )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دستور /start برای نمایش پیام خوش‌آمدگویی."""
    await update.message.reply_text(
        "ربات فعال است. من را در کانال خود ادمین کنید تا خروج اعضا را به شما گزارش دهم."
    )

def extract_status_change(chat_member_update: ChatMemberUpdated) -> tuple | None:
    """تغییرات وضعیت اعضا را بررسی کرده و کاربر خارج شده را برمی‌گرداند."""
    new_member_status = chat_member_update.new_chat_member.status
    old_member_status = chat_member_update.old_chat_member.status
    
    was_member = old_member_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    is_now_left = new_member_status in [ChatMember.LEFT, ChatMember.BANNED]

    if was_member and is_now_left:
        return chat_member_update.new_chat_member.user
    return None

async def track_left_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تابع اصلی برای رصد اعضای خارج شده و ارسال گزارش به ادمین."""
    user_who_left = extract_status_change(update.chat_member)
    if user_who_left:
        user = user_who_left
        chat = update.chat_member.chat
        username = f"(@{user.username})" if user.username else "(نام کاربری ندارد)"
        message = (
            f"کاربر زیر کانال «{chat.title}» را ترک کرد:\n\n"
            f"👤 **نام:** {user.full_name}\n"
            f"🆔 **شناسه:** `{user.id}`\n"
            f"🔗 **نام کاربری:** {username}"
        )
        logger.info(f"کاربر {user.full_name} کانال {chat.title} را ترک کرد.")
        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID, text=message, parse_mode='Markdown'
            )

def main() -> None:
    """تابع اصلی برای راه‌اندازی ربات."""
    if not TOKEN:
        logger.error("خطا: توکن ربات (TOKEN) در متغیرهای محیطی تنظیم نشده است.")
        return

    allowed_updates = [UpdateType.MESSAGE, UpdateType.CHAT_MEMBER]

    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .build()
    )

    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatMemberHandler(track_left_members, ChatMemberHandler.CHAT_MEMBER))

    logger.info("ربات با موفقیت در حال اجراست...")
    application.run_polling(allowed_updates=allowed_updates)

if __name__ == "__main__":
    webserver_thread = threading.Thread(target=run_webserver)
    webserver_thread.start()
    main()
