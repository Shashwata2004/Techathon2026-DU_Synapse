# Discord Bot

The bot reads live data from the FastAPI backend. It does not store device state.

## Setup

```bash
cd bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

On Windows:

```bash
venv\Scripts\activate
python bot.py
```

## Environment

Set these in your shell or a `.env` file:

```env
DISCORD_BOT_TOKEN=
BACKEND_BASE_URL=http://localhost:8000
DISCORD_ALERT_CHANNEL_ID=
OPENAI_API_KEY=
```

`OPENAI_API_KEY` and `DISCORD_ALERT_CHANNEL_ID` are optional. Without them, the core `!status`, `!room`, and `!usage` commands still work.

## Commands

- `!status`
- `!room drawing`
- `!room work1`
- `!room work2`
- `!usage`
