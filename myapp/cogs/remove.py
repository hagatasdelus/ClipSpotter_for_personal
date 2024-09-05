import discord
from discord.ext import commands
from myapp.models import Category, DiscordModel


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Successfully loaded : Remove")
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="remove", description="Remove the current settings."
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    async def remove_command(self, interaction: discord.Interaction):
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
            return
        await guild.remove_cat_settings()
        await interaction.response.send_message(
            "Removed current settings. Please set again.", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Remove(bot))
