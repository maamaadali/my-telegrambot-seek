# -*- coding: utf-8 -*-

import logging
from telegram import Update, ChatMember, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, ChatMemberHandler, ContextTypes

# فعال کردن لاگ‌گیری برای دیباگ کردن بهتر
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- متغیرهای اصلی ---
# توکن ربات خود را که از BotFather گرفته‌اید، اینجا قرار دهید
TOKEN = "7119870529:AAFS3rYP1Cipck1N5qD0jER9RDRT7pEBT68"
# شناسه عددی چت خودتان را اینجا قرار دهید تا گزارش‌ها به شما ارسال شود
# برای پیدا کردن شناسه عددی خود، به ربات @userinfobot پیام دهید
ADMIN_CHAT_ID = 6571464370  # این عدد را با شناسه خودتان جایگزین کنید

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دستور /start برای شروع به کار ربات و نمایش پیام خوش‌آمدگویی."""
    await update.message.reply_text(
        "سلام! من را به کانال خود اضافه کنید و به من دسترسی ادمین بدهید.\n"
        "هر زمان که کاربری کانال را ترک کند، من به شما اطلاع خواهم داد."
    )

def extract_status_change(chat_member_update: ChatMemberUpdated) -> tuple | None:
    """
    تغییرات وضعیت اعضا را بررسی کرده و اطلاعات کاربر را در صورت ترک کانال برمی‌گرداند.
    این تابع زمانی که یک کاربر از کانال خارج می‌شود (left) یا از آن حذف می‌شود (kicked)، فعال می‌شود.
    """
    # وضعیت جدید و قدیم کاربر را استخراج می‌کند
    new_member_status = chat_member_update.new_chat_member.status
    old_member_status = chat_member_update.old_chat_member.status
    
    # بررسی می‌کند که آیا کاربر قبلاً عضو بوده و حالا خارج شده است
    was_member = old_member_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    is_now_left = new_member_status in [ChatMember.LEFT, ChatMember.BANNED]

    if was_member and is_now_left:
        # اگر کاربر خارج شده باشد، اطلاعات او را برمی‌گرداند
        return chat_member_update.new_chat_member.user
    
    return None

async def track_left_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    این تابع اصلی برای رصد اعضای خارج شده است.
    هر زمان تغییری در وضعیت اعضای چت (کانال) رخ دهد، این تابع فراخوانی می‌شود.
    """
    # اطلاعات کاربر را از تابع کمکی استخراج می‌کند
    user_who_left = extract_status_change(update.chat_member)
    
    if user_who_left:
        user = user_who_left
        chat = update.chat_member.chat
        
        # نام کاربری را بررسی می‌کند که آیا وجود دارد یا نه
        username = f"(@{user.username})" if user.username else "(نام کاربری ندارد)"
        
        # پیامی که برای ادمین ارسال می‌شود
        message = (
            f"کاربر زیر کانال «{chat.title}» را ترک کرد:\n\n"
            f"👤 **نام:** {user.full_name}\n"
            f"🆔 **شناسه:** `{user.id}`\n"
            f"🔗 **نام کاربری:** {username}"
        )
        
        logger.info(f"کاربر {user.full_name} کانال {chat.title} را ترک کرد.")
        
        # ارسال پیام به ادمین با فرمت Markdown
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )

def main() -> None:
    """ربات را راه‌اندازی و اجرا می‌کند."""
    # ساخت یک نمونه از Application با توکن ربات
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن CommandHandler برای دستور /start
    application.add_handler(CommandHandler("start", start))
    
    # اضافه کردن ChatMemberHandler برای رصد تغییرات اعضا
    # این handler به تمام تغییرات اعضا در هر چتی که ربات در آن حضور دارد، گوش می‌دهد
    application.add_handler(ChatMemberHandler(track_left_members, ChatMemberHandler.CHAT_MEMBER))

    # شروع به کار ربات در حالت Long Polling
    print("ربات برای رصد اعضای ترک کرده در حال اجراست...")
    application.run_polling()

if __name__ == "__main__":
    main()
