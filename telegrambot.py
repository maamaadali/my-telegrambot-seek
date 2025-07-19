# -*- coding: utf-8 -*-

import logging
import os
import html
import json
import traceback
from telegram import Update, ChatMember, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, ChatMemberHandler, ContextTypes
from telegram.constants import ParseMode

# فعال کردن لاگ‌گیری برای دیباگ کردن بهتر
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- خواندن متغیرهای حساس از محیط ---
TOKEN = os.environ.get("TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

# --- تابع جدید برای مدیریت خطاها ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    این تابع خطاها را ثبت می‌کند و یک پیام برای ادمین ارسال می‌کند
    تا از بروز مشکل مطلع شود.
    """
    logger.error("Exception while handling an update:", exc_info=context.error)

    # فرمت کردن اطلاعات خطا برای ارسال به ادمین
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # فرمت کردن اطلاعات آپدیت به صورت خوانا
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        f"</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # ارسال گزارش خطا به ادمین
    if ADMIN_CHAT_ID:
        # برای جلوگیری از طولانی شدن بیش از حد پیام، آن را به قطعات کوچکتر تقسیم می‌کنیم
        for i in range(0, len(message), 4096):
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID, text=message[i:i+4096], parse_mode=ParseMode.HTML
            )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دستور /start برای شروع به کار ربات و نمایش پیام خوش‌آمدگویی."""
    await update.message.reply_text(
        "سلام! من را به کانال خود اضافه کنید و به من دسترسی ادمین بدهید.\n"
        "هر زمان که کاربری کانال را ترک کند، من به شما اطلاع خواهم داد."
    )

def extract_status_change(chat_member_update: ChatMemberUpdated) -> tuple | None:
    """تغییرات وضعیت اعضا را بررسی کرده و اطلاعات کاربر را در صورت ترک کانال برمی‌گرداند."""
    new_member_status = chat_member_update.new_chat_member.status
    old_member_status = chat_member_update.old_chat_member.status
    
    was_member = old_member_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    is_now_left = new_member_status in [ChatMember.LEFT, ChatMember.BANNED]

    if was_member and is_now_left:
        return chat_member_update.new_chat_member.user
    
    return None

async def track_left_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """این تابع اصلی برای رصد اعضای خارج شده است."""
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
                chat_id=ADMIN_CHAT_ID,
                text=message,
                parse_mode='Markdown'
            )

def main() -> None:
    """ربات را راه‌اندازی و اجرا می‌کند."""
    if not TOKEN:
        logger.error("خطا: توکن ربات (TOKEN) در متغیرهای محیطی تنظیم نشده است.")
        return
    if not ADMIN_CHAT_ID:
        logger.error("خطا: شناسه ادمین (ADMIN_CHAT_ID) در متغیرهای محیطی تنظیم نشده است.")
    
    application = Application.builder().token(TOKEN).build()

    # --- ثبت کردن مدیر خطا ---
    application.add_error_handler(error_handler)

    # ثبت دستورات و پاسخ‌دهنده‌ها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatMemberHandler(track_left_members, ChatMemberHandler.CHAT_MEMBER))

    print("ربات برای رصد اعضای ترک کرده در حال اجراست...")
    application.run_polling()

if __name__ == "__main__":
    main()
