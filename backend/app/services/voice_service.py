import os
import logging
import httpx
from telegram import Bot

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# مسیر ذخیره‌سازی فایل‌های صوتی
STORAGE_DIR = os.path.join("backend", "storage", "voices")
os.makedirs(STORAGE_DIR, exist_ok=True)


class VoiceService:
    @staticmethod
    async def download_voice_file(bot: Bot, file_id: str, report_id: int) -> str:
        """
        دریافت لینک دانلود فایل صوتی از بله و ذخیره آن در دیسک محلی
        """
        try:
            # ۱. دریافت اطلاعات فایل از API بله
            file_obj = await bot.get_file(file_id)
            
            # استخراج file_path تمیز (بدون آدرس پیش‌فرض تلگرام)
            raw_path = file_obj.file_path
            if "api.telegram.org/file/bot" in raw_path:
                # حذف آدرس پیش‌فرض تلگرام که کتابخانه اضافه کرده است
                file_path_relative = raw_path.split(f"bot{settings.BALE_BOT_TOKEN}/")[-1]
            else:
                file_path_relative = raw_path

            # ۲. ساخت آدرس مستقیم دانلود روی سرور بله
            file_url = f"https://tapi.bale.ai/file/bot{settings.BALE_BOT_TOKEN}/{file_path_relative}"
            logger.info(f"در حال دانلود فایل از آدرس بله: {file_url}")

            # ۳. تعیین مسیر ذخیره‌سازی محلی
            file_extension = "ogg"
            file_name = f"voice_report_{report_id}.{file_extension}"
            local_file_path = os.path.join(STORAGE_DIR, file_name)

            # ۴. دانلود فایل از بله
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(file_url, timeout=30.0)
                response.raise_for_status()

                with open(local_file_path, "wb") as f:
                    f.write(response.content)

            logger.info(f"فایل صوتی با موفقیت ذخیره شد: {local_file_path}")
            return local_file_path

        except Exception as e:
            logger.error(f"خطا در دانلود فایل صوتی (report_id={report_id}): {e}", exc_info=True)
            raise e


voice_service = VoiceService()