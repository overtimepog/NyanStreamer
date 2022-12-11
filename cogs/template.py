""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

from discord.ext import commands
from discord.ext.commands import Context
import discord
from discord import app_commands
from discord.ext import commands

from helpers import checks
from helpers import db_manager


# Here we name the cog and create a new class for the cog.
class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    #command to add a new streamer and their server and their ID to the database streamer table, using the add_streamer function from helpers\db_manager.py
    @commands.hybrid_command(
        name="addstreamer",
        description="This command will add a streamer to the database.",
    )
    @checks.is_owner()
    async def add_streamer(self, ctx: Context, streamer_channel: str, emoteprefix: str):
        """
        This command will add a streamer to the database.

        :param ctx: The context in which the command was called.
        :param streamer_channel: The channel of the streamer that should be added.
        :param server_id: The ID of the server where the streamer should be added.
        :param emotePrefix: The emote prefix for the streamer.
        """
        server_id = ctx.guild.id
        #check if the streamer already exists in the database
        streamers = await db_manager.view_streamers()
        for i in streamers:
            if streamer_channel in i:
                await ctx.send(f"{streamer_channel} already exists in the database.")
                return
        await db_manager.add_streamer(streamer_channel, server_id, emoteprefix)
        await ctx.send(f"Added {streamer_channel} to the database.")

    #command to veiw all streamers in the database streamer table, using the view_streamers function from helpers\db_manager.py
    @commands.hybrid_command(
        name="viewstreamers",
        description="This command will view all streamers in the database.",
    )
    @checks.is_owner()
    async def view_streamers(self, ctx: Context):
        """
        This command will view all streamers in the database.

        :param ctx: The context in which the command was called.
        """
        streamers = await db_manager.view_streamers()
        embed = discord.Embed(title="Streamers", description="All streamers in the database.", color=0x00ff00)
        for i in streamers:
            embed.add_field(name=i[0], value=i[1], inline=False)
        await ctx.send(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Template(bot))
