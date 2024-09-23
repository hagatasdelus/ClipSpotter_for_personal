import asyncio
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from typing import Any

import discord
from discord.ext import commands
from fastapi import FastAPI
from sqlalchemy.ext.declarative import declarative_base

from clipspotter import ACCESS_TOKEN
from clipspotter.config.config import engine, get_logger

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="cs$", case_insensitive=True, intents=intents)

Base = declarative_base()
logger = get_logger(__name__)


def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[Mapping[str, Any], None]:
        _ = app  # Unused variable
        await init_models()
        yield {}

    app = FastAPI(lifespan=lifespan)

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    return app


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def load_extensions():
    initial_extensions = [
        "clipspotter.cogs.set",
        "clipspotter.cogs.display",
        "clipspotter.cogs.clip_range",
        "clipspotter.cogs.status",
        "clipspotter.cogs.remove",
        "clipspotter.cogs.set_streamer",
        "clipspotter.cogs.cshelp",
    ]
    for cog in initial_extensions:
        await bot.load_extension(cog)


async def main():
    async with bot:
        await load_extensions()
        await bot.start(ACCESS_TOKEN)


@bot.event
async def on_ready():
    logger.info("Bot is ready.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
