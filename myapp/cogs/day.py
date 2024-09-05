import discord
from discord.ext import commands
from myapp.models import DiscordModel
from myapp.constants import MAX_CLIP_FETCH_DAYS, MIN_CLIP_FETCH_DAYS


class GetFrom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Successfully loaded : Day")
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="day", description="Set the number of days to get clips from."
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    async def get_from_command(self, interaction: discord.Interaction, get_from: int):
        if get_from < MIN_CLIP_FETCH_DAYS or get_from > MAX_CLIP_FETCH_DAYS:
            await interaction.response.send_message(
                f"Invalid those days: {get_from}. Please provide less than 5 years(1825 days).",
                ephemeral=True,
            )
            return
        guild = await DiscordModel.select_guild_by_guild_id(interaction.guild_id)
        if not guild:
            await interaction.response.send_message(
                "Not found guild info.", ephemeral=True
            )
            return
        await guild.update_days_by_guild_id(get_from=get_from)
        await interaction.response.send_message(
            f"Set to get clips from {get_from} day{'s' if get_from > MIN_CLIP_FETCH_DAYS else ''} ago.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(GetFrom(bot))
