import logging
from telegram import Update
from telegram.ext import ContextTypes

from backend.app.crud import crud_user, crud_voice_report
from backend.app.db.session import AsyncSessionLocal
from backend.app.schemas import UserCreate, VoiceReportCreate, VoiceReportUpdate
from backend.app.services.voice_service import voice_service
from backend.app.services.stt_service import stt_service

logger = logging.getLogger(__name__)


async def get_or_create_bot_user(db, tg_user):
    """تابع کمکی جهت ثبت/بازیابی کاربر و چک کردن دسترسی"""
    user_in = UserCreate(
        bale_user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )
    return await crud_user.get_or_create(db, obj_in=user_in)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /start"""
    if not update.message or not update.effective_user:
        return

    tg_user = update.effective_user

    async with AsyncSessionLocal() as db:
        db_user = await get_or_create_bot_user(db, tg_user)

        if not db_user.is_approved:
            await update.message.reply_text(
                f"سلام {tg_user.first_name} عزیز! 👋\n\n"
                "🔒 حساب کاربری شما ثبت شده اما هنوز توسط مدیر سیستم **تایید نشده است**.\n"
                "لطفاً منتظر تایید مدیر بمانید."
            )
            return

        welcome_message = (
            f"سلام {tg_user.first_name} عزیز! 👋\n\n"
            "به سامانه ثبت گزارش‌های صوتی خوش آمدید.\n"
            "شما می‌توانید گزارش‌های صوتی خود را ارسال کنید تا به‌صورت خودکار متن‌کاوی و ذخیره شوند.\n\n"
            "برای راهنمایی بیشتر دستور /help را ارسال کنید."
        )
        await update.message.reply_text(welcome_message)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پاسخ به دستور /help"""
    if not update.message or not update.effective_user:
        return

    tg_user = update.effective_user

    async with AsyncSessionLocal() as db:
        db_user = await get_or_create_bot_user(db, tg_user)

        if not db_user.is_approved:
            await update.message.reply_text("🔒 شما دسترسی به بخش‌های ربات را ندارید. حساب شما در انتظار تایید است.")
            return

        help_text = (
            "راهنمای استفاده از ربات: 📌\n\n"
            "۱. یک وویس (Voice) حاوی گزارش کاری خود ضبط و ارسال کنید.\n"
            "۲. سیستم به‌صورت خودکار صوت شما را پردازش کرده و متنش را استخراج می‌کند.\n"
            "۳. گزارش شما در پایگاه داده ثبت خواهد شد."
        )
        await update.message.reply_text(help_text)


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دریافت وویس ارسال شده، بررسی دسترسی، ثبت در دیتابیس، دانلود فایل صوتی و استخراج متن"""
    if not update.message or not update.message.voice or not update.effective_user:
        return

    tg_user = update.effective_user
    voice = update.message.voice

    async with AsyncSessionLocal() as db:
        # ۱. بررسی احراز هویت و دسترسی کاربر
        db_user = await get_or_create_bot_user(db, tg_user)

        if not db_user.is_approved:
            await update.message.reply_text(
                "🔒 **خطای دسترسی:**\n"
                "حساب کاربری شما هنوز تایید نشده است و امکان ثبت گزارش صوتی را ندارید."
            )
            return

        processing_msg = await update.message.reply_text("🎙 گزارش صوتی شما دریافت شد. در حال ثبت و دریافت فایل...")

        try:
            # ۲. ساخت رکورد اولیه گزارش صوتی
            report_in = VoiceReportCreate(
                user_id=db_user.id,
                file_id=voice.file_id,
                duration=voice.duration,
            )
            db_report = await crud_voice_report.create(db, obj_in=report_in)

            # ۳. دانلود محلی فایل صوتی از سرور بله
            local_path = await voice_service.download_voice_file(
                bot=context.bot,
                file_id=voice.file_id,
                report_id=db_report.id,
            )

            # ۴. آپدیت وضعیت به دانلود شده
            await crud_voice_report.update(
                db, db_obj=db_report, obj_in=VoiceReportUpdate(file_path=local_path, status="downloaded")
            )

            # اطلاع‌رسانی مرحله تبدیل گفتار به متن
            await processing_msg.edit_text("⚙️ فایل صوتی ذخیره شد. در حال استخراج متن گزارش (Speech-to-Text)...")

            # ۵. تبدیل گفتار به متن
            transcription_text = await stt_service.transcribe_audio(local_path)

            # ۶. آپدیت متن و وضعیت نهایی در دیتابیس
            final_update = VoiceReportUpdate(
                transcription=transcription_text,
                status="completed"
            )
            await crud_voice_report.update(db, db_obj=db_report, obj_in=final_update)

            # ۷. ارسال متن استخراج شده به کاربر در بله
            success_text = (
                f"✅ **گزارش صوتی با موفقیت پردازش شد**\n\n"
                f"🆔 **شناسه پیگیری:** `{db_report.id}`\n"
                f"⏱ **مدت زمان:** {voice.duration} ثانیه\n"
                f"📊 **وضعیت:** تکمیل شده (Completed)\n\n"
                f"📝 **متن استخراج‌شده:**\n"
                f"« {transcription_text} »"
            )
            await processing_msg.edit_text(success_text, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"خطا در پردازش وویس: {e}", exc_info=True)
            await processing_msg.edit_text("❌ متأسفانه در پردازش گزارش صوتی خطایی رخ داد. لطفاً دوباره تلاش کنید.")