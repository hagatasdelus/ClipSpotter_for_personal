import discord
from discord.ext import commands

from clipspotter.api import TwitchAPI
from clipspotter.config import MAX_CLIPS_TO_FETCH, MIN_CLIPS_TO_FETCH, get_logger
from clipspotter.models import (
    Category,
    DiscordModel,
    TwitchGameModel,
    TwitchStreamerModel,
    Visibility,
)

logger = get_logger(__name__)


class Display(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_api = TwitchAPI()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Successfully loaded : Display")
        await self.bot.tree.sync()

    @discord.app_commands.command(name="display", description="Display clips from the set streamer or game")
    @discord.app_commands.describe(
        num_clips="The number of clips to display",
        visibility="The visibility of the message (default: private)",
    )
    @discord.app_commands.choices(
        visibility=[
            discord.app_commands.Choice(name=vis.value, value=vis.value) for vis in Visibility.selectable_visibilities()
        ],
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    async def display(
        self,
        interaction: discord.Interaction,
        num_clips: discord.app_commands.Range[int, MIN_CLIPS_TO_FETCH, MAX_CLIPS_TO_FETCH],
        visibility: Visibility = Visibility.PRIVATE,
    ):
        guild = await DiscordModel.select_guild_by_guild_id(interaction.guild_id)
        if not guild:
            await interaction.response.send_message(
                "Not found guild info. Please set the streamer or game using the '/set' command.",
                ephemeral=True,
            )
            return
        if not guild.days_ago:
            await interaction.response.send_message(
                "Guild information is not propertly set.\n"
                "Please set the number of days to get clips from using the '/clip-range' command.",
                ephemeral=True,
            )
            return
        set_id = await self.get_set_id(guild)
        if not set_id:
            await interaction.response.send_message(
                "No streamer or game set.\nPlease set the streamer or game using the '/set' command.",
                ephemeral=True,
            )
            return
        clips = await self.fetch_clips(guild, set_id, num_clips)
        if not clips:
            await interaction.response.send_message("No clips found.", ephemeral=True)
            return

        await self.send_clips(interaction, clips, visibility)

    async def get_set_id(self, guild) -> str | None:
        if guild.category == Category.STREAMER:
            streamer_info = await TwitchStreamerModel.select_by_name(guild.name)
            return streamer_info.streamer_id if streamer_info else None
        game_info = await TwitchGameModel.select_by_name(guild.name)
        return game_info.game_id if game_info else None

    async def fetch_clips(self, guild, set_id, num_clips):
        return self.twitch_api.get_clips(
            category=guild.category,
            set_id=set_id,
            days_ago=guild.days_ago,
            first=num_clips,
        )

    async def send_clips(self, interaction: discord.Interaction, clips, visibility: Visibility):
        await interaction.response.send_message(
            f"Found {len(clips)} clips. Sending them now...",
            ephemeral=visibility.is_ephemeral,
        )
        for i, clip in enumerate(clips, 1):
            await interaction.followup.send(f"Clip {i}: {clip['url']}", ephemeral=visibility.is_ephemeral)


async def setup(bot: commands.Bot):
    await bot.add_cog(Display(bot))
