import discord
from discord.ext import commands
from myapp.models import Category, DiscordModel, TwitchStreamerModel, Visibility


class SetStreamer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Successfully loaded : SetStreamer")
        await self.bot.tree.sync()

    @discord.app_commands.command(
        name="set-streamer",
        description="Set the streamer to get clips by display name. (Streamers only)",
    )
    @discord.app_commands.describe(
        display_name="The name of the streamer (display name)",
        visibility="The visibility of the message (default: private)",
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    @discord.app_commands.choices(
        visibility=[
            discord.app_commands.Choice(name=vis.value, value=vis.value)
            for vis in Visibility.selectable_visibilities()
        ],
    )
    async def set_streamer_command(
        self,
        interaction: discord.Interaction,
        display_name: str,
        visibility: Visibility = Visibility.PRIVATE,
    ):
        guild = await self.get_or_create_guild(interaction.guild_id)
        try:
            output_streamer = await self.get_registered_streamer(display_name)
            await guild.save_new_cat_settings(
                Category.STREAMER, output_streamer.streamer_name
            )
            await interaction.response.send_message(
                self.format_streamer_message(
                    output_streamer.streamer_name, output_streamer.streamer_display_name
                ),
                ephemeral=visibility.is_ephemeral,
            )
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

    async def get_or_create_guild(self, guild_id):
        guild = await DiscordModel.select_guild_by_guild_id(guild_id)
        if guild is None:
            guild = await DiscordModel.create_new_guild(guild_id)
        return guild

    async def get_registered_streamer(self, input_name: str):
        existing_streamer = await TwitchStreamerModel.select_by_display_name(input_name)
        if existing_streamer:
            return existing_streamer
        raise ValueError(
            f"Streamer not found: {input_name}. Initially, use /set to register by user name, not display name."
        )

    def format_streamer_message(self, name, display_name):
        base_string = f"Successfully set {Category.STREAMER.display_name} to: "
        if name == display_name:
            return base_string + name
        else:
            return base_string + f"{display_name}({name})"


async def setup(bot: commands.Bot):
    await bot.add_cog(SetStreamer(bot))
