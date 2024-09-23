import discord
from discord.ext import commands

from clipspotter.config import MIN_CLIP_FETCH_DAYS, get_logger
from clipspotter.models import Category, DiscordModel, TwitchStreamerModel, Visibility

logger = get_logger(__name__)


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Successfully loaded : Status")
        await self.bot.tree.sync()

    @discord.app_commands.command(name="status", description="Display the current set streamer or game")
    @discord.app_commands.describe(
        visibility="The visibility of the message (default: private)",
    )
    @discord.app_commands.choices(
        visibility=[
            discord.app_commands.Choice(name=vis.value, value=vis.value) for vis in Visibility.selectable_visibilities()
        ],
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    async def status_command(
        self,
        interaction: discord.Interaction,
        visibility: Visibility = Visibility.PRIVATE,
    ):
        guild = await DiscordModel.select_guild_by_guild_id(interaction.guild_id)
        if not guild:
            await interaction.response.send_message(
                "Not found guild info. Please set the streamer or game using the '/set' command.", ephemeral=True
            )
            return
        if guild.category == Category.UNSELECTED or not guild.name:
            await interaction.response.send_message(
                "No settings found. Use the '/set' command to set a streamer or game.",
                ephemeral=True,
            )
            return
        if guild.days_ago is not None:
            name_status = await self.get_name(guild)
            await interaction.response.send_message(
                f"Current {guild.category.display_name} set to: {name_status}.\n"
                f"Set to get clips from {guild.days_ago} day{'s' if guild.days_ago > MIN_CLIP_FETCH_DAYS else ''} ago.",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            "The number of days to get clips has not been set.\n"
            "Please set the number of days to get clips from using the '/clip-range' command.",
            ephemeral=visibility.is_ephemeral,
        )

    async def get_name(self, guild):
        if guild.category == Category.STREAMER:
            streamer = await TwitchStreamerModel.select_by_name(guild.name)
            if streamer:
                return f"{streamer.streamer_display_name}({streamer.streamer_name})"
        return guild.name


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
