import discord
from discord.ext import commands

from myapp.config import get_logger
from myapp.constants import MAX_CLIP_FETCH_DAYS, MIN_CLIP_FETCH_DAYS
from myapp.models import DiscordModel, Visibility

logger = get_logger(__name__)


class ClipRange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Successfully loaded : ClipRange")
        await self.bot.tree.sync()

    @discord.app_commands.command(name="clip-range", description="Set the number of days to get clips from.")
    @discord.app_commands.describe(
        days_ago="The number of days to get clips from.",
        visibility="The visibility of the message (default: private)",
    )
    @discord.app_commands.choices(
        visibility=[
            discord.app_commands.Choice(name=vis.value, value=vis.value) for vis in Visibility.selectable_visibilities()
        ],
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    async def clip_range_command(
        self,
        interaction: discord.Interaction,
        days_ago: discord.app_commands.Range[int, MIN_CLIP_FETCH_DAYS, MAX_CLIP_FETCH_DAYS],
        visibility: Visibility = Visibility.PRIVATE,
    ):
        guild = await DiscordModel.select_guild_by_guild_id(interaction.guild_id)
        if not guild:
            await interaction.response.send_message(
                "Not found guild info. Please set the streamer or game using the '/set' command.", ephemeral=True
            )
            return
        await guild.update_days_by_guild_id(days_ago=days_ago)
        await interaction.response.send_message(
            f"Set to get clips from {days_ago} day{'s' if days_ago > MIN_CLIP_FETCH_DAYS else ''} ago.",
            ephemeral=visibility.is_ephemeral,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ClipRange(bot))
