import discord
from discord.ext import commands
from myapp.api import TwitchAPI
from myapp.constants import MAX_CLIPS_TO_FETCH, MIN_CLIPS_TO_FETCH
from myapp.models import Category, DiscordModel, TwitchGameModel, TwitchStreamerModel


class Display(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_api = TwitchAPI()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Successfully loaded : Display")
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="display", description="Display clips from the set streamer or game."
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    async def display(self, interaction: discord.Interaction, num_clips: int):
        if not self.validate_input(num_clips):
            await interaction.response.send_message(
                f"Please provide a number between {MIN_CLIPS_TO_FETCH} and {MAX_CLIPS_TO_FETCH}.",
                ephemeral=True,
            )
            return
        guild = await DiscordModel.select_guild_by_guild_id(interaction.guild_id)
        if not guild:
            await interaction.response.send_message(
                "Not found guild info.", ephemeral=True
            )
            return
        if not guild.get_from:
            await interaction.response.send_message(
                "Guild information is not propertly set.\nPlease set the number of days to get clips from using the '/day' command.",
                ephemeral=True,
            )
        set_id = await self.get_set_id(guild)
        clips = await self.fetch_clips(guild, set_id, num_clips)
        if not clips:
            await interaction.response.send_message("No clips found.", ephemeral=True)
            return

        await self.send_clips(interaction, clips)

    def validate_input(self, num_clips: int) -> bool:
        return MIN_CLIPS_TO_FETCH <= num_clips <= MAX_CLIPS_TO_FETCH

    async def get_set_id(self, guild):
        if guild.category == Category.STREAMER:
            set_info = await TwitchStreamerModel.select_by_name(guild.name)
            return set_info.streamer_id
        else:
            set_info = await TwitchGameModel.select_by_name(guild.name)
            return set_info.game_id

    async def fetch_clips(self, guild, set_id, num_clips):
        return self.twitch_api.get_clips(
            category=guild.category,
            set_id=set_id,
            get_from=guild.get_from,
            first=num_clips,
        )

    async def send_clips(self, interaction: discord.Interaction, clips):
        await interaction.response.send_message(
            f"Found {len(clips)} clips. Sending them now...", ephemeral=True
        )
        for i, clip in enumerate(clips, 1):
            await interaction.followup.send(f"Clip {i}: {clip['url']}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Display(bot))
