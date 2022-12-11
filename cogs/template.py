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
        user_id = ctx.message.author.id
        #check if the streamer already exists in the database
        streamers = await db_manager.view_streamers()
        for i in streamers:
            if streamer_channel in i or user_id in i or emoteprefix in i:
                await ctx.send(f"{streamer_channel} already exists in the database.")
                return
        await db_manager.add_streamer(streamer_channel, user_id, emoteprefix)
        await ctx.send(f"Added {streamer_channel} to the database, with the ID {emoteprefix}.") 

    #command to remove a streamer from the database streamer table, using the remove_streamer function from helpers\db_manager.py
    @commands.hybrid_command(
        name="removestreamer",
        description="This command will remove a streamer from the database.",
    )
    @checks.is_owner()
    async def remove_streamer(self, ctx: Context):
        """
        This command will remove a streamer from the database.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        #check if the streamer exists in the database
        streamers = await db_manager.view_streamers()
        print(streamers)
        for i in streamers:
            user_id = int(user_id)
            streamerUser_id = int(i[2])
            if user_id == streamerUser_id:
                await db_manager.remove_streamer(user_id)
                await ctx.send(f"Removed {i[0]} from the database.")
                return
        await ctx.send(f"You don't have any streamers in the database.")
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

    #command to create a new item in the database item table, using the add_item function from helpers\db_manager.py
    @commands.hybrid_command(
        name="creatitem",
        description="This command will create a new item in the database.",
    )
    @checks.is_owner()
    async def create_item(self, ctx: Context, item_name: str, item_price: int, item_emote: discord.Emoji):
        """
        This command will create a new item in the database.

        :param ctx: The context in which the command was called.
        :param item_name: The name of the item that should be added.
        :param item_price: The price of the item that should be added.
        """
        user_id = ctx.message.author.id
        #check if the item already exists in the database
        #grab the streamersID from the database
        streamerID = await db_manager.get_streamerID_with_userID(user_id)
        streamerChannel = await db_manager.get_streamerChannel(user_id)
        items = await db_manager.view_items(streamerChannel)
        emojiString = f'<:{item_emote.name}:{item_emote.id}>'
        print(items)
        for i in items:
            if item_name in i:
                await ctx.send(f"`{item_name}` already exists in the database.")
                return
        await db_manager.add_item(streamerID, item_name, item_price, emojiString)
        await ctx.send(f"Added `{item_name}` {emojiString} to the database, with the price `{item_price}`.")

    #command to remove an item from the database item table, using the remove_item function from helpers\db_manager.py
    @commands.hybrid_command(
        name="removeitem",
        description="This command will remove an item from the database.",
    )
    @checks.is_owner()
    async def remove_item(self, ctx: Context, item_name: str):
        """
        This command will remove an item from the database.

        :param ctx: The context in which the command was called.
        :param item_name: The name of the item that should be removed.
        """
        user_id = ctx.message.author.id
        #check if the item exists in the database
        streamerChannel = await db_manager.get_streamerChannel(user_id)
        streamerID = await db_manager.get_streamerID_with_userID(user_id)
        items = await db_manager.view_items(streamerChannel)
        for i in items:
            if item_name in i:
                await db_manager.remove_item(streamerID, item_name)
                await ctx.send(f"Removed `{item_name}` from the database.")
                return
        await ctx.send(f"`{item_name}` doesn't exist in the database.")


#command to view the items of a specific streamer by their ID, using the view_items function from helpers\db_manager.py
    @commands.hybrid_command(
        name="viewitems",
        description="This command will view all items of a specific streamer.",
    )
    @checks.is_owner()
    #the user needs to input the streamers ID
    async def view_items(self, ctx: Context, streamer_channel: str):
        """
        This command will view all items of a specific streamer.

        :param ctx: The context in which the command was called.
        :param streamer_id: The ID of the streamer whose items should be viewed.
        """
        user_id = ctx.message.author.id
        #check if the streamer exists in the database
        streamers = await db_manager.view_streamers()
        #remove the https://www.twitch.tv/ from the streamerchannel
        #rmove prefix function
        def remove_prefix(text, prefix):
            if text.startswith(prefix):
                return text[len(prefix):]
            return text
        streamer_channel_name = remove_prefix(streamer_channel, "https://www.twitch.tv/")
        for i in streamers:
            if streamer_channel in i:
                items = await db_manager.view_items(streamer_channel)
                embed = discord.Embed(title="Items", description=f"All of `{streamer_channel_name}'s` Items.", color=0x00ff00)
                print(items)
                for i in items:
                    #remove the streamerID from the name of the item
                    print(i)
                    item_name = i[2]
                    item_price = i[3]
                    item_emote = i[4]
                    embed.add_field(name=f"{item_name}{item_emote}", value=f"Price: {item_price}", inline=False)
                await ctx.send(embed=embed)
                return
        await ctx.send(f"Streamer doesn't exist in the database.")




# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Template(bot))
