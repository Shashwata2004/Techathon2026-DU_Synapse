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

`OPENAI_API_KEY` and `DISCORD_ALERT_CHANNEL_ID` are optional. Without them, the bot commands still work, but LLM rewriting and proactive alert posting are disabled.

The bot is command-driven. Every command fetches fresh data from the backend instead of storing device state in the bot. Optional proactive alert posting polls alerts every 45 seconds only when `DISCORD_ALERT_CHANNEL_ID` is configured.

## Proactive Alert Setup

1. Open Discord user settings.
2. Go to Advanced.
3. Enable Developer Mode.
4. Right-click the alert channel.
5. Click Copy Channel ID.
6. Put that value in `.env`:

```env
DISCORD_ALERT_CHANNEL_ID=
```

Leave `DISCORD_ALERT_CHANNEL_ID` empty to disable proactive alert posting.

## Commands

- `!help` - show all commands
- `!status` - full office status
- `!room <room>` - check one room
- `!room drawing` - check Drawing Room
- `!room work1` - check Work Room 1
- `!room work2` - check Work Room 2
- `!usage` - current power usage
- `!alerts` - show active alerts
- `!summary` - boss-friendly quick summary
- `!waste <hours>` - estimate waste for a time period
- `!recommend` - energy-saving recommendation
- `!top` - highest consuming room or rooms
- `!toggle <room> <device>` - toggle one device through the backend
- `!roomon <room>` - turn all devices in a room ON
- `!roomoff <room>` - turn all devices in a room OFF
- `!resetdemo` - reset demo state

Examples: `!waste 3`, `!toggle work1 fan1`, `!roomon work2`, `!roomoff drawing`
