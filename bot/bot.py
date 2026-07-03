import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from api_client import BackendClient
from llm_rewriter import LlmRewriter
from response_formatter import format_alert, format_room, format_status, format_usage


load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000").strip()
DISCORD_ALERT_CHANNEL_ID = os.getenv("DISCORD_ALERT_CHANNEL_ID", "").strip()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
backend = BackendClient(BACKEND_BASE_URL)
rewriter = LlmRewriter()
posted_alert_ids: set[str] = set()


async def maybe_rewrite(answer: str) -> str:
    return await rewriter.rewrite(answer)


@bot.event
async def on_ready() -> None:
    print(f"Smart Office bot logged in as {bot.user}")
    if DISCORD_ALERT_CHANNEL_ID and not alert_watcher.is_running():
        alert_watcher.start()


@bot.command(name="status")
async def status_command(ctx: commands.Context) -> None:
    try:
        answer = format_status(await backend.get_state())
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await ctx.reply(f"I couldn't reach the office backend right now: {exc}", mention_author=False)


@bot.command(name="room")
async def room_command(ctx: commands.Context, room_name: str | None = None) -> None:
    if not room_name:
        await ctx.reply("Tell me a room to check. Try: drawing, work1, or work2.", mention_author=False)
        return

    try:
        answer = format_room(await backend.get_room(room_name))
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except ValueError:
        await ctx.reply("I couldn't find that room. Try: drawing, work1, or work2.", mention_author=False)
    except Exception as exc:
        await ctx.reply(f"I couldn't reach the office backend right now: {exc}", mention_author=False)


@bot.command(name="usage")
async def usage_command(ctx: commands.Context) -> None:
    try:
        answer = format_usage(await backend.get_usage())
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await ctx.reply(f"I couldn't reach the office backend right now: {exc}", mention_author=False)


@tasks.loop(seconds=10)
async def alert_watcher() -> None:
    if not DISCORD_ALERT_CHANNEL_ID:
        return

    channel = bot.get_channel(int(DISCORD_ALERT_CHANNEL_ID))
    if channel is None:
        return

    try:
        alerts = (await backend.get_alerts()).get("activeAlerts", [])
    except Exception:
        return

    for alert in alerts:
        if alert["id"] in posted_alert_ids:
            continue
        posted_alert_ids.add(alert["id"])
        await channel.send(await maybe_rewrite(format_alert(alert)))


def main() -> None:
    if not DISCORD_BOT_TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is not set. Add it to your environment or .env file.")
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
