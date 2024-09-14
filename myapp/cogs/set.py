import discord
import requests
from discord.ext import commands
from myapp.api import TwitchAPI
from myapp.models import Category, DiscordModel, TwitchGameModel, TwitchStreamerModel


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
        description="Set the streamer or game to get clips from.",
    )
    @discord.app_commands.describe(
        category="The category to set (Streamers or Games)",
        name="The name of the streamer or game",
    )
    @discord.app_commands.checks.has_permissions(use_application_commands=True)
    @discord.app_commands.choices(
        category=[
            discord.app_commands.Choice(name=cat.display_name, value=cat.value)
            for cat in Category.selectable_categories()
        ]
    )
    async def set(self, interaction: discord.Interaction, category: str, name: str):
        category_enum = Category.from_string(category)
        if category_enum is None:
            await interaction.response.send_message(
                f"Invalid category: {category}", ephemeral=True
            )
            return

        guild = await self.get_or_create_guild(interaction.guild_id)
        try:
            output_name = await self.register_category_item(
                interaction, category_enum, name
            )
            await guild.save_new_cat_settings(category_enum, output_name)
            await interaction.response.send_message(
                f"Successfully set {category_enum.display_name} to: {output_name}",
                ephemeral=True,
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
            output_name = await self.register_streamer(interaction, input_name)
        elif category == Category.GAME:
            output_name = await self.register_game(interaction, input_name)
        else:
            raise ValueError(f"Invalid category: {category}")
        return output_name

    async def register_streamer(
        self, interaction: discord.Interaction, input_name: str
    ):
        existing_streamer = await TwitchStreamerModel.select_by_name(input_name)
        if existing_streamer:
            return existing_streamer.streamer_name

        try:
            set_id, name = self.api.get_broadcaster_id(input_name)
            await TwitchStreamerModel.create(streamer_name=name, streamer_id=set_id)
            return name
        except ValueError:
            await interaction.response.send_message(
                f"Error: The streamer {input_name} was not found on Twitch.",
                ephemeral=True,
            )
            raise SetError("Name not found")
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP Error occurred: {str(http_err)}")
            await interaction.response.send_message(
                f"An error occurred while communicating with Twitch. Please try again later.",
                ephemeral=True,
            )
            raise SetError("HTTP Error")
        except Exception as e:
            print(f"❌ Unexpected error registering streamer: {str(e)}")
            await interaction.response.send_message(
                f"An unexpected error occurred while registering streamer: {input_name}.",
                ephemeral=True,
            )
            raise SetError("Unexpected Error")

    async def register_game(self, interaction: discord.Interaction, input_name: str):
        existing_game = await TwitchGameModel.select_by_normalized_name(input_name)
        if existing_game:
            return existing_game.game_name

        try:
            set_id, name = self.api.get_game_id(input_name)
            await TwitchGameModel.create(game_name=name, game_id=set_id)
            return name
        except ValueError:
            await interaction.response.send_message(
                f"Error: The game {input_name} was not found on Twitch.",
                ephemeral=True,
            )
            raise SetError("Name not found")
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP Error occurred: {str(http_err)}")
            await interaction.response.send_message(
                f"An error occurred while communicating with Twitch. Please try again later.",
                ephemeral=True,
            )
            raise SetError("HTTP Error")
        except Exception as e:
            print(f"❌ Unexpected error registering game: {str(e)}")
            await interaction.response.send_message(
                f"An unexpected error occurred while registering game: {input_name}.",
                ephemeral=True,
            )
            raise SetError("Unexpected Error")


async def setup(bot: commands.Bot):
    await bot.add_cog(Set(bot))
