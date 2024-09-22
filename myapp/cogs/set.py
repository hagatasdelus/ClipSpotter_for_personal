import discord
from discord.ext import commands

from myapp.api import TwitchAPI
from myapp.config import get_logger
from myapp.models import (
    Category,
    DiscordModel,
    TwitchGameModel,
    TwitchStreamerModel,
    Visibility,
)

logger = get_logger(__name__)


class Set(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = TwitchAPI()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Successfully loaded : Set")
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="set",
        description="Set the streamer (username) or game from which you want to get clips",
    )
    @discord.app_commands.describe(
        category="The category to set (Streamers or Games)",
        name="The name of the streamer (username) or game",
        visibility="The visibility of the message (default: private)",
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    @discord.app_commands.choices(
        category=[
            discord.app_commands.Choice(name=cat.display_name, value=cat.value)
            for cat in Category.selectable_categories()
        ],
        visibility=[
            discord.app_commands.Choice(name=vis.value, value=vis.value) for vis in Visibility.selectable_visibilities()
        ],
    )
    async def set_command(
        self,
        interaction: discord.Interaction,
        category: Category,
        name: str,
        visibility: Visibility = Visibility.PRIVATE,
    ):
        guild = await self.get_or_create_guild(interaction.guild_id)
        output_message, output_name = await self.register_category_item(category, name)
        if not output_name:
            await interaction.response.send_message(
                f"The {category.display_name} '{name}' was not found on Twitch.", ephemeral=True
            )
            return
        await guild.save_new_cat_settings(category, output_name)
        await interaction.response.send_message(
            output_message,
            ephemeral=visibility.is_ephemeral,
        )

    @set_command.error
    async def set_command_error(
        self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError
    ) -> None:
        if isinstance(error, discord.app_commands.AppCommandError):
            await interaction.response.send_message(
                "Please enter a valid username. The characters used in the user name should be A-Z, a-b, 0-9, or _.",
                ephemeral=True,
            )

    async def get_or_create_guild(self, guild_id) -> DiscordModel:
        guild = await DiscordModel.select_guild_by_guild_id(guild_id)
        if guild is None:
            guild = await DiscordModel.create_new_guild(guild_id)
        return guild

    async def register_category_item(self, category: Category, input_name: str) -> tuple[str | None, str | None]:
        if category == Category.STREAMER:
            return await self.register_streamer(input_name)
        return await self.register_game(input_name)

    async def register_streamer(self, input_name: str) -> tuple[str | None, str | None]:
        existing_streamer = await TwitchStreamerModel.select_by_name(input_name)
        if existing_streamer:
            return (
                self.format_streamer_message(
                    existing_streamer.streamer_name,
                    existing_streamer.streamer_display_name,
                ),
                existing_streamer.streamer_name,
            )

        set_id, name, display_name = self.api.get_broadcaster_id(input_name)
        if not set_id or not name or not display_name:
            return None, None
        await TwitchStreamerModel.create(
            streamer_name=name,
            streamer_id=set_id,
            streamer_display_name=display_name,
        )
        return self.format_streamer_message(name, display_name), name

    async def register_game(self, input_name: str) -> tuple[str | None, str | None]:
        existing_game = await TwitchGameModel.select_by_normalized_name(input_name)
        if existing_game:
            return (
                self.format_game_message(existing_game.game_name),
                existing_game.game_name,
            )

        set_id, name = self.api.get_game_id(input_name)
        if not set_id:
            return None, None
        await TwitchGameModel.create(game_name=name, game_id=set_id)
        return self.format_game_message(name), name

    def format_streamer_message(self, name, display_name) -> str:
        base_string = f"Successfully set {Category.STREAMER.display_name} to: "
        if name == display_name:
            return base_string + name
        return base_string + f"{display_name}({name})"

    def format_game_message(self, name) -> str:
        return f"Successfully set {Category.GAME.display_name} to: {name}"


async def setup(bot: commands.Bot):
    await bot.add_cog(Set(bot))
