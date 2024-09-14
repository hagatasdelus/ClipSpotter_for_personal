import json

import discord
from discord.ext import commands


class CSHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("myapp/help_data.json", "r") as f:
            self.help_data = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Successfully loaded : Help")
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="help", description="Display the help information."
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=self.help_data["title"],
            description=self.help_data["description"],
            color=getattr(discord.Color, self.help_data["color"])(),
        )

        # General Usage note
        embed.add_field(
            name=self.help_data["general_usage"]["name"],
            value=self.help_data["general_usage"]["value"],
            inline=False,
        )

        # Commands
        for command in self.help_data["commands"]:
            embed.add_field(name=command["name"], value=command["value"], inline=False)
            if "usage" in command:
                embed.add_field(name="Usage", value=command["usage"], inline=False)
            if "categories" in command:
                embed.add_field(
                    name="Categories", value=command["categories"], inline=False
                )
            if "example" in command:
                embed.add_field(name="Example", value=command["example"], inline=False)

        # Note
        embed.add_field(
            name=self.help_data["note"]["name"],
            value=self.help_data["note"]["value"],
            inline=False,
        )

        # Attention
        embed.add_field(
            name=self.help_data["attention"]["name"],
            value=self.help_data["attention"]["value"],
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CSHelp(bot))
