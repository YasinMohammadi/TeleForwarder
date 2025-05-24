
# TeleForwarder

**TeleForwarder ** is a _single-user_ Telegram forwarder that forwards messages from your channel to all/list of groups.

-   **Daily** mode – fetch all _text-only_ posts from today (Midnight → now, Asia/Tehran) and resend them to every target group in round-robin order, **60 s** apart.
    
-   **Listen** mode – stay connected to the source channel and forward each new _text_ post the moment it arrives.
    
-   Targets can be a **fixed list** (`TARGET_GROUPS`) or **every public group** the user account has joined (`FORWARD_TO=all`).
    
-   No admin bot, no interactive commands — _the entire runtime is driven by the `.env` file_.
    

----------

## Features

**Time-window**

Only forwards between `START_HOUR` ≤ local hour < `END_HOUR` (both in **Asia/Tehran** by default). Outside the window it logs `DEBUG` and sleeps.

**Pure text**

Any post that contains **media** is ignored. Forwarding uses `send_message` — never `forward_messages` — so no photos or files slip through.

**Round-robin pacing**

_Message 1_ → all groups → wait 60 s → _Message 2_ → … When the list ends it starts over (daily mode).

**Pluggable modes**

Switch via `FORWARD_MODE=daily

**Clean Architecture**

Core utilities → Domain → Infrastructure → Application (use-cases) → Framework (`main.py`).

**Logging**

`loguru` with file rotation (`forwarder.log`, 10 MB, 10 days).

**Typed**

Python 3.10+ with explicit type hints.

**Unit tests**

`pytest` & `pytest-asyncio`, stubbing Telethon so tests run offline.

## Project Layout

```txt
teleforwarder/
│
├── config.py                   ← pydantic-settings (Settings)
├── core/
│   ├── __init__.py
│   └── time_utils.py           ← start_of_today()
├── domain/
│   ├── model.py                ← TextMessage VO
│   └── services.py             ← round_robin()
├── infrastructure/
│   ├── logger_setup.py         ← adds loguru sink
│   └── telegram_gateway.py     ← Telethon wrapper
├── application/
│   └── use_cases.py            ← ForwardDailyTexts  &  ForwardOnNew
├── main.py                     ← bootstrap (select mode, schedule jobs)
└── __init__.py
tests/                           ← pytest suite (offline)
```

## Installation

```bash
git clone https://github.com/YasinMohammadi/teleforwarder.git
cd teleforwarder
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .   # editable install so package is on PYTHONPATH
```

## Environment Variables (`.env`)

```ini
# --- Telegram API credentials ---
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=abc123...

# --- Session file name ---
TELEGRAM_SESSION=user_session

# --- Forwarder behaviour ---
SOURCE_CHANNEL=@my_source_channel       # channel to read from
FORWARD_MODE=daily                      # daily | listen
FORWARD_TO=list                         # list | all
TARGET_GROUPS=@g1,@g2                   # comma-separated; ignored if FORWARD_TO=all

# --- Time & pacing ---
TIMEZONE=Asia/Tehran
START_HOUR=8
END_HOUR=22
SLEEP_BETWEEN_MESSAGES=60               # seconds between messages in a round

# --- Daily refresh cron (Tehran time) ---
CRON_SCHEDULE=0 0 * * *                 # midnight every day
```
_Leave `TARGET_GROUPS` empty if you’ll use `FORWARD_TO=all`._

----------

## Running
```bash
python -m teleforwarder.main
```

## License

MIT. Feel free to open issues & PRs.
