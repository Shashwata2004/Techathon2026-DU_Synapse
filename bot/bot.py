import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from api_client import BackendClient
from llm_rewriter import LlmRewriter
from response_formatter import (
    format_alerts,
    format_help_text,
    format_proactive_alert,
    format_recommendation,
    format_reset_result,
    format_room,
    format_room_power_result,
    format_status,
    format_summary,
    format_toggle_result,
    format_top,
    format_usage,
    format_waste,
    resolve_device_id,
    resolve_room_id,
)


load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000").strip()
DISCORD_ALERT_CHANNEL_ID = os.getenv("DISCORD_ALERT_CHANNEL_ID", "").strip()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
backend = BackendClient(BACKEND_BASE_URL)
rewriter = LlmRewriter()
posted_alert_ids: set[str] = set()


async def maybe_rewrite(answer: str) -> str:
    return await rewriter.rewrite(answer)


async def reply_backend_error(ctx: commands.Context, exc: Exception) -> None:
    await ctx.reply(f"I couldn't reach the office backend right now: {exc}", mention_author=False)


@bot.event
async def on_ready() -> None:
    print(f"Smart Office bot logged in as {bot.user}")
    if DISCORD_ALERT_CHANNEL_ID and not alert_watcher.is_running():
        alert_watcher.start()
    elif not DISCORD_ALERT_CHANNEL_ID:
        print("Proactive Discord alerts disabled: DISCORD_ALERT_CHANNEL_ID is not set.")


@bot.command(name="help")
async def help_command(ctx: commands.Context) -> None:
    await ctx.reply(format_help_text(), mention_author=False)


@bot.command(name="status")
async def status_command(ctx: commands.Context) -> None:
    try:
        answer = format_status(await backend.get_state())
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


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
        await reply_backend_error(ctx, exc)


@bot.command(name="usage")
async def usage_command(ctx: commands.Context) -> None:
    try:
        answer = format_usage(await backend.get_usage())
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="alerts")
async def alerts_command(ctx: commands.Context) -> None:
    try:
        answer = format_alerts(await backend.get_alerts())
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="summary")
async def summary_command(ctx: commands.Context) -> None:
    try:
        answer = format_summary(await backend.get_state())
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="waste")
async def waste_command(ctx: commands.Context, hours: str | None = None) -> None:
    try:
        parsed_hours = float(hours) if hours is not None else 3.0
    except ValueError:
        await ctx.reply("Use a positive number of hours. Example: !waste 3", mention_author=False)
        return

    if parsed_hours <= 0:
        await ctx.reply("Use a positive number of hours. Example: !waste 3", mention_author=False)
        return

    try:
        answer = format_waste(await backend.get_usage(), parsed_hours)
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="recommend")
async def recommend_command(ctx: commands.Context) -> None:
    try:
        answer = format_recommendation(await backend.get_state())
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="top")
async def top_command(ctx: commands.Context) -> None:
    try:
        answer = format_top(await backend.get_usage())
        await ctx.reply(await maybe_rewrite(answer), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="toggle")
async def toggle_command(ctx: commands.Context, room_name: str | None = None, device_name: str | None = None) -> None:
    if not room_name or not device_name:
        await ctx.reply("Use: !toggle work1 fan1", mention_author=False)
        return

    try:
        room_id = resolve_room_id(room_name)
        device_id = resolve_device_id(room_name, device_name)
    except ValueError as exc:
        if str(exc) == "invalid_device":
            await ctx.reply("I couldn't find that device. Try: fan1, fan2, light1, light2, or light3.", mention_author=False)
        else:
            await ctx.reply("I couldn't find that room. Try: drawing, work1, or work2.", mention_author=False)
        return

    try:
        await backend.toggle_device(device_id)
        room = await backend.get_room(room_id)
        await ctx.reply(await maybe_rewrite(format_toggle_result(room, device_id)), mention_author=False)
    except ValueError:
        await ctx.reply("I couldn't find that room or device.", mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="roomon")
async def room_on_command(ctx: commands.Context, room_name: str | None = None) -> None:
    if not room_name:
        await ctx.reply("Use: !roomon work2", mention_author=False)
        return

    try:
        room_id = resolve_room_id(room_name)
    except ValueError:
        await ctx.reply("I couldn't find that room. Try: drawing, work1, or work2.", mention_author=False)
        return

    try:
        await backend.set_room_all_on(room_id)
        room = await backend.get_room(room_id)
        await ctx.reply(await maybe_rewrite(format_room_power_result(room, "ON")), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="roomoff")
async def room_off_command(ctx: commands.Context, room_name: str | None = None) -> None:
    if not room_name:
        await ctx.reply("Use: !roomoff drawing", mention_author=False)
        return

    try:
        room_id = resolve_room_id(room_name)
    except ValueError:
        await ctx.reply("I couldn't find that room. Try: drawing, work1, or work2.", mention_author=False)
        return

    try:
        await backend.set_room_all_off(room_id)
        room = await backend.get_room(room_id)
        await ctx.reply(await maybe_rewrite(format_room_power_result(room, "OFF")), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@bot.command(name="resetdemo")
async def reset_demo_command(ctx: commands.Context) -> None:
    try:
        await backend.reset_demo()
        state = await backend.get_state()
        await ctx.reply(await maybe_rewrite(format_reset_result(state)), mention_author=False)
    except Exception as exc:
        await reply_backend_error(ctx, exc)


@tasks.loop(seconds=45)
async def alert_watcher() -> None:
    if not DISCORD_ALERT_CHANNEL_ID:
        return

    try:
        channel_id = int(DISCORD_ALERT_CHANNEL_ID)
    except ValueError:
        print("Invalid DISCORD_ALERT_CHANNEL_ID. Proactive alerts are disabled.")
        return

    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception:
            return

    try:
        alerts = (await backend.get_alerts()).get("activeAlerts", [])
    except Exception:
        return

    for alert in alerts:
        if alert["id"] in posted_alert_ids:
            continue
        posted_alert_ids.add(alert["id"])
        await channel.send(await maybe_rewrite(format_proactive_alert(alert)))


def main() -> None:
    if not DISCORD_BOT_TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is not set. Add it to your environment or .env file.")
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
