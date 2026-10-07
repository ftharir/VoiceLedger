# BaleVoiceReports

A Bale messenger bot plus REST API that collects **voice reports** from organization members, transcribes them to Persian text, and stores them in a searchable, multi-domain knowledge base.

> سامانه‌ی مرکزی دریافت، ذخیره و بازیابی گزارش‌های سازمانی: کاربر یک پیام صوتی در بله می‌فرستد، سیستم آن را به متن فارسی تبدیل می‌کند و در پایگاه دانش ذخیره می‌کند.

## How it works

```
Bale user ──voice──▶ Bot (python-telegram-bot, Bale API)
                        │ 1. get/create user, check admin approval
                        │ 2. create VoiceReport (pending)
                        │ 3. download .ogg to local storage
                        │ 4. transcribe with faster-whisper (Persian)
                        ▼
                 PostgreSQL ◀── FastAPI (users / voice-reports / health)
                 voice_reports + knowledge_entries (one commit)
```

## Features

- **Bale bot** with `/start`, `/help` and voice-message handling
- **Approval system**: new users are registered but cannot submit until approved; roles are `super_admin`, `domain_admin`, `operator`
- **Speech-to-text** in Persian using [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (`small` model, CPU, int8, VAD filter), run off the event loop
- **Report lifecycle** status: `pending → downloading → downloaded → transcribing → completed / failed`
- **Multi-domain knowledge base**: every report belongs to a domain (default seeded domain: `technical`); the transcript is saved as a `KnowledgeEntry` in the same transaction as the report completion
- **Async stack**: FastAPI, SQLAlchemy 2.0 (asyncpg), Alembic migrations, Pydantic v2 settings
- Docker Compose for PostgreSQL, Dockerfile for the API

## Tech stack

Python 3.12 · FastAPI · SQLAlchemy 2 (async) · PostgreSQL 16 · Alembic · python-telegram-bot (pointed at `tapi.bale.ai`) · faster-whisper · Docker

## Project structure

```
backend/
  app/
    api/v1/endpoints/   REST endpoints (users, voice-reports)
    bot/                Bale bot entrypoint and handlers
    core/config.py      Settings loaded from .env
    crud/               Database access layer
    db/                 Async engine and session
    models/             User, Domain, VoiceReport, KnowledgeEntry
    schemas/            Pydantic schemas
    services/           voice download + speech-to-text
    main.py             FastAPI app
  alembic/versions/     Database migrations
compose.yaml            PostgreSQL service
```

## Getting started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- A Bale bot token (create a bot via Bale's BotFather)

### 1. Configure

```bash
cp .env.example .env
```

Edit `.env` and set the database password. Add your bot token as well:

```env
BALE_BOT_TOKEN=<your bot token>
```

### 2. Start PostgreSQL

```bash
docker compose up -d postgres
```

### 3. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS
pip install -r backend/requirements.txt
pip install httpx faster-whisper
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Run the API and the bot (two terminals)

```bash
uvicorn backend.app.main:app --reload
```

```bash
python -m backend.app.bot.main
```

Interactive API docs: http://localhost:8000/docs

The first transcription downloads the Whisper model, so it takes a while.

### Approving users

New users start with `is_approved = false`. There is no admin UI yet, so approve a user directly in the database:

```sql
UPDATE users SET is_approved = true, role = 'super_admin' WHERE bale_user_id = <id>;
```

## API overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/db-check` | Live database connectivity check |
| POST | `/api/v1/users/` | Create or fetch a user by Bale ID |
| GET | `/api/v1/users/{bale_user_id}` | Get a user |
| POST | `/api/v1/voice-reports/` | Create a voice report record |
| GET | `/api/v1/voice-reports/user/{user_id}` | List a user's reports |

## Status and roadmap

This is a work in progress. Current limitations and planned work:

- API endpoints have no authentication yet
- No admin commands for approving users from inside the bot
- Failed reports are not yet marked `failed`, and retries are not implemented (`error_message` / `retry_count` columns exist)
- Searching and retrieving knowledge-base entries is not implemented yet
- The `tests/` package is empty

## License

No license specified.
