import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""
    user = update.effective_user
    first_name = user.first_name if user else "کاربر"
    
    welcome_message = (
        f"سلام {first_name} عزیز! 👋\n\n"
        "به سامانه ثبت گزارش‌های صوتی خوش آمدید.\n"
        "شما می‌توانید گزارش‌های صوتی خود را ارسال کنید تا به‌صورت خودکار متن‌کاوی و ذخیره شوند.\n\n"
        "برای راهنمایی بیشتر دستور /help را ارسال کنید."
    )
    
    if update.message:
        await update.message.reply_text(welcome_message)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /help"""
    help_text = (
        "راهنمای استفاده از ربات: 📌\n\n"
        "۱. یک وویس (Voice) حاوی گزارش کاری خود ضبط و ارسال کنید.\n"
        "۲. سیستم به‌صورت خودکار صوت شما را پردازش کرده و متنش را استخراج می‌کند.\n"
        "۳. گزارش شما در پایگاه داده ثبت خواهد شد."
    )
    if update.message:
        await update.message.reply_text(help_text)