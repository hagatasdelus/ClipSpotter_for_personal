import discord
from discord.ext import commands
from myapp.constants import MIN_CLIP_FETCH_DAYS
from myapp.models import Category, DiscordModel, Visibility


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Successfully loaded : Status")
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="status", description="Display the current set streamer or game."
    )
    @discord.app_commands.describe(
        visibility="The visibility of the message (default: private)",
    )
    @discord.app_commands.choices(
        visibility=[
            discord.app_commands.Choice(name=vis.value, value=vis.value)
            for vis in Visibility.selectable_visibilities()
        ]
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
                "Not found guild info.", ephemeral=True
            )
            return
        if guild.category == Category.UNSELECTED or not guild.name:
            await interaction.response.send_message(
                "No settings found. Use the '/set' command to set a streamer or game.",
                ephemeral=True,
            )
        else:
            if guild.get_from is not None:
                await interaction.response.send_message(
                    f"Current {guild.category.display_name} set to: {guild.name}.\nSet to get clips from {guild.get_from} day{'s' if guild.get_from > MIN_CLIP_FETCH_DAYS else ''} ago.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"The number of days to get clips has not been set.\nPlease set the number of days to get clips from using the '/day' command.",
                    ephemeral=visibility.is_ephemeral,
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
