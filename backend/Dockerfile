# استفاده از ایمیج پایه رسمی پایتون نسخه 3.12 (نسخه slim برای کاهش حجم)
FROM python:3.12-slim

# جلوگیری از نوشتن فایل‌های pyc روی دیسک و ارسال مستقیم Logها به ترمینال
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تعیین پوشه کاری داخل کانتینر
WORKDIR /app

# نصب ابزارهای پایه سیستم‌عامل
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# کپی کردن فایل نیازمندی‌ها جهت استفاده از قابلیت Caching داکر
COPY backend/requirements.txt /app/requirements.txt

# نصب کتابخانه‌های پایتون
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# کپی کردن کدهای برنامه و سایر فایل‌های لازم به داخل کانتینر
COPY backend /app/backend
COPY .env /app/.env

# اضافه کردن مسیر پوشه کاری به PYTHONPATH جهت شناسایی ماژول‌ها
ENV PYTHONPATH=/app

# مشخص کردن پورتی که کانتینر روی آن گوش می‌دهد
EXPOSE 8000

# دستور اجرای سرور FastAPI در زمان روشن شدن کانتینر
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]