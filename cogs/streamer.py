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
import os
import sys


if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

twitch_client_id = config["CLIENT_ID"]
twitch_client_secret = config["CLIENT_SECRET"]

def checkUser(user_id, oauth_token):
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-ID": f"{twitch_client_id}"
    }
    params = {
        "user_id": user_id
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return len(data["data"]) > 0  # If the 'data' array is not empty, the user is streaming
    else:
        print(f"Error checking user: {response.json()}")
        return False

global i
i = 0
cash = "⌬"
replycont = "<:replycontinued:1124415317054070955>"
reply = "<:reply:1124415034643189912>"
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
        try:
            self.live_streams = set()
            self.check_streams.start()
        except Exception as e:
            print(e)
            pass

    #check every 5 minutes if any streamers are live
    @tasks.loop(minutes=5)
    async def check_streams(self):
        # Get all streamers from the database
        streamers = await db_manager.view_streamers()
        #check if the streamer is live
        for i in streamers:
            user_id = i[2]
            twitch_id_of_streamer = i[3]
            oauth = await db_manager.get_twitch_oauth_token(user_id)
            if oauth == None or oauth == False or oauth == [] or oauth == "None" or oauth == 0:
                continue
            is_live = checkUser(twitch_id_of_streamer, oauth)
            if is_live:
                self.live_streams.add(i[1])
            else:
                self.live_streams.discard(i[1])
        #send a message to the discord channel if a streamer is live
        if len(self.live_streams) > 0:
            channel = self.bot.get_channel(887439772495859978)
            message = ""
            for i in self.live_streams:
                message += f"{i} is live! https://www.twitch.tv/{i}\n"
            await channel.send(message)
        else:
            print("No streamers are live")

    @check_streams.before_loop
    async def before_check_streams(self):
        await self.bot.wait_until_ready()



    @commands.hybrid_group(
        name="streamer",
        description="The base command for all streamer commands.",
        aliases=["s"],
    )
    async def streamer(self, ctx: Context):
        """
        The base command for all streamer commands.

        :param ctx: The context in which the command was called.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("streamer")


    #command to create a new item in the database item table, using the create_streamer_item function from helpers\db_manager.py
    #`streamer_prefix` varchar(20) NOT NULL,
    #`item_id` varchar(20) NOT NULL,
    #`item_name` varchar NOT NULL,
    #`item_emoji` varchar(255) NOT NULL,
    #`item_rarity` varchar(255) NOT NULL,
    
    @streamer.command(
        name="createitem",
        description="make a new item for your viewers to collect!",
        aliases=["ci", "create_item"],
    )
    @checks.is_streamer()
    async def create_item(self, ctx: Context, channel: str, name: str, emoji: str):
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

        #get the user id from the twitch channel name 
        user_id = await db_manager.get_user_id_from_streamer_channel(channel)
        #get the streamer prefix
        streamer_prefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        #get streamer broadcast type
        broadcast_type = await db_manager.get_broadcaster_type_from_user_id(user_id)
        print(broadcast_type)
        #check if the item exists in the database
        items = await db_manager.view_streamer_items(channel)
        for i in items:
            if name in i:
                await ctx.send(f"An Item named {name} already exists for your channel.")
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
            await db_manager.create_streamer_item(streamer_prefix, channel, name, emoji)
            #give the user the item 
            item_id = str(streamer_prefix) + "_" + name
            #convert all spaces in the item name to underscores
            item_id = item_id.replace(" ", "_")
            #send more info
            embed = discord.Embed(title="Item Creation", description=f"Created item {emoji} **{name}** for the channel {channel}",)
            embed.set_footer(text="ID: " + item_id)
            await ctx.send(embed=embed)

    #autocommplete for the createitem command
    @create_item.autocomplete("channel")
    async def create_item_channel_autocomplete(self, ctx: discord.Interaction, argument: str):
        """
        This function provides autocomplete choices for the create_item command.

        :param ctx: The context in which the command was called.
        :param argument: The user's current input for the item name.
        """
        streamers = await db_manager.get_user_mod_channels(ctx.user.id)
        user_channel = await db_manager.get_streamer_channel_from_user_id(ctx.user.id)

        # Add the user's channel to the list
        if user_channel is not None:
            streamers.append((user_channel,))
        choices = []

        for streamer in streamers:
            streamer = streamer[0]
            #make it a string
            streamer = str(streamer)
            if argument.lower() in streamer.lower():
                choices.append(app_commands.Choice(name=streamer, value=streamer))
        return choices[:25]

    #command to remove an item from the database item table, using the remove_item function from helpers\db_manager.py, make sure only streamers can remove their own items
    @streamer.command(
        name="removeitem",
        description="delete an item from your channel! (only works for items you or your mods created)",
        aliases=["ri", "remove_item"],
    )
    @checks.is_streamer()
    async def removeitem(self, ctx: Context, channel: str, item: str):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        """
        This command will remove an item from the database.

        :param ctx: The context in which the command was called.
        :param item_id: The id of the item that should be removed.
        """
        items = await db_manager.view_streamer_items(channel)
        for i in items:
            if item in i:
                emoji = await db_manager.get_streamer_item_emote(item)
                name = await db_manager.get_streamer_item_name(item)
                embed = discord.Embed(title="Item Removal", description=f"Removed the item {emoji} **{name}** from the channel {channel}",)
                embed.set_footer(text="ID: " + item)
                await ctx.send(embed=embed)
                await db_manager.remove_item(item)
                return
        await ctx.send(f"Item with the ID `{item}` does not exist in the database or you are not the streamer that owns this item.")

    #autocommplete for the removeitem command
    @removeitem.autocomplete("channel")
    async def remove_item_channel_autocomplete(self, ctx: discord.Interaction, argument: str):
        """
        This function provides autocomplete choices for the remove_item command.

        :param ctx: The context in which the command was called.
        :param argument: The user's current input for the item name.
        """
        streamers = await db_manager.get_user_mod_channels(ctx.user.id)
        user_channel = await db_manager.get_streamer_channel_from_user_id(ctx.user.id)

        # Add the user's channel to the list
        if user_channel is not None:
            streamers.append((user_channel,))
        choices = []

        for streamer in streamers:
            streamer = streamer[0]
            #make it a string
            streamer = str(streamer)
            if argument.lower() in streamer.lower():
                choices.append(app_commands.Choice(name=streamer, value=streamer))
        return choices[:25]
    
    @removeitem.autocomplete("item")
    async def remove_item_autocomplete(self, ctx: discord.Interaction, argument):
        """
        This function provides autocomplete choices for the remove_item command.

        :param ctx: The context in which the command was called.
        :param argument: The user's current input for the item name.
        """
        channel_value = ctx.data["options"][0]["options"][0]["value"]
        print(channel_value)
        streamer_items = await db_manager.view_user_streamer_made_items(channel_value)
        choices = []
        for item in streamer_items:
            if argument.lower() in item[3].lower():  # Assuming item[1] is the item's name
                choices.append(app_commands.Choice(name=item[3], value=item[2]))  # Assuming item[0] is the item's ID
        return choices[:25]


    #command to view all the streamer items owned by the user from a specific streamer, if they dont have the item, display ??? for the emoji
    @streamer.command(
        name="case",
        description="see all the items you have from streamers! :)",
    )
    async def case(self, ctx: Context, streamer: str = None):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        
        if streamer == None:
            streamers = await db_manager.view_streamers()
        else:
            streamers = await db_manager.view_streamers()
            for i in streamers:
                if streamer in i:
                    streamers = []
                    streamers.append(i)
                    break
    
        user_id = ctx.message.author.id
        user_name = ctx.message.author.name
    
        # Get all streamers from the database
        
    
        # Create a list of embeds with 2 streamers per embed
        embeds = []
        for i in range(0, len(streamers), 2):
            description = ""
            total_items = 0
            total_owned_items = 0
            for streamer in streamers[i:i+2]:
                streamer = streamer[1].lower()

                # Get the items from the database
                items = await db_manager.view_streamer_items(streamer)

                # Get the user's items from the database
                user_items = await db_manager.view_streamer_item_inventory(user_id)

                # Initialize an empty string to hold all the item information
                item_info = ""
                user_item_count = 0

                # Add the items to the string
                for index, item in enumerate(items):  # Initialize counter for user items
                    total_items += 1
                    if any(item[2] in user_item for user_item in user_items):
                        user_item_count += 1  # Increment counter if user owns the item
                        total_owned_items += 1
                        if index == len(items) - 1:  # Check if this is the last item
                            item_info += f"{reply} **{item[4]}{item[3]}**\n"
                        else:
                            item_info += f"{replycont} **{item[4]}{item[3]}**\n"
                    else:
                        if index == len(items) - 1:  # Check if this is the last item
                            item_info += f"{reply} **???**\n"
                        else:
                            item_info += f"{replycont} **???**\n"

                # Add the streamer information to the description
                description += f"**[{streamer}](https://twitch.tv/{streamer})** ({user_item_count}/{len(items)})\n{item_info}\n\n"

            # Create the embed with the description
            embed = discord.Embed(title=f"{user_name}'s Streamer Items", description="Here are your Streamer Items, If it has ???, it means you don't own one, think of this as a trophy case for streamer items you collect by watching their streams :) \n \n" + description)
            embed.set_footer(text=f"Total items owned: {total_owned_items}/{total_items}")
            embeds.append(embed)

    
        class StreamerItemsButton(discord.ui.View):
            def __init__(self, current_page, embeds, **kwargs):
                super().__init__(**kwargs)
                self.current_page = current_page
                self.embeds = embeds
    
            @discord.ui.button(label="<<", style=discord.ButtonStyle.green)
            async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = 0
                await interaction.response.edit_message(embed=self.embeds[self.current_page])
    
            @discord.ui.button(label="<", style=discord.ButtonStyle.green)
            async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page > 0:
                    self.current_page -= 1
                    await interaction.response.edit_message(embed=self.embeds[self.current_page])
    
            @discord.ui.button(label=">", style=discord.ButtonStyle.green)
            async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page < len(self.embeds) - 1:
                    self.current_page += 1
                    await interaction.response.edit_message(embed=self.embeds[self.current_page])
    
            @discord.ui.button(label=">>", style=discord.ButtonStyle.green)
            async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = len(self.embeds) - 1
                await interaction.response.edit_message(embed=self.embeds[self.current_page])
    
        # If there are multiple pages, add the buttons
        if len(embeds) > 1:
            view = StreamerItemsButton(current_page=0, embeds=embeds)
            await ctx.send(embed=embeds[0], view=view)
        else:
            await ctx.send(embed=embeds[0])

    @case.autocomplete("streamer")
    async def streamercase_autocomplete(self, ctx: Context, argument):
        # Get all streamers from the database
        streamers = await db_manager.view_streamers()

        # Filter the streamers based on the user's input
        choices = [app_commands.Choice(name=streamer[1], value=streamer[1]) for streamer in streamers if argument.lower() in streamer[1].lower()]

        # Return the first 25 matches
        return choices[:25]
    

    #add mod command to add a mod for a streamer
    @streamer.command(
        name="addmod",
        description="add a mod for your channel!",
        aliases=["am", "add_mod"],
    )
    @checks.is_streamer()
    async def add_mod(self, ctx: Context, user: discord.Member):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        """
        This command will add a mod for a streamer in the database.

        :param ctx: The context in which the command was called.
        :param user_id: The id of the user that should be added as a mod.
        """
        user_id = ctx.message.author.id
        #get the streamer prefix
        streamer_prefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        #get streamer broadcast type
        channel = await db_manager.get_streamer_channel_from_user_id(user_id)

        #prevent the streamer from adding themselves as a mod
        if user.id == user_id:
            await ctx.send("You cannot add yourself as a mod!")
            return
        #get the streamer's mods
        mods = await db_manager.get_channel_mods(channel)
        #check if the user is already a mod
        for i in mods:
            if user.id in i:
                await ctx.send(f"{user.mention} is already a mod for your channel!")
                return
        #add the mod
        #get the mods twitch name and id
        twitch_name = await db_manager.get_twitch_name(user.id)
        twitch_id = await db_manager.get_twitch_id(user.id)
        if twitch_name == None or twitch_name == False or twitch_name == [] or twitch_name == "None" or twitch_name == 0:
            await ctx.send(f"{user.mention} is not connected to a twitch account!")
            return
        await db_manager.add_mod_to_channel(channel, user.id, twitch_id, twitch_name)
        await ctx.send(f"Added {user.mention} as a mod for your channel!")

    #remove mod command to remove a mod for a streamer
    @streamer.command(
        name="removemod",
        description="remove a mod for your channel!",
        aliases=["rm", "remove_mod"],
    )
    @checks.is_streamer()
    async def remove_mod(self, ctx: Context, user: discord.Member):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        """
        This command will remove a mod for a streamer in the database.

        :param ctx: The context in which the command was called.
        :param user_id: The id of the user that should be removed as a mod.
        """
        user_id = ctx.message.author.id
        #get the streamer prefix
        streamer_prefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        #get streamer broadcast type
        channel = await db_manager.get_streamer_channel_from_user_id(user_id)
        #get the streamer's mods
        mods = await db_manager.get_channel_mods(channel)
        #check if the user is already a mod
        for i in mods:
            if user.id in i:
                #remove the mod
                await db_manager.remove_mod_from_channel(channel, user.id)
                await ctx.send(f"Removed {user.mention} as a mod for your channel!")
                return
        await ctx.send(f"{user.mention} is not a mod for your channel!")

    
    #command to view all the mods for a streamer
    @streamer.command(
        name="mods",
        description="see all the mods for your channel!",
    )
    @checks.is_streamer()
    async def mods(self, ctx: Context):
        """
        This command will view all the mods for a streamer in the database.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        #get the streamer prefix
        streamer_prefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        #get streamer broadcast type
        channel = await db_manager.get_streamer_channel_from_user_id(user_id)
        #get the streamer's mods
        mods = await db_manager.get_channel_mods(channel)
        #create a string with all the mods
        mod_string = ""
        for i in range(len(mods)):
            if i == len(mods) - 1:  # If it's the last mod
                mod_string += f"{reply} <@{mods[i][0]}>\n"
            else:
                mod_string += f"{replycont} <@{mods[i][0]}>\n"
        else:
            if mod_string == "":
                mod_string = "No mods for this channel, Yet!"
        #create an embed with all the mods
        embed = discord.Embed(title=f"{channel}'s Mods", description=mod_string)
        await ctx.send(embed=embed)

    #chat setup command
    @streamer.group(
        name="chat",
        description="chat commands for streamers!",
    )
    async def chat(self, ctx: Context):
        """
        The base command for all chat commands.

        :param ctx: The context in which the command was called.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("chat")

    #command to setup the chat for a streamer
    @chat.command(
        name="setup",
        description="setup the chat for your channel!",
        aliases=["s", "set_up"],
    )
    @checks.is_streamer()
    async def chatsetup(self, ctx: Context, streamer: str, channel: discord.TextChannel):
        """
        This command will setup the chat for a streamer in the database.

        :param ctx: The context in which the command was called.
        """
        mods = await db_manager.get_channel_mods(streamer)
        await db_manager.set_discord_channel_id_chat(streamer, channel.id)
        await ctx.send(f"Twitch to Discord Chat setup for **{streamer}** in {channel.mention}! (It will take a few minutes for the chat to start working)")

    #auto complete for the chatsetup command for the streamer
    @chatsetup.autocomplete("streamer")
    async def chatsetup_streamer_autocomplete(self, ctx: Context, argument):
        streamers = await db_manager.get_user_mod_channels(ctx.user.id)
        user_channel = await db_manager.get_streamer_channel_from_user_id(ctx.user.id)

        # Add the user's channel to the list
        if user_channel is not None:
            streamers.append((user_channel,))
        choices = []

        for streamer in streamers:
            streamer = streamer[0]
            #make it a string
            streamer = str(streamer)
            if argument.lower() in streamer.lower():
                choices.append(app_commands.Choice(name=streamer, value=streamer))
        return choices[:25]
    
    #remove the chat setup for a streamer
    @chat.command(
        name="remove",
        description="remove the chat setup for your channel!",
        aliases=["r", "remove_setup"],
    )
    @checks.is_streamer()
    async def chatremove(self, ctx: Context, streamer: str):
        """
        This command will remove the chat setup for a streamer in the database.

        :param ctx: The context in which the command was called.
        """
        mods = await db_manager.get_channel_mods(streamer)
        await db_manager.remove_discord_channel_id_chat(streamer)
        await ctx.send(f"Twitch to Discord Chat removed for **{streamer}**! (It will take a few minutes for the chat to stop working)")

    #auto complete for the chatremove command for the streamer
    @chatremove.autocomplete("streamer")
    async def chatremove_streamer_autocomplete(self, ctx: Context, argument):
        streamers = await db_manager.get_user_mod_channels(ctx.user.id)
        user_channel = await db_manager.get_streamer_channel_from_user_id(ctx.user.id)

        # Add the user's channel to the list
        if user_channel is not None:
            streamers.append((user_channel,))
        choices = []

        for streamer in streamers:
            streamer = streamer[0]
            #make it a string
            streamer = str(streamer)
            if argument.lower() in streamer.lower():
                choices.append(app_commands.Choice(name=streamer, value=streamer))
        return choices[:25]

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
        await db_manager.remove_streamer_items(ctx.author.id)
        await db_manager.remove_streamer(ctx.author.id)
        await ctx.send("Your twitch account has been disconnected from your discord account!")


    #every 5 minutes check if the streamers are live

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Streamer(bot))