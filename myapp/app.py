import discord
from discord.ext import commands
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from collections.abc import AsyncGenerator
from typing import Any
from myapp import ACCESS_TOKEN, DATABASE_URL, Base


intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="cs$", case_insensitive=True, intents=intents)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
        await init_models()
        yield

    app = FastAPI(lifespan=lifespan)

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    return app


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def load_extensions():
    INITIAL_EXTENSIONS = [
        "myapp.cogs.set",
        "myapp.cogs.display",
        "myapp.cogs.day",
        "myapp.cogs.status",
        "myapp.cogs.remove",
        "myapp.cogs.cshelp",
    ]
    for cog in INITIAL_EXTENSIONS:
        await bot.load_extension(cog)


async def main():
    async with bot:
        await load_extensions()
        await bot.start(ACCESS_TOKEN)


@bot.event
async def on_ready():
    print("Bot is ready.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
