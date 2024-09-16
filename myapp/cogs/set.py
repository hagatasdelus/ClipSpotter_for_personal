import discord
from discord.ext import commands
from myapp.api import TwitchAPI
from myapp.models import (
    Category,
    DiscordModel,
    TwitchGameModel,
    TwitchStreamerModel,
    Visibility,
)


class SetError(Exception):
    pass


class Set(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = TwitchAPI()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Successfully loaded : Set")
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="set",
        description="Set the streamer (username) or game from which you want to get clips",
    )
    @discord.app_commands.describe(
        category="The category to set (Streamers or Games)",
        username="The name of the streamer (username) or game",
        visibility="The visibility of the message (default: private)",
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    @discord.app_commands.choices(
        category=[
            discord.app_commands.Choice(name=cat.display_name, value=cat.value)
            for cat in Category.selectable_categories()
        ],
        visibility=[
            discord.app_commands.Choice(name=vis.value, value=vis.value)
            for vis in Visibility.selectable_visibilities()
        ],
    )
    async def set_command(
        self,
        interaction: discord.Interaction,
        category: Category,
        username: str,
        visibility: Visibility = Visibility.PRIVATE,
    ):
        guild = await self.get_or_create_guild(interaction.guild_id)
        try:
            output_message, output_name = await self.register_category_item(
                interaction, category, username
            )
            await guild.save_new_cat_settings(category, output_name)
            await interaction.response.send_message(
                output_message,
                ephemeral=visibility.is_ephemeral,
            )
        except SetError:
            pass

    async def get_or_create_guild(self, guild_id):
        guild = await DiscordModel.select_guild_by_guild_id(guild_id)
        if guild is None:
            guild = await DiscordModel.create_new_guild(guild_id)
        return guild

    async def register_category_item(
        self, interaction: discord.Interaction, category: Category, input_name: str
    ):
        if category == Category.STREAMER:
            return await self.register_streamer(interaction, input_name)
        elif category == Category.GAME:
            return await self.register_game(interaction, input_name)
        else:
            raise ValueError(f"Invalid category: {category}")

    async def register_streamer(
        self, interaction: discord.Interaction, input_name: str
    ):
        existing_streamer = await TwitchStreamerModel.select_by_name(input_name)
        if existing_streamer:
            return (
                self.format_streamer_message(
                    existing_streamer.streamer_name,
                    existing_streamer.streamer_display_name,
                ),
                existing_streamer.streamer_name,
            )

        try:
            set_id, name, display_name = self.api.get_broadcaster_id(input_name)
            await TwitchStreamerModel.create(
                streamer_name=name,
                streamer_id=set_id,
                streamer_display_name=display_name,
            )
            return self.format_streamer_message(name, display_name), name
        except ValueError:
            await interaction.response.send_message(
                f"The streamer {input_name} was not found on Twitch.",
                ephemeral=True,
            )
            raise SetError("Name not found")

    async def register_game(self, interaction: discord.Interaction, input_name: str):
        existing_game = await TwitchGameModel.select_by_normalized_name(input_name)
        if existing_game:
            return (
                self.format_game_message(existing_game.game_name),
                existing_game.game_name,
            )

        try:
            set_id, name = self.api.get_game_id(input_name)
            await TwitchGameModel.create(game_name=name, game_id=set_id)
            return self.format_game_message(name), name
        except ValueError:
            await interaction.response.send_message(
                f"The game {input_name} was not found on Twitch.",
                ephemeral=True,
            )
            raise SetError("Name not found")

    def format_streamer_message(self, name, display_name):
        base_string = f"Successfully set {Category.STREAMER.display_name} to: "
        if name == display_name:
            return base_string + name
        else:
            return base_string + f"{display_name}({name})"

    def format_game_message(self, name):
        return f"Successfully set {Category.GAME.display_name} to: {name}"


async def setup(bot: commands.Bot):
    await bot.add_cog(Set(bot))
