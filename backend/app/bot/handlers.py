import logging
from telegram import Update
from telegram.ext import ContextTypes

from backend.app.crud import crud_user, crud_voice_report
from backend.app.db.session import AsyncSessionLocal
from backend.app.schemas import UserCreate, VoiceReportCreate

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


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دریافت وویس ارسال شده، ثبت کاربر و ایجاد رکورد گزارش صوتی در دیتابیس"""
    if not update.message or not update.message.voice or not update.effective_user:
        return

    tg_user = update.effective_user
    voice = update.message.voice

    # اطلاع‌رسانی اولیه به کاربر
    processing_msg = await update.message.reply_text("🎙 گزارش صوتی شما دریافت شد. در حال ثبت در سیستم...")

    async with AsyncSessionLocal() as db:
        try:
            # ۱. ثبت یا بازیابی کاربر
            user_in = UserCreate(
                bale_user_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
            )
            db_user = await crud_user.get_or_create(db, obj_in=user_in)

            # ۲. ساخت رکورد جدید گزارش صوتی
            report_in = VoiceReportCreate(
                user_id=db_user.id,
                file_id=voice.file_id,
                duration=voice.duration,
            )
            db_report = await crud_voice_report.create(db, obj_in=report_in)

            # ۳. ارسال پاسخ موفقیت‌آمیز به کاربر
            success_text = (
                f"✅ **گزارش صوتی با موفقیت ثبت شد**\n\n"
                f"🆔 **شناسه پیگیری:** `{db_report.id}`\n"
                f"⏱ **مدت زمان:** {voice.duration} ثانیه\n"
                f"📊 **وضعیت:** در صف پردازش (Pending)\n\n"
                f"به محض استخراج متن، نتیجه به شما اطلاع داده خواهد شد."
            )
            await processing_msg.edit_text(success_text, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"خطا در ثبت گزارش صوتی: {e}", exc_info=True)
            await processing_msg.edit_text("❌ متأسفانه در ثبت گزارش صوتی خطایی رخ داد. لطفاً دوباره تلاش کنید.")