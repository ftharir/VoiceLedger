import logging
import sys
from telegram.ext import ApplicationBuilder, CommandHandler

from backend.app.core.config import settings
from backend.app.bot.handlers import help_handler, start_handler

# تنظیم لاگر
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# آدرس پایه API پیام‌رسان بله
BALE_BASE_URL = "https://tapi.bale.ai/bot"


def create_bot_application():
    """ساخت و کانفیگ نمونه Application ربات بله"""
    token = getattr(settings, "BALE_BOT_TOKEN", None)
    
    if not token or token == "your_bale_bot_token_here":
        logger.warning("BALE_BOT_TOKEN تنظیم نشده است!")

    # تنظیم base_url به سرور بله
    builder = ApplicationBuilder().token(token if token else "DUMMY_TOKEN").base_url(BALE_BASE_URL)
    app = builder.build()

    # ثبت Handlerهای دستورات
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))

    return app


if __name__ == "__main__":
    logger.info("در حال راه‌اندازی ربات بله...")
    bot_app = create_bot_application()
    
    if settings.BALE_BOT_TOKEN and settings.BALE_BOT_TOKEN != "your_bale_bot_token_here":
        bot_app.run_polling()
    else:
        logger.error("خطا: توکن معتبر برای بله در فایل .env یافت نشد.")
        sys.exit(1)