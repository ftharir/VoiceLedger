import logging

from telegram import Update
from telegram.ext import ContextTypes

from backend.app.crud import crud_user, crud_voice_report
from backend.app.crud.crud_domain import crud_domain
from backend.app.crud.crud_knowledge_entry import crud_knowledge_entry
from backend.app.db.session import AsyncSessionLocal
from backend.app.schemas import (
    UserCreate,
    VoiceReportCreate,
    VoiceReportUpdate,
)
from backend.app.services.voice_service import voice_service
from backend.app.services.stt_service import stt_service


logger = logging.getLogger(__name__)


async def get_or_create_bot_user(db, tg_user):
    """
    کاربر بله را از دیتابیس دریافت می‌کند.
    اگر کاربر قبلاً ثبت نشده باشد، او را ایجاد می‌کند.
    """
    user_in = UserCreate(
        bale_user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )

    return await crud_user.get_or_create(
        db,
        obj_in=user_in,
    )


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    پردازش دستور /start
    """
    if not update.message or not update.effective_user:
        return

    tg_user = update.effective_user

    async with AsyncSessionLocal() as db:
        db_user = await get_or_create_bot_user(
            db,
            tg_user,
        )

        if not db_user.is_approved:
            await update.message.reply_text(
                f"سلام {tg_user.first_name} عزیز! 👋\n\n"
                "🔒 حساب کاربری شما ثبت شده، اما هنوز توسط مدیر "
                "سیستم تایید نشده است.\n"
                "لطفاً منتظر تایید مدیر بمانید."
            )
            return

        welcome_message = (
            f"سلام {tg_user.first_name} عزیز! 👋\n\n"
            "به سامانه ثبت گزارش‌های صوتی خوش آمدید.\n"
            "شما می‌توانید گزارش صوتی خود را ارسال کنید تا "
            "به‌صورت خودکار متن آن استخراج و ذخیره شود.\n\n"
            "برای راهنمایی بیشتر دستور /help را ارسال کنید."
        )

        await update.message.reply_text(welcome_message)


async def help_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    پردازش دستور /help
    """
    if not update.message or not update.effective_user:
        return

    tg_user = update.effective_user

    async with AsyncSessionLocal() as db:
        db_user = await get_or_create_bot_user(
            db,
            tg_user,
        )

        if not db_user.is_approved:
            await update.message.reply_text(
                "🔒 شما دسترسی به بخش‌های ربات را ندارید. "
                "حساب شما در انتظار تایید است."
            )
            return

        help_text = (
            "📌 راهنمای استفاده از ربات:\n\n"
            "1. یک پیام صوتی (Voice) حاوی گزارش کاری خود ضبط و ارسال کنید.\n"
            "2. سیستم به‌صورت خودکار صوت شما را پردازش کرده و متنش را استخراج می‌کند.\n"
            "3. گزارش شما در پایگاه داده ثبت خواهد شد."
        )

        await update.message.reply_text(help_text)


async def voice_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    دریافت Voice، بررسی کاربر، ذخیره فایل، تبدیل صوت به متن
    و ثبت متن در Knowledge Base.
    """
    if (
        not update.message
        or not update.message.voice
        or not update.effective_user
    ):
        return

    tg_user = update.effective_user
    voice = update.message.voice

    async with AsyncSessionLocal() as db:
        # ---------------------------------------------------------
        # 1. دریافت یا ایجاد کاربر
        # ---------------------------------------------------------
        db_user = await get_or_create_bot_user(
            db,
            tg_user,
        )

        # ---------------------------------------------------------
        # 2. بررسی تایید کاربر
        # ---------------------------------------------------------
        if not db_user.is_approved:
            await update.message.reply_text(
                "🔒 خطای دسترسی:\n"
                "حساب کاربری شما هنوز تایید نشده است و "
                "امکان ثبت گزارش صوتی را ندارید."
            )
            return

        processing_msg = await update.message.reply_text(
            "🎙 گزارش صوتی شما دریافت شد.\n"
            "در حال ثبت و دریافت فایل..."
        )

        try:
            # ---------------------------------------------------------
            # 3. دریافت Domain پیش‌فرض
            # ---------------------------------------------------------
            default_domain = await crud_domain.get_by_slug(
                db,
                slug="technical",
            )

            if default_domain is None:
                raise RuntimeError(
                    "Default domain 'technical' was not found."
                )

            # ---------------------------------------------------------
            # 4. ایجاد VoiceReport
            # ---------------------------------------------------------
            report_in = VoiceReportCreate(
                user_id=db_user.id,
                domain_id=default_domain.id,
                file_id=voice.file_id,
                duration=voice.duration,
            )

            db_report = await crud_voice_report.create(
                db,
                obj_in=report_in,
            )

            # ---------------------------------------------------------
            # 5. دانلود فایل صوتی
            # ---------------------------------------------------------
            local_path = await voice_service.download_voice_file(
                bot=context.bot,
                file_id=voice.file_id,
                report_id=db_report.id,
            )

            # ---------------------------------------------------------
            # 6. ذخیره مسیر فایل و وضعیت downloaded
            # ---------------------------------------------------------
            await crud_voice_report.update(
                db,
                db_obj=db_report,
                obj_in=VoiceReportUpdate(
                    file_path=local_path,
                    status="downloaded",
                ),
            )

            await processing_msg.edit_text(
                "⚙️ فایل صوتی ذخیره شد.\n"
                "در حال استخراج متن گزارش (Speech-to-Text)..."
            )

            # ---------------------------------------------------------
            # 7. تبدیل Voice به Text
            # ---------------------------------------------------------
            transcription_text = await stt_service.transcribe_audio(
                local_path
            )

            # ---------------------------------------------------------
            # 8. تکمیل VoiceReport + ایجاد KnowledgeEntry
            #
            # این دو عملیات در CRUDKnowledgeEntry با یک Commit
            # انجام می‌شوند تا اطلاعات هماهنگ باقی بمانند.
            # ---------------------------------------------------------
            await crud_knowledge_entry.complete_voice_report_with_entry(
                db,
                report=db_report,
                transcription=transcription_text,
            )

            # ---------------------------------------------------------
            # 9. ارسال نتیجه به کاربر
            # ---------------------------------------------------------
            success_text = (
                "✅ گزارش صوتی با موفقیت پردازش شد\n\n"
                f"🆔 شناسه پیگیری: {db_report.id}\n"
                f"⏱ مدت زمان: {voice.duration} ثانیه\n"
                "📊 وضعیت: تکمیل شده (Completed)\n"
                f"🏷 حوزه: {default_domain.name}\n\n"
                "📝 متن استخراج‌شده:\n"
                f"{transcription_text}"
            )

            await processing_msg.edit_text(
                success_text,
            )

        except Exception as e:
            logger.error(
                "خطا در پردازش Voice user=%s: %s",
                tg_user.id,
                e,
                exc_info=True,
            )

            await processing_msg.edit_text(
                "❌ متأسفانه در پردازش گزارش صوتی خطایی رخ داد.\n"
                "لطفاً دوباره تلاش کنید."
            )