import os
import logging
import asyncio
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self):
        self.model = None

    def _load_model(self):
        if self.model is None:
            logger.info("در حال بارگذاری مدل Whisper فارسی (faster-whisper - small)...")
            # استفاده از مدل small که دقت بسیار بالاتری در زبان فارسی دارد
            self.model = WhisperModel("small", device="cpu", compute_type="int8")
            logger.info("مدل Whisper با موفقیت بارگذاری شد.")

    async def transcribe_audio(self, file_path: str) -> str:
        """
        دریافت مسیر فایل صوتی محلی و تبدیل واقعی آن به متن فارسی با Whisper
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"فایل صوتی در مسیر یافت نشد: {file_path}")

        try:
            logger.info(f"در حال پردازش و استخراج متن واقعی از فایل: {file_path}")

            def run_transcription():
                self._load_model()
                # تنظیم پارامترها برای جلوگیری از ایجاد متن‌های بی‌معنی (Hallucination)
                segments, info = self.model.transcribe(
                    file_path,
                    language="fa",
                    beam_size=5,
                    temperature=0.0,  # جلوگیری از حدس‌های عجیب‌وغریب
                    vad_filter=True,   # حذف سکوت‌های ابتدا و انتهای وویس
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                
                full_text = " ".join([segment.text.strip() for segment in segments])
                return full_text

            transcription = await asyncio.to_thread(run_transcription)

            logger.info(f"متن استخراج‌شده: {transcription}")
            return transcription if transcription.strip() else "(متنی از وویس تشخیص داده نشد)"

        except Exception as e:
            logger.error(f"خطا در تبدیل گفتار به متن: {e}", exc_info=True)
            raise e


stt_service = STTService()