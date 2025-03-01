
# TeleForwarder

**TeleForwarder** project automatically forwards messages from one Telegram channel to one or more supergroups using a **single** user account (via Telethon). It also uses a bot  allowing dynamic settings (such as target groups, cron schedule, and forwarding modes) to be updated live via an admin Telegram bot interface.

## Features

- **Automatic Forwarding:** Fetch messages from a specified Telegram channel and forward them to multiple supergroups.
- **Sensitive Data via .env:** API credentials, channel username, and bot token are loaded from a `.env` file.
- **Dynamic Configuration:** Update supergroups, cron schedule, forward mode, and order through Telegram commands.
- **Forward Modes:**
  - **today:** Forward all messages from today.
  - **new:** Forward only messages that have not been forwarded yet.
- **Forward Order:**
  - **batch:** Forward all messages in one API call (if supported).
  - **one_by_one:** Forward messages individually with an optional delay.

- **Allowed Time Interval:**  
  Control the hours during which messages are forwarded.  
  - By default, forwarding is only enabled between 08:00 and 22:00.  
  - Use `/settimeinterval` to adjust the interval or disable it (set to "always") to forward messages at any time.

- **Admin Interface:**  
  Manage configuration using commands:
  - `/status` – View current configuration.
  - `/setgroups @group1, @group2` – Set a new list of supergroups.
  - `/addgroup @group` – Add a single group.
  - `/removegroup @group` – Remove a group.
  - `/setcron <cron_schedule>` – Update the cron schedule.
  - `/setmode <today|new>` – Change the forwarding mode.
  - `/setorder <batch|one_by_one>` – Change the forwarding order.
  - `/settimeinterval <always> OR /settimeinterval <start_hour> <end_hour>` – Set or disable the allowed time interval.


## Project Structure

```bash
├── .env              # Environment variables (API ID, hash, bot token)
├── config.json       # Dynamic config (source channel, supergroups, modes)
├── requirements.txt  # Python dependencies
└── src/
    ├── main.py  			#Entry point: logs in user, schedules forwarding, starts admin bot
    └── src/            
	    ├── envconfig.py         # Loads .env (API creds, bot token)
	    ├── config_manager.py    # Reads/writes config.json, handles last_forwarded_id
	    ├── single_user_forwarder.py
	    ├── admin_bot.py
	    └── user_sessions/       # Telethon session file (e.g. user1.session)
```

## Quick Start

**Clone the repository:**

```bash
   git clone https://github.com/yourusername/teleforwarder.git
   cd teleforwarder
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Set Up `.env`:**  
Provide your API credentials and bot token in `.env`:
```bash
TELEGRAM_BOT_TOKEN=123456:ABC-YourBotToken
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=YourApiHash

```
-   **Check `config.json`:**
    
    -   `source_channel`: The channel you’re fetching from (e.g. `"@my_source_channel"`).
    -   `supergroups`: A list of target groups or supergroups to forward to.
    -   `forward_mode`: Either `"today"` or `"new"`.
    -   `cron_schedule`: e.g. `"*/5 * * * *"` for every 5 minutes.
    -   `last_forwarded_id`: If using `"new"` mode, store the highest forwarded message ID here.
-   **Run:**
```bash
python src/main.py
```
    -   On first run, Telethon may prompt for a phone/code if no session file exists.
    -   Once logged in, the user session is saved in `src/user_sessions/user1.session`.

    
    

## Admin Bot Commands

Use these commands in your admin bot’s private chat to dynamically update configuration:

-   `/status` – Display the current `config.json`.
-   `/setchannel @somechannel` – Change the source channel.
-   `/setgroups @g1, @g2` – Overwrite the supergroups list.
-   `/setmode today|new` – Switch between re‐forwarding all day’s messages vs. forwarding only new.
-   `/settimeinterval always` or `/settimeinterval 8 22` – Disable or enable daily time window.
-   `/setcron "* * * * *"` – Update the cron schedule (run job every minute, etc.).




## Logging

-   The project uses Python’s `logging` module with a default level of `INFO`.
-   To see debug‐level logs (including raw HTTP requests from `python-telegram-bot`), set `level=logging.DEBUG` in `main.py`.

## Contributing

Feel free to submit pull requests or open issues to improve logging, add advanced filtering, or handle multi‐user scenarios.

Enjoy your single-user Telegram forwarder with chunked “today” mode and dynamic admin configuration!
