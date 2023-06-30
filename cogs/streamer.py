""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import asyncio
from collections import defaultdict
import datetime
import json
import random
import re
import pytz
import requests
from discord import Color, Webhook, SyncWebhook
import aiohttp
import discord
from discord import Embed, app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context, has_permissions

from helpers import battle, checks, db_manager, hunt, mine, search, bank, beg
from typing import List, Tuple
from discord.ext.commands.errors import CommandInvokeError
from num2words import num2words

global i
i = 0
cash = "⚙"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
    # Add more rarities and colors as needed
}

# Here we name the cog and create a new class for the cog.
class Streamer(commands.Cog, name="streamer"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="viewstreamers",
        description="This command will view all streamers in the database.",
    )
    @checks.is_owner()
    async def view_streamers(self, ctx: Context):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        """
        This command will view all streamers in the database.

        :param ctx: The context in which the command was called.
        """
        streamers = await db_manager.view_streamers()
        embed = discord.Embed(title="Streamers", description="All streamers in the database.", color=0x00ff00)
        for i in streamers:
            streamer_channel = i[1]
            def remove_prefix(text, prefix):
                if text.startswith(prefix):
                    return text[len(prefix):]
                return text
            streamer_channel_name = remove_prefix(streamer_channel, "https://www.twitch.tv/")
            embed.add_field(name=streamer_channel_name, value=i[1], inline=False)
        await ctx.send(embed=embed)


    #command to create a new item in the database item table, using the create_streamer_item function from helpers\db_manager.py
    #`streamer_prefix` varchar(20) NOT NULL,
    #`item_id` varchar(20) NOT NULL,
    #`item_name` varchar NOT NULL,
    #`item_emoji` varchar(255) NOT NULL,
    #`item_rarity` varchar(255) NOT NULL,
    
    @commands.hybrid_command(
        name="createitem",
        description="This command will create a new streamer item in the database.",
    )
    @checks.is_streamer()
    async def create_item(self, ctx: Context, item_name: str, item_emoji: str):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        """
        This command will create a new streamer item in the database.

        :param ctx: The context in which the command was called.
        :param item_id: The id of the item that should be created.
        :param item_name: The name of the item that should be created.
        :param item_emoji: The emoji of the item that should be created.
        :param item_rarity: The rarity of the item that should be created.
        """
        user_id = ctx.message.author.id
        #get the streamer prefix
        streamer_prefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        print(streamer_prefix)
        #print(streamer_prefix)
        #get streamer broadcast type
        channel = await db_manager.get_streamer_channel_from_user_id(user_id)
        print(channel)
        #print(channel)
        broadcast_type = await db_manager.get_broadcaster_type_from_user_id(user_id)
        print(broadcast_type)
        #check if the item exists in the database
        items = await db_manager.view_streamer_items(channel)
        for i in items:
            if item_name in i:
                await ctx.send(f"An Item named {item_name} already exists for your channel.")
                return
        #create the item
        #if the streamer has more than 5 items and is an affilate, the item will not be created
        if broadcast_type == "affiliate" and len(items) >= 5:
            await ctx.send("You have reached the maximum amount of custom items for an affiliate.")
            return
        #if the streamer has more than 10 items and is a partner, the item will not be created
        elif broadcast_type == "partner" and len(items) >= 10:
            await ctx.send("You have reached the maximum amount of custom items for a partner.")
            return
        else:
            await db_manager.create_streamer_item(streamer_prefix, channel, item_name, item_emoji)
            #give the user the item 
            item_id = str(streamer_prefix) + "_" + item_name
            #convert all spaces in the item name to underscores
            item_id = item_id.replace(" ", "_")
            #send more info
            embed = discord.Embed(title="Item Creation", description=f"Created item {item_emoji} **{item_name}** for the channel {channel}",)
            embed.set_footer(text="ID: " + item_id)
            await ctx.send(embed=embed)

    #command to remove an item from the database item table, using the remove_item function from helpers\db_manager.py, make sure only streamers can remove their own items
    @commands.hybrid_command(
        name="removeitem",
        description="This command will remove an item from the database.",
    )
    @checks.is_streamer()
    async def removeitem(self, ctx: Context, item: str):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        """
        This command will remove an item from the database.

        :param ctx: The context in which the command was called.
        :param item_id: The id of the item that should be removed.
        """
        user_id = ctx.message.author.id
        #check if the item exists in the database
        channel = await db_manager.get_streamer_channel_from_user_id(user_id)
        items = await db_manager.view_streamer_items(channel)
        for i in items:
            if item in i:
                await db_manager.remove_item(item)
                await ctx.send(f"Removed item with the ID `{item}` from your items.")
                return
        await ctx.send(f"Item with the ID `{item}` does not exist in the database or you are not the streamer that owns this item.")

    #autocommplete for the removeitem command
    @removeitem.autocomplete("item")
    async def remove_item_autocomplete(self, ctx: discord.Interaction, argument):
        """
        This function provides autocomplete choices for the remove_item command.

        :param ctx: The context in which the command was called.
        :param argument: The user's current input for the item name.
        """
        streamer_items = await db_manager.view_user_streamer_made_items(ctx.user.id)
        choices = []
        for item in streamer_items:
            if argument.lower() in item[3].lower():  # Assuming item[1] is the item's name
                choices.append(app_commands.Choice(name=item[3], value=item[2]))  # Assuming item[0] is the item's ID
        return choices[:25]


    #command to view all the streamer items owned by the user from a specific streamer, if they dont have the item, display ??? for the emoji
    @commands.hybrid_command(
        name="streamercase",
        description="This command will view all of the items owned by the user from a specific streamer.",
    )
    async def streamercase(self, ctx: Context, streamer: str):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        """
        This command will view all of the items owned by the user from a specific streamer.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        user_name = ctx.message.author.name
        streamer = streamer.lower()

        # Get the items from the database
        items = await db_manager.view_streamer_items(streamer)
        #print(items)

        # Get the user's items from the database
        user_items = await db_manager.view_streamer_item_inventory(user_id)
        #print(user_items)

        if len(items) == 0:
            await ctx.send("This streamer has no items.")
            return

        embed = discord.Embed(title=f"{user_name}'s Streamer Items from {streamer}", description=f"Here are every item from {streamer}. If it has ???, it means you don't own one, think of this as a trophy case for streamer items you collect by watching {streamer}'s streams :)", color=0x00ff00)

        # Add the items to the embed
        for i in items:
            if any(i[2] in j for j in user_items):
                embed.add_field(name=f"{i[4]}", value=f"**{i[3]}**", inline=False)
            else:
                embed.add_field(name=f"**???**", value=f"**???**", inline=False)

        await ctx.send(embed=embed)
        #else:
            #await ctx.send("You cannot view your own items.")

    @commands.hybrid_command(
        name="connect",
        description="Connect your twitch account to your discord account!",
    )
    async def connect(self, ctx: Context):
        #check if th user exists in the database
        user_exists = await db_manager.check_user(ctx.author.id)
        if user_exists == None or user_exists == [] or user_exists == False or user_exists == 0 or user_exists == "None":
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        #create an embed to send to the user, then add a button to connect their twitch account
        embed = discord.Embed(
            title="Connect your twitch account to your discord account!",
            description="Click the button below to connect your twitch account to your discord account!",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/881056455321487390/881056516333762580/unknown.png")
        embed.set_footer(text="NyanStreamer")
        #make a discord.py button interaction
        class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
            def __init__(self, url: str):
                super().__init__()
                self.url = url
                self.add_item(discord.ui.Button(label="Register With Twitch!", url=self.url))
        #send the embed to the user in DMs
        await ctx.send("Check your DMs :)")
        try:
            await ctx.author.send(embed=embed, view=MyView(f"https://nyanstreamer.lol/webhook?discord_id={ctx.author.id}")) # Send a message with our View class that contains the button
        except(CommandInvokeError):
            await ctx.send("I couldn't DM you! Make sure your DMs are open!")
            return
        
    #disconnect command
    @commands.hybrid_command(
        name="disconnect",
        description="Disconnect your twitch account from your discord account!",
    )
    async def disconnect(self, ctx: Context):
        #check if the user is connected
        isConnected = await db_manager.is_connected(ctx.author.id)
        if isConnected == False:
            await ctx.send("You are not connected to a twitch account!")
            return
        #disconnect the user
        await db_manager.disconnect_twitch_id(ctx.author.id)
        await db_manager.disconnect_twitch_name(ctx.author.id)
        await db_manager.update_is_not_streamer(ctx.author.id)
        await ctx.send("Your twitch account has been disconnected from your discord account!")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Streamer(bot))