""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import asyncio
import json
import random
import re
import requests
from discord import Webhook, SyncWebhook
import aiohttp
import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord.ext.commands import Context, has_permissions

from helpers import battle, checks, db_manager, hunt, mine

global i
i = 0
cash = "<:cash:1077573941515792384>"
# Here we name the cog and create a new class for the cog.
class Basic(commands.Cog, name="basic"):
    def __init__(self, bot):
        self.bot = bot

    #command to add a new streamer and their server and their ID to the database streamer table, using the add_streamer function from helpers\db_manager.py
    #registering a streamer will also add them to the database user table
    @commands.hybrid_command(
        name="streamer",
        description="This command will add a new streamer to the database.",
    )
    async def streamer(self, ctx: Context, itemprefix: str):
        """
        This command will add a new streamer to the database.

        :param ctx: The context of the command.
        :param itemprefix: The prefix that the streamer wants to be used with thier custom items.
        """

#Done, fix this so it works with the the users connected twitch account

        userprofile = await db_manager.profile(ctx.author.id)
        twitch_id = userprofile[14]
        twitch_username = userprofile[15]
        if twitch_id == None or twitch_username == None or twitch_id == "None" or twitch_username == "None":
            await ctx.send("You must be connected to a twitch account to use this command.")
            return

        broadcaster_cast_type = await db_manager.get_broadcaster_type(twitch_username)
        user_id = ctx.author.id
        #check if the streamer already exists in the database
        if await db_manager.is_streamer(user_id):
            #this code fucking sucks, ive spent way too much time and now I have to rewrite it all because I cant figure out how to make it work, yay
            await ctx.send("this person is already a streamer. :)")
            return
        if broadcaster_cast_type == "partner":
            #if the user already exists in the database, update their streamer status to true
            if await db_manager.check_user(user_id):
                await db_manager.update_is_streamer(user_id)
                await db_manager.add_streamer(twitch_username, user_id, itemprefix, twitch_id, broadcaster_cast_type)
                await ctx.send("Thanks for registering as a streamer, as a Partner you get access to more custom item slots, and you can use the /give command to give items to your viewers, items will also be dropped to viewers in your streams.")
                return
            await db_manager.add_streamer(twitch_username, user_id, itemprefix, twitch_id, broadcaster_cast_type)
            await db_manager.add_user(user_id, True)
            #await ctx.send("Streamer added to the database.")
            return
        elif broadcaster_cast_type == "affiliate":
            #if the user already exists in the database, update their streamer status to true
            if await db_manager.check_user(user_id):
                await db_manager.update_is_streamer(user_id)
                await db_manager.add_streamer(twitch_username, user_id, itemprefix, twitch_id, broadcaster_cast_type)
                await ctx.send("Thanks for registering as a streamer, as an Affiliate you get to create custom items and they will be dropped in your streams.")
                return
            await db_manager.add_streamer(twitch_username, user_id, itemprefix, twitch_id, broadcaster_cast_type)
            await db_manager.add_user(user_id, True)
            #await ctx.send("Streamer added to the database.")
            return
        elif broadcaster_cast_type == "":
            #await db_manager.add_user(user_id, False)
            await ctx.send("You must be a twitch affiliate or partner to use this command.")
            return
    #if an error is raised, this will be called
    @streamer.error
    async def streamer_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please enter a channel name and an emoteprefix.")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please enter a valid channel name and an emoteprefix.")
            return


    #command to remove a streamer from the database streamer table, using the remove_streamer function from helpers\db_manager.py
    @commands.hybrid_command(
        name="unregister",
        description="This command will remove a streamer from the database.",
    )
    async def unregister(self, ctx: Context):
        """
        This command will remove a streamer from the database.

        :param ctx: The context in which the command was called.
        :param streamer_channel: The streamer's twitch channel.
        """
        user_id = ctx.author.id
        await db_manager.remove_streamer(user_id)
        #set the user's streamer status to false
        await db_manager.update_is_not_streamer(user_id)
        #await db_manager.remove_user(user_id)
        await ctx.send("Streamer removed from the database.")   

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
            streamer_channel = i[1]
            def remove_prefix(text, prefix):
                if text.startswith(prefix):
                    return text[len(prefix):]
                return text
            streamer_channel_name = remove_prefix(streamer_channel, "https://www.twitch.tv/")
            embed.add_field(name=streamer_channel_name, value=i[1], inline=False)
        await ctx.send(embed=embed)

#command to view inventory of a user, using the view_inventory function from helpers\db_manager.py
#STUB - Inventory
    @commands.hybrid_command(
        name="inventory",
        description="This command will view your inventory.",
    )
    async def inventory(self, ctx: Context):
        """
        This command will show you your inventory.

        :param ctx: The context in which the command was called.
        """
        #get the shop items from the database
        #create the user if they dont exist
        if not await db_manager.check_user(ctx.author.id):
            await ctx.send("You have not Started your adventure yet, use /start to start your adventure.")
            return
        items = await db_manager.view_inventory(ctx.author.id)
        print(items)
        if items == []:
            await ctx.send("Your inventory is empty.")
            return
        #create an embed
        #create muliple embeds if there are more than 10 items in the shop
        # Calculate number of pages based on number of items
        num_pages = (len(items) // 5) + (1 if len(items) % 5 > 0 else 0)
        
        current_page = 0

        # Create a list of embeds with 5 items per embed
        embeds = []
        for i in range(num_pages):
            start_idx = i * 5
            end_idx = start_idx + 5
            inv_embed = discord.Embed(
                title="Inventory",
                description="Your inventory, use /use to use an item. and /equip to equip an item.  ",
            )
            inv_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
            inv_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            for j in range(start_idx, end_idx):
                if j < len(items):
                    item = items[j]
                    item_id = item[1]
                    item_name = item[2]
                    item_price = item[3]
                    item_emoji = item[4]
                    item_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, item_id)
                    if item_amount == 0:
                        continue
                    item_description = await db_manager.get_basic_item_description(item_id)
                    equippedItems = await db_manager.get_equipped_items(ctx.author.id)
                    isEquipped = await db_manager.check_item_equipped(ctx.author.id, item_id)
                    if isEquipped == 1:
                        inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount} - Equipped", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                    else:
                        inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount}", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
            embeds.append(inv_embed)
        
        class Select(discord.ui.Select):
            def __init__(self):
                options=[
                    discord.SelectOption(label="All"),
                    discord.SelectOption(label="Weapons"),
                    discord.SelectOption(label="Tools"),
                    discord.SelectOption(label="Armor"),
                    discord.SelectOption(label="Consumables"),
                    discord.SelectOption(label="Materials"),
                    discord.SelectOption(label="Badges"),
                    ]
                super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
            async def callback(self, interaction: discord.Interaction):
                if self.values[0] == "All":
                    embeds = []
                    for i in range(num_pages):
                        start_idx = i * 5
                        end_idx = start_idx + 5
                        inv_embed = discord.Embed(
                            title="Inventory",
                            description="Your inventory, use /use to use an item. and /equip to equip an item.  ",
                        )
                        inv_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
                        inv_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                        for j in range(start_idx, end_idx):
                            if j < len(items):
                                item = items[j]
                                item_id = item[1]
                                item_name = item[2]
                                item_price = item[3]
                                item_emoji = item[4]
                                item_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, item_id)
                                if item_amount == 0:
                                    continue
                                item_description = await db_manager.get_basic_item_description(item_id)
                                #check if the item is equiped
                                isEquipped = await db_manager.check_item_equipped(ctx.author.id, item_id)
                                if isEquipped == 1:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount} - Equipped", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                                else:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount}", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                        embeds.append(inv_embed)
                        await interaction.response.edit_message(embed=embeds[current_page])
                        
                if self.values[0] == "Weapons":
                    embeds = []
                    for i in range(num_pages):
                        start_idx = i * 5
                        end_idx = start_idx + 5
                        inv_embed = discord.Embed(
                            title="Inventory",
                            description="Your inventory, use /use to use an item. and /equip to equip an item.  ",
                        )
                        inv_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
                        inv_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                        for j in range(start_idx, end_idx):
                            if j < len(items):
                                item = items[j]
                                item_id = item[1]
                                item_name = item[2]
                                item_price = item[3]
                                item_emoji = item[4]
                                item_type = item[7]
                                if item_type == "Weapon":
                                    item_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, item_id)
                                    item_description = await db_manager.get_basic_item_description(item_id)
                                    if item_amount == 0:
                                        continue
                                else:
                                    #dont add the item to the embed
                                    continue
                                isEquipped = await db_manager.check_item_equipped(ctx.author.id, item_id)
                                if isEquipped == 1:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount} - Equipped", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                                else:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount}", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                        embeds.append(inv_embed)
                    await interaction.response.edit_message(embed=embeds[current_page])
                    
                if self.values[0] == "Tools":
                    embeds = []
                    for i in range(num_pages):
                        start_idx = i * 5
                        end_idx = start_idx + 5
                        inv_embed = discord.Embed(
                            title="Inventory",
                            description="Your inventory, use /use to use an item. and /equip to equip an item.  ",
                        )
                        inv_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
                        inv_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                        for j in range(start_idx, end_idx):
                            if j < len(items):
                                item = items[j]
                                item_id = item[1]
                                item_name = item[2]
                                item_price = item[3]
                                item_emoji = item[4]
                                item_type = item[7]
                                if item_type == "Tool":
                                    item_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, item_id)
                                    item_description = await db_manager.get_basic_item_description(item_id)
                                    if item_amount == 0:
                                        continue
                                else:
                                    #dont add the item to the embed
                                    continue
                                isEquipped = await db_manager.check_item_equipped(ctx.author.id, item_id)
                                if isEquipped == 1:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount} - Equipped", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                                else:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount}", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                        embeds.append(inv_embed)
                    await interaction.response.edit_message(embed=embeds[current_page])
                    
                if self.values[0] == "Armor":
                    embeds = []
                    for i in range(num_pages):
                        start_idx = i * 5
                        end_idx = start_idx + 5
                        inv_embed = discord.Embed(
                            title="Inventory",
                            description="Your inventory, use /use to use an item. and /equip to equip an item.  ",
                        )
                        inv_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
                        inv_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                        for j in range(start_idx, end_idx):
                            if j < len(items):
                                item = items[j]
                                item_id = item[1]
                                item_name = item[2]
                                item_price = item[3]
                                item_emoji = item[4]
                                item_type = item[7]
                                item_sub_type = await db_manager.get_basic_item_sub_type(item_id)
                                if item_type == "Armor" or item_type == "Accessory" or item_sub_type == "Bauble":
                                    item_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, item_id)
                                    item_description = await db_manager.get_basic_item_description(item_id)
                                    if item_amount == 0:
                                        continue
                                else:
                                    #dont add the item to the embed
                                    continue
                                isEquipped = await db_manager.check_item_equipped(ctx.author.id, item_id)
                                if isEquipped == 1:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount} - Equipped", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                                else:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount}", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                        embeds.append(inv_embed)
                    await interaction.response.edit_message(embed=embeds[current_page])
                    
                if self.values[0] == "Consumables":
                    embeds = []
                    for i in range(num_pages):
                        start_idx = i * 5
                        end_idx = start_idx + 5
                        inv_embed = discord.Embed(
                            title="Inventory",
                            description="Your inventory, use /use to use an item. and /equip to equip an item.  ",
                        )
                        inv_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
                        inv_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                        for j in range(start_idx, end_idx):
                            if j < len(items):
                                item = items[j]
                                item_id = item[1]
                                item_name = item[2]
                                item_price = item[3]
                                item_emoji = item[4]
                                item_type = item[7]
                                if item_type == "Consumable":
                                    item_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, item_id)
                                    item_description = await db_manager.get_basic_item_description(item_id)
                                    if item_amount == 0:
                                        continue
                                else:
                                    #dont add the item to the embed
                                    continue
                                inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount}", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                        embeds.append(inv_embed)
                    await interaction.response.edit_message(embed=embeds[current_page])
                    
                if self.values[0] == "Materials":
                    embeds = []
                    for i in range(num_pages):
                        start_idx = i * 5
                        end_idx = start_idx + 5
                        inv_embed = discord.Embed(
                            title="Inventory",
                            description="Your inventory, use /use to use an item. and /equip to equip an item.  ",
                        )
                        inv_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
                        inv_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                        for j in range(start_idx, end_idx):
                            if j < len(items):
                                item = items[j]
                                item_id = item[1]
                                item_name = item[2]
                                item_price = item[3]
                                item_emoji = item[4]
                                item_type = item[7]
                                if item_type == "Material":
                                    item_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, item_id)
                                    item_description = await db_manager.get_basic_item_description(item_id)
                                    if item_amount == 0:
                                        continue
                                else:
                                    #dont add the item to the embed
                                    continue
                                inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount}", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                        embeds.append(inv_embed)
                    await interaction.response.edit_message(embed=embeds[current_page])
                    
                if self.values[0] == "Badges":
                    embeds = []
                    for i in range(num_pages):
                        start_idx = i * 5
                        end_idx = start_idx + 5
                        inv_embed = discord.Embed(
                            title="Inventory",
                            description="Your inventory, use /use to use an item. and /equip to equip an item.  ",
                        )
                        inv_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
                        inv_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                        for j in range(start_idx, end_idx):
                            if j < len(items):
                                item = items[j]
                                item_id = item[1]
                                item_name = item[2]
                                item_price = item[3]
                                item_emoji = item[4]
                                item_type = item[7]
                                if item_type == "Badge":
                                    item_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, item_id)
                                    item_description = await db_manager.get_basic_item_description(item_id)
                                    if item_amount == 0:
                                        continue
                                else:
                                    #dont add the item to the embed
                                    continue
                                isEquipped = await db_manager.check_item_equipped(ctx.author.id, item_id)
                                if isEquipped == 1:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount} - Equipped", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                                else:
                                    inv_embed.add_field(name=f"{item_emoji}{item_name} - {item_amount}", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
                        embeds.append(inv_embed)
                    await interaction.response.edit_message(embed=embeds[current_page])
                    
                    
               
                    
                    
        class InvButton(discord.ui.View):
            def __init__(self, current_page, **kwargs):
                super().__init__(**kwargs)
                self.current_page = current_page
                self.add_item(Select())
            @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
            async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = 0
                await interaction.response.defer()
                await message.edit(embed=embeds[self.current_page])
            @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
            async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page -= 1
                await interaction.response.defer()
                await message.edit(embed=embeds[self.current_page])
            @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
            async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page += 1
                await interaction.response.defer()
                await message.edit(embed=embeds[self.current_page])
            @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
            async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = num_pages - 1
                await interaction.response.defer()
                await message.edit(embed=embeds[self.current_page])
            def __end__(self, current_page, **kwargs):
                super().__end__(**kwargs)
                self.current_page = current_page
                self.add_item(Select())
                
        message = await ctx.send(embed=embeds[current_page], view=InvButton(current_page))
        
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
        #get streamer broadcast type
        channel = await db_manager.get_streamer_channel_from_user_id(user_id)
        print(channel)
        broadcast_type = await db_manager.get_broadcaster_type(channel)
        #check if the item exists in the database
        items = await db_manager.view_streamer_items(channel)
        for i in items:
            if item_name in i:
                await ctx.send(f"An Item named {item_name} already exists for your channel.")
                return
        #create the item
        #if the streamer has more than 5 items and is an affilate, the item will not be created
        if broadcast_type == "affiliate" and len(items) >= 5:
            await ctx.send("You have reached the maximum amount of items for an affiliate.")
            return
        #if the streamer has more than 10 items and is a partner, the item will not be created
        elif broadcast_type == "partner" and len(items) >= 10:
            await ctx.send("You have reached the maximum amount of items for a partner.")
            return
        else:
            await db_manager.create_streamer_item(streamer_prefix, channel, item_name, item_emoji)
            #give the user the item 
            item_id = str(streamer_prefix) + "_" + item_name
            #convert all spaces in the item name to underscores
            item_id = item_id.replace(" ", "_")
            await db_manager.add_streamer_item_to_user(user_id, item_id)
            await ctx.send("Item created.")

    #command to remove an item from the database item table, using the remove_item function from helpers\db_manager.py, make sure only streamers can remove their own items
    @commands.hybrid_command(
        name="removeitem",
        description="This command will remove an item from the database.",
    )
    @checks.is_streamer()
    async def remove_item(self, ctx: Context, item: str):
        """
        This command will remove an item from the database.

        :param ctx: The context in which the command was called.
        :param item_id: The id of the item that should be removed.
        """
        user_id = ctx.message.author.id
        #check if the item exists in the database
        items = await db_manager.view_streamer_items(user_id)
        for i in items:
            if item in i:
                await db_manager.remove_item(item)
                await ctx.send(f"Removed item with the ID `{item}` from your items.")
                return
        await ctx.send(f"Item with the ID `{item}` does not exist in the database or you are not the streamer that owns this item.")

#command to view all the streamer items owned by the user from a specific streamer, if they dont have the item, display ??? for the emoji
    @commands.hybrid_command(
        name="streamercase",
        description="This command will view all of the items owned by the user from a specific streamer.",
    )
    async def streamercase(self, ctx: Context, streamer: str):
        """
        This command will view all of the items owned by the user from a specific streamer.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        user_name = ctx.message.author.name
        streamer = streamer.lower()
        #get the streamer prefix
        streamer_prefix = await db_manager.get_streamerPrefix_with_channel(streamer)
        print(streamer_prefix)
        #get the streamer prefix of the user
        user_streamer_prefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        print(user_streamer_prefix)
        #if streamer_prefix != user_streamer_prefix:
        #get streamer broadcast type
        #get the items from the database
        #put the streamername to lowercase
        items = await db_manager.view_streamer_items(streamer)
        #get the users items from the database
        user_items = await db_manager.view_streamer_item_inventory(user_id)
        #create the embed
        if len(items) == 0:
            await ctx.send("This streamer has no items.")
            return
        embed = discord.Embed(title=f"{user_name}'s Streamer Items from {streamer}", description=f"heres every item from {streamer} \n if it has ???, it means you dont own one, think of this as a trophy case for streamer items you collect by watching {streamer}'s streams :)\n", color=0x00ff00)
        #add the items to the embed
        for i in items:
            #check if the user has the item
            for j in user_items:
                if i[1] in j:
                    embed.add_field(name=f"{i[4]}", value=f"**{i[3]}**", inline=False)
                else:
                    embed.add_field(name=f"**???**", value=f"**???**", inline=False)
        #send the embed
        await ctx.send(embed=embed)
        #else:
            #await ctx.send("You cannot view your own items.")
     


    @commands.hybrid_command(
        name="questboard",
        description="This command will show the quest board.",
    )
    async def questboard(self, ctx: Context):
        """
        This command will show the quest board.

        :param ctx: The context in which the command was called.
        """
        #get all the quests from the database
        quests = await db_manager.get_quests_on_board()
        embeds = []
        #create an embed to show the quests
        #for each quest in the quests, create a page for it
        for i in quests:
            #create an embed for the specific quest
            questembed = discord.Embed(title=f"{i[1]}")
            #get the quest id
            quest_id = i[0]
            quest_id = str(quest_id)
            #get the quest name
            quest_name = i[1]
            quest_name = str(quest_name)
            #get the quest description
            quest_description = i[2]
            quest_description = str(quest_description)
            #get the quest xp
            quest_xp = i[3]
            quest_xp = str(quest_xp)
            #get the quest reward
            quest_reward = i[4]
            quest_reward = str(quest_reward)
            #get the quest reward amount
            quest_reward_amount = i[5]
            quest_reward_amount = str(quest_reward_amount)
            #get the quest level requirement
            quest_level_req = i[6]
            quest_level_req = str(quest_level_req)
            #get the quest type
            quest_type = i[7]
            quest_type = str(quest_type)
            #get the quest itself
            quest = i[8]
            quest = str(quest)
            #add a field to the embed for this quest
            questembed.add_field(name=f"**{quest_name}**", value=f"`ID:{quest_id}` \n **Description**: `{quest_description}` \n **XP**: `{quest_xp}` \n **Reward**: `{quest_reward_amount} {quest_reward}` \n **Level Requirement**: `{quest_level_req}` \n **Quest**: `{quest_type} {quest}'s` ", inline=False)
            
            #save the embed to a list
            embeds.append(questembed)
        
        #send the first embed, and add reactions to it to switch between the different embeds
        message = await ctx.send(embed=embeds[0])
        await message.add_reaction("⏪")
        await message.add_reaction("⏩")
        await message.add_reaction("✅")
        #create a function to check if the reaction is the one we want
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⏪", "⏩" , "✅"]
        #create a function that whenever the user clicks the check mark, it will add the quest to the users quest list
        
        #switch between the different embeds
        i = 0
        reaction = None
        while True:
            if str(reaction) == "⏪":
                if i > 0:
                    i -= 1
                    await message.edit(embed=embeds[i])
            elif str(reaction) == "⏩":
                if i < len(embeds)-1:
                    i += 1
                    await message.edit(embed=embeds[i])
            elif str(reaction) == "✅":
                #get the quest id from the embed
                quest_name = embeds[i].title
                #get the quest id from the database
                quest_id = await db_manager.get_quest_id_from_quest_name(quest_name)
                print(quest_id)
                quest_id = str(quest_id)
                #get the user id
                user_id = ctx.message.author.id
                user_id = str(user_id)
                #check if the user already has the quest
                user_has_quest = await db_manager.check_user_has_quest(user_id, quest_id)
                #check if the user has any quest 
                user_has_any_quest = await db_manager.check_user_has_any_quest(user_id)
                isCompleted = await db_manager.check_quest_completed(user_id, quest_id)
                #check if the user meets the level requirements
                user_level = await db_manager.get_level(user_id)
                level_req = await db_manager.get_quest_level_required(quest_id)
                #convert them to integers
                user_level = int(user_level[0])
                level_req = int(level_req)
                if user_level < level_req:
                    await ctx.send("You do not meet the level requirements for this quest!")
                    break
                #if the user already has the quest, tell them they already have it
                elif isCompleted == True:
                    await ctx.send("You already completed this quest!")
                    break
                
                elif user_has_quest == True:
                    await ctx.send("You already have this quest!")
                    break
                #if the user already has a different quest, tell them they already have a quest
                elif user_has_any_quest == True:
                    await ctx.send("You already have a quest!, Abondon or Complete your current quest to get a new one!")
                    break
                #if the user already completed the quest, tell them they already completed it

                #if the user doesnt have the quest, add it to their quest list
                else:
                    #get a quest slot for the user
                    await db_manager.give_user_quest(user_id, quest_id)
                    await db_manager.create_quest_progress(user_id, quest_id)
                    await ctx.send("Quest added to your quest list!")
                    #remove the quest from the quest board
                    #await db_manager.remove_quest_from_board(quest_id)
                    break
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction, user)                
            except asyncio.TimeoutError:
                break
            
        #when the user clicks the check mark, add the quest to the users quest list, remove the quest from the quest board, check if the user already has the quest, and if they do, tell them they already have it, and if they dont, add it to their quest list
    #abandon quest hybrid command 
    @commands.hybrid_command(
        name="abandonquest",
        description="Abandon your current quest",
    )
    async def abandonquest(self, ctx: Context):
        await db_manager.remove_quest_from_user(ctx.author.id)
        await ctx.send("You have Abandoned your current quest, if you want to get a new one please check the quest board")
        
    
    #shop command that shows the shop
    @commands.hybrid_command(
        name="shop",
        description="This command will show the shop.",
    )
    async def shop(self, ctx: Context):
        """
        This command will show the shop.

        :param ctx: The context in which the command was called.
        """
        #get the shop items from the database
        items = await db_manager.display_shop_items()
        #pick random items from the shop to display
        #create an embed
        #create muliple embeds if there are more than 10 items in the shop
        # Calculate number of pages based on number of items
        num_pages = (len(items) // 5) + (1 if len(items) % 5 > 0 else 0)
        
        current_page = 0

        # Create a list of embeds with 5 items per embed
        embeds = []
        for i in range(num_pages):
            start_idx = i * 5
            end_idx = start_idx + 5
            shop_embed = discord.Embed(
                title="Shop",
                description="This is the shop, you can buy items here with `/buy itemid` EX. `/buy iron_sword`.",
            )
            shop_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
            for j in range(start_idx, end_idx):
                if j < len(items):
                    item = items[j]
                    item_id = item[0]
                    item_name = item[1]
                    item_price = item[2]
                    item_emoji = item[3]
                    item_description = await db_manager.get_basic_item_description(item_id)
                    item_amount = await db_manager.get_shop_item_amount(item_id)
                    shop_embed.add_field(name=f"{item_emoji}{item_name} - {cash}{item_price} ({item_amount})", value=f'**{item_description}** \n ID:`{item_id}`', inline=False)
            embeds.append(shop_embed)
            
        class ShopButton(discord.ui.View):
            def __init__(self, current_page, **kwargs):
                super().__init__(**kwargs)
                self.current_page = current_page
            @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
            async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = 0
                await interaction.response.defer()
                await message.edit(embed=embeds[self.current_page], view=ShopButton(self.current_page))
            @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
            async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page -= 1
                await interaction.response.defer()
                await message.edit(embed=embeds[self.current_page], view=ShopButton(self.current_page))
            @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
            async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page += 1
                await interaction.response.defer()
                await message.edit(embed=embeds[self.current_page], view=ShopButton(self.current_page))
            @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
            async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = num_pages - 1
                await interaction.response.defer()
                await message.edit(embed=embeds[self.current_page], view=ShopButton(self.current_page))
        message = await ctx.send(embed=embeds[current_page], view=ShopButton(current_page))

     #buy command for buying items, multiple of the same item can be bought, and the user can buy multiple items at once, then removes them from the shop, and makes sure the user has enough bucks
    @commands.hybrid_command(
        name="buy",
        description="This command will buy an item from the shop.",
    )
    async def buy(self, ctx: Context, item: str, amount: int):
        """
        This command will buy an item from the shop.

        :param ctx: The context in which the command was called.
        :param item_id: The ID of the item that should be bought.
        :param amount: The amount of the item that should be bought.
        """
        user_id = ctx.message.author.id
        user_profile = await db_manager.profile(user_id)
        user_money = user_profile[1]
        user_money = int(user_money)
        user_health = user_profile[2]
        isStreamer = user_profile[3]
        #get the users xp and level
        user_xp = user_profile[11]
        user_level = user_profile[12]
        #check if the item exists in the shop
        shop = await db_manager.display_shop_items()
        for i in shop:
            if item in i:
                #check if the user has enough bucks
                item_price = i[2]
                item_price = int(item_price)
                total_price = item_price * amount
                if user_money >= total_price:
                    #if the item type is a weapon, check if the user has already has this weapon
                    item_type = await db_manager.get_basic_item_type(item)
                    if item_type == "Weapon":
                        #check if the user has this weapon
                        user_inventory = await db_manager.view_inventory(user_id)
                        for i in user_inventory:
                            if item in i:
                                await ctx.send(f"You already have this weapon!")
                                return
                        #if the user is trying to buy more than 1 of the same weapon, tell them they can only buy 1
                        if amount > 1:
                            await ctx.send(f"You can only buy 1 of the same Weapon!")
                            return
                        
                    if item_type == "Armor":
                        #check if the user has this armor on their inventory
                        user_inventory = await db_manager.view_inventory(user_id)
                        for i in user_inventory:
                            if item in i:
                                await ctx.send(f"You already have this armor!")
                                return
                        #if the user is trying to buy more than 1 of the same weapon, tell them they can only buy 1
                        if amount > 1:
                            await ctx.send(f"You can only buy 1 of the same Armor!")
                            return
                    item_name = await db_manager.get_basic_item_name(item)
                    item_price = await db_manager.get_shop_item_price(item)
                    item_emoji = await db_manager.get_shop_item_emoji(item)
                    #Q, how to I get the string out of a coroutine?
                    #A, use await
                    item_rarity = await db_manager.get_basic_item_rarity(item)
                    item_type = await db_manager.get_basic_item_type(item)
                    item_damage = await db_manager.get_basic_item_damage(item)
                    item_name = await db_manager.get_basic_item_name(item)
                    item_element = await db_manager.get_basic_item_element(item)
                    item_crit_chance = await db_manager.get_basic_item_crit_chance(item)
                    #remove the item from the shop
                    #send a message asking the user if they are sure they want to buy the item, and add reactions to the message to confirm or cancel the purchase
                    message = await ctx.send(f"Are you sure you want to buy `{amount}` of `{item_name}` for `{total_price}` bucks?")
                    await message.add_reaction("✅")
                    await message.add_reaction("❌")
                    #create a function to check if the reaction is the one we want
                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]
                    #wait for the reaction
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await ctx.send("You took too long to respond.")
                        return
                    #if the user reacted with ❌, cancel the purchase
                    if str(reaction) == "❌":
                        await ctx.send("Purchase cancelled.")
                        return
                    #if the user reacted with ✅, continue with the purchase
                    if str(reaction) == "✅":
                        #make sure they have enough money to buy the item
                            #if the item type is a weapon, check if the user has already has this weapon
                        item_type = await db_manager.get_basic_item_type(item)
                        if item_type == "Weapon":
                            #check if the user has this weapon
                            user_inventory = await db_manager.view_inventory(user_id)
                            for i in user_inventory:
                                if item in i:
                                    await ctx.send(f"You already have this weapon!")
                                    return
                            #if the user is trying to buy more than 1 of the same weapon, tell them they can only buy 1
                            if amount > 1:
                                await ctx.send(f"You can only buy 1 of the same Weapon!")
                                return
                        
                        if item_type == "Armor":
                            #check if the user has this armor on their inventory
                            user_inventory = await db_manager.view_inventory(user_id)
                            for i in user_inventory:
                                if item in i:
                                    await ctx.send(f"You already have this armor!")
                                    return
                            #if the user is trying to buy more than 1 of the same weapon, tell them they can only buy 1
                            if amount > 1:
                                await ctx.send(f"You can only buy 1 of the same Armor!")
                                return
                            
                        #if the user doesnt have enough money, tell them
                        if user_money < total_price:
                            await ctx.send(f"You don't have enough money to buy `{amount}` of `{item_name}`.")
                            return
                        #if the user has enough money, continue with the purchase
                        else:
                            ctx.send(f"You bought `{amount}` of `{item_name}` for `{total_price}` bucks.")
                            #remove the item from the shop
                            await db_manager.remove_shop_item_amount(item, amount)
                            #add the item to the users inventory
                            await db_manager.add_item_to_inventory(user_id, item, amount)
                            #if the user has a quest, check it
                            userquestID = await db_manager.get_user_quest(user_id)
                            if userquestID != "None":
                                questItem = await db_manager.get_quest_item_from_id(userquestID)
                                if questItem == item:
                                    await db_manager.update_quest_progress(user_id, userquestID, amount)
                                #now check if the user has completed the quest
                                questProgress = await db_manager.get_quest_progress(user_id, userquestID)
                                questAmount = await db_manager.get_quest_total_from_id(userquestID)
                                questRewardType = await db_manager.get_quest_reward_type_from_id(userquestID)
                                if questProgress >= questAmount:
                                    #give the user the reward
                                    if questRewardType == "Money":
                                        questReward = await db_manager.get_quest_reward_from_id(userquestID)
                                        await db_manager.add_money(user_id, questReward)
                                        await ctx.send(f"You completed the quest and got `{questReward}` bucks!")
                                    if questRewardType == "Item":
                                        questReward = await db_manager.get_quest_reward_from_id(userquestID)
                                        await db_manager.add_item_to_inventory(user_id, questReward, 1)
                                        await ctx.send(f"You completed the quest and got `{questReward}`!")
                                    #remove the quest from the user
                                    await db_manager.mark_quest_completed(user_id, userquestID)

                            
                            #remove the price from the users money
                            await db_manager.remove_money(user_id, total_price)
                            await ctx.send(f"You bought `{amount}` of `{item_name}` for `{total_price}` bucks.")
                        return
                else:
                    item_name = await db_manager.get_basic_item_name(item)
                    await ctx.send(f"You don't have enough bucks to buy `{amount}` of `{item_name}`.")
                    return
        await ctx.send(f"Item doesn't exist in the shop.")
        
    #sell command for selling items, multiple of the same item can be sold, and the user can sell multiple items at once, then removes them from the users inventory, and adds the price to the users money
    @commands.hybrid_command(
        name="sell",
        description="This command will sell an item from your inventory.",
    )
    async def sell(self, ctx: Context, item: str, amount: int):
        """
        This command will sell an item from your inventory.

        :param ctx: The context in which the command was called.
        :param item_id: The ID of the item that should be sold.
        :param amount: The amount of the item that should be sold.
        """
        user_id = ctx.message.author.id
        user_profile = await db_manager.profile(user_id)
        user_money = user_profile[1]
        user_money = int(user_money)
        user_health = user_profile[2]
        isStreamer = user_profile[3]
        #get the users xp and level
        user_xp = user_profile[11]
        user_level = user_profile[12]
        #check if the item exists in the users inventory
        user_inventory = await db_manager.view_inventory(user_id)
        for i in user_inventory:
            if item in i:
                #check if its equipped
                if i[9] == 1:
                    await ctx.send(f"You can't sell an equipped item!, unequip it first with `/unequip {item}`")
                    return
                #check if the user has enough of the item
                item_amount = i[6]
                item_amount = int(item_amount)
                if item_amount >= amount:
                    item_price = i[3]
                    item_price = int(item_price)
                    total_price = item_price * amount
                    #remove the item from the users inventory
                    await db_manager.remove_item_from_inventory(user_id, item, amount)
                    #add the price to the users money
                    await db_manager.add_money(user_id, total_price)
                    await ctx.send(f"You sold `{amount}` of `{i[2]}` for `{total_price}` bucks.")
                    return
                else:
                    await ctx.send(f"You don't have enough `{i[2]}` to sell `{amount}`.")
                    return
        await ctx.send(f"Item doesn't exist in your inventory.")

#view a users profile using the view_profile function from helpers\db_manager.py
    @commands.hybrid_command(
        name="profile",
        description="This command will view your profile.",
    )
    async def profile(self, ctx: Context):
        """
        This command will view your profile.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        user_profile = await db_manager.profile(user_id)
        print(user_profile)
        user_id = user_profile[0]
        user_money = user_profile[1]
        user_health = user_profile[2]
        isStreamer = user_profile[3]
        #get the users xp and level
        user_xp = user_profile[11]
        user_level = user_profile[12]
        user_quest = user_profile[13]
        user_twitch_id = user_profile[14]
        user_twitch_name = user_profile[15]
        #get the xp needed for the next level
        xp_needed = await db_manager.xp_needed(user_id)
        #convert the xp needed to a string
        xp_needed = str(xp_needed)
        
        user_items = await db_manager.view_inventory(user_id)
        embed = discord.Embed(title="Profile", description=f"{ctx.message.author.mention}'s Profile.", color=0x00ff00)
        if user_health == 0:
            embed.add_field(name="Health", value=f"{user_health} (Dead)", inline=True)
        else:
            embed.add_field(name="Health", value=f"{user_health}", inline=True)
        embed.add_field(name="Money", value=f"{cash}{user_money}", inline=True)
        #get the badges from the database
        badges = await db_manager.get_equipped_badges(user_id)
        #make a feild for the badges and set the title to badges and the value to the badges
        Userbadges = []
        for badge in badges:
            badge_name = badge[2]
            badge_emote = badge[4]
            badge = f"{badge_emote} {badge_name} \n"
            Userbadges.append(badge)
        
        #get each badge and add it to the badges feild
        Userbadges = ''.join(Userbadges)
        embed.add_field(name="Badges", value=f"{Userbadges}", inline=False)
        #add xp and level
        embed.add_field(name="XP", value=f"{user_xp} / {xp_needed}", inline=True)
        embed.add_field(name="Level", value=f"{user_level}", inline=True)
        #for i in user_items:
        #    item_name = i[2]
        #    item_emote = i[4]
        #    item_amount = i[6]
        #    item_type = i[7]
        #    if item_type == "Weapon":
        #        embed.add_field(name=f"{item_emote} {item_name}", value=f"Damage: {item_amount}", inline=True)
            
        #create a section for the users current quest
        if user_quest == 0 or user_quest == None or user_quest == "" or user_quest == "None":
            embed.add_field(name="Current Quest", value="`No Current Quest, Check the Quest Board to get one`", inline=False)
        else:
            quest_name = await db_manager.get_quest_name_from_quest_id(user_quest)
            quest_description = await db_manager.get_quest_description_from_quest_id(user_quest)
            questTotal = await db_manager.get_quest_total_from_id(user_quest)
            quest_progress = await db_manager.get_quest_progress(user_id, user_quest)
            quest_progress = str(quest_progress)
            embed.add_field(name="Current Quest", value=f"`{quest_name} - {quest_progress}/{questTotal}`", inline=False)
        embed.set_thumbnail(url=ctx.message.author.avatar.url)
        if isStreamer == 1:
            isStreamer = "Yes"
        elif isStreamer == 0:
            isStreamer = "No"
        if user_twitch_name == None or user_twitch_name == "" or user_twitch_name == "None":
            user_twitch_name = "Not Connected"
        embed.set_footer(text=f"User ID: {user_id} | Twitch: {user_twitch_name} | Streamer: {isStreamer}")

        await ctx.send(embed=embed)
        
    #hybrid command to start the user on their journy, this will create a profile for the user using the profile function from helpers\db_manager.py and give them 200 bucks
    @commands.hybrid_command(
        name="start",
        description="This command will start your journey.",
    )
    async def start(self, ctx: Context):
        """
        This command will start your journey.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        #check if the user is in the database
        userExist = await db_manager.check_user(user_id)
        if userExist == None or userExist == []:
            await db_manager.profile(user_id)
            await db_manager.add_money(user_id, 200)
            await db_manager.add_item_to_inventory(user_id, "iron_sword", 1)
            await db_manager.add_item_to_inventory(user_id, "huntingbow", 1)
            await ctx.send(f"You have started your Journy, Welcome {ctx.message.author.name} to **Dank Streamer**.")
        else:
            await ctx.send("You have already started your journey.")
            
#get the quotes of a specific enemy
    @commands.hybrid_command(
        name="quotes",
        description="This command will view the quotes of a specific enemy.",
    )
    async def quotes(self, ctx: Context, enemy: str):
        """
        This command will view the quotes of a specific enemy.

        :param ctx: The context in which the command was called.
        :param enemy: The enemy that you want to view the quotes of.
        """
        quotes = await db_manager.get_enemy_quotes(enemy)
        if quotes == None or quotes == []:
            await ctx.send("That enemy doesn't have any quotes.")
        else:
            embed = discord.Embed(title="Quotes", description=f"{enemy}'s Quotes.", color=0x00ff00)
            for i in quotes:
                quote = i[1]
                embed.add_field(name="Quote", value=f"{quote}", inline=False)
            await ctx.send(embed=embed)        
    
        



#a command to give a user money using the add_money function from helpers\db_manager.py
    @commands.hybrid_command(
        name="give",
        description="This command will give a user money.",
    )
    async def give(self, ctx: Context, user: discord.Member, amount: int):
        """
        This command will give a user money.

        :param ctx: The context in which the command was called.
        :param user: The user that should be given money.
        :param amount: The amount of money that should be given.
        """
        user_id = ctx.message.author.id
        user_money = await db_manager.get_money(user_id)
        if user_money >= amount:
            await db_manager.add_money(user.id, amount)
            await db_manager.remove_money(user_id, amount)
            await ctx.send(f"You gave {user.mention} `{amount}`.")
        else:
            await ctx.send(f"You don't have enough money to give this user.")
        
    #a command to equip an item using the equip_item function from helpers\db_manager.py, check if the item has isEquippable set to true, if there are mutiple items of the same type, remove the old one and equip the new one, if there are mutliples of the same item, equip the first one, if the item is already equipped, say that it is already equipped, check that only one of the weapon and armor item type is equipped at a time
    @commands.hybrid_command(
        name="equip",
        description="This command will equip an item.",
    )
    async def equip(self, ctx: Context, item: str):
        """
        This command will equip an item.

        :param ctx: The context in which the command was called.
        :param item: The item that should be equipped.
        """
        user_id = ctx.message.author.id
        item_name = await db_manager.get_basic_item_name(item)
        item_type = await db_manager.get_basic_item_type(item)
        item_sub_type = await db_manager.get_basic_item_sub_type(item)
        item_equipped_id = await db_manager.id_of_item_equipped(user_id, item)
        print(item_equipped_id)
        print(item_type)
        if item_equipped_id == item:
            await ctx.send(f"`{item_name}` is already equipped.")
            return
        if item_type == "Weapon":
            weapon_equipped = await db_manager.is_weapon_equipped(user_id)
            if weapon_equipped == True:
                await ctx.send(f"You already have a weapon equipped.")
                return 
        
        if item_sub_type == "Ring":
            ring_equipped = await db_manager.is_item_sub_type_equipped(user_id, "Ring")
            if ring_equipped == True:
                await ctx.send(f"You already have a ring equipped.")
                return
            
        if item_sub_type == "Necklace":
            necklace_equipped = await db_manager.is_item_sub_type_equipped(user_id, "Necklace")
            if necklace_equipped == True:
                await ctx.send(f"You already have a necklace equipped.")
                return
            
        if item_sub_type == "Helmet":
            helmet_equipped = await db_manager.is_item_sub_type_equipped(user_id, "Helmet")
            if helmet_equipped == True:
                await ctx.send(f"You already have a helmet equipped.")
                return
            
        if item_sub_type == "Chestplate":
            chestplate_equipped = await db_manager.is_item_sub_type_equipped(user_id, "Chestplate")
            if chestplate_equipped == True:
                await ctx.send(f"You already have a chestplate equipped.")
                return
            
        if item_sub_type == "Leggings":
            leggings_equipped = await db_manager.is_item_sub_type_equipped(user_id, "Leggings")
            if leggings_equipped == True:
                await ctx.send(f"You already have leggings equipped.")
                return
            
        if item_sub_type == "Boots":
            boots_equipped = await db_manager.is_item_sub_type_equipped(user_id, "Boots")
            if boots_equipped == True:
                await ctx.send(f"You already have boots equipped.")
                return
            
        isEquippable = await db_manager.is_basic_item_equipable(item)
        if isEquippable == 1:
            await db_manager.equip_item(user_id, item)
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item)
            if item_effect == None or item_effect == "None":
                await ctx.send(f"You equipped `{item_name}`.")
                return
            print(item_effect)
            #split the effect by spaces
            item_effect = item_effect.split()
            #get the effect, the effect type, and the effect amount
            effect = item_effect[0]
            print(effect)
            effect_add_or_minus = item_effect[1]
            print(effect_add_or_minus)
            effect_amount = item_effect[2]
            print(effect_amount)
            #if the effect is health
            if effect == "health":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's health
                    await db_manager.add_health_boost(user_id, effect_amount)
                    await db_manager.add_health(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` health.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's health
                    await db_manager.remove_health_boost(user_id, effect_amount)
                    await db_manager.remove_health(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you -`{effect_amount}` health.")
                    
            #if the effect is damage
            elif effect == "damage":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's damage
                    await db_manager.add_damage_boost(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` damage.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's damage
                    await db_manager.remove_damage_boost(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you -`{effect_amount}` damage.")
                    
            #if the effect is luck
            elif effect == "luck":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's luck
                    await db_manager.add_luck(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` luck.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's luck
                    await db_manager.remove_luck(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you -`{effect_amount}` luck.")
                    
            #if the effect is crit chance
            elif effect == "crit_chance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's crit chance
                    await db_manager.add_crit_chance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` crit chance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's crit chance
                    await db_manager.remove_crit_chance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you -`{effect_amount}` crit chance.")
                    
            #if the effect is fire resistance
            elif effect == "fire_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's fire resistance
                    await db_manager.add_fire_resistance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` fire resistance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's fire resistance
                    await db_manager.remove_fire_resistance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you -`{effect_amount}` fire resistance.")
                    
            #if the effect is paralsys resistance
            elif effect == "paralysis_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's paralsys resistance
                    await db_manager.add_paralysis_resistance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` paralsys resistance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's paralsys resistance
                    await db_manager.remove_paralysis_resistance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you -`{effect_amount}` paralsys resistance.")
                    
            #if the effect is poison resistance
            elif effect == "poison_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's poison resistance
                    await db_manager.add_poison_resistance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` poison resistance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's poison resistance
                    await db_manager.remove_poison_resistance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you -`{effect_amount}` poison resistance.")
                    
            #if the effect is frost resistance
            elif effect == "frost_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's frost resistance
                    await db_manager.add_frost_resistance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` frost resistance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's frost resistance
                    await db_manager.remove_frost_resistance(user_id, effect_amount)
                    await ctx.send(f"You equipped `{item_name}`. It gave you -`{effect_amount}` frost resistance.")
        else:
            await ctx.send(f"that is not equippable.")
            
    #a command to unequip an item using the unequip_item function from helpers\db_manager.py, check if the item is equipped, if it is, unequip it, if it isn't, say that it isn't equipped
    @commands.hybrid_command(
        name="unequip",
        description="This command will unequip an item.",
    )
    async def unequip(self, ctx: Context, item: str):
        """
        This command will unequip an item.

        :param ctx: The context in which the command was called.
        :param item: The item that should be unequipped.
        """
        user_id = ctx.message.author.id
        item_name = await db_manager.get_basic_item_name(item)
        item_equipped_id = await db_manager.id_of_item_equipped(user_id, item)
        if item_equipped_id == item:
            #remove the item effect
            item_effect = await db_manager.get_basic_item_effect(item)
            if item_effect == "None":
                await db_manager.unequip_item(user_id, item)
                await ctx.send(f"You unequiped `{item_name}`.")
                return
            #split the effect by spaces
            item_effect = item_effect.split()
            #get the effect, the effect type, and the effect amount
            effect = item_effect[0]
            effect_add_or_minus = item_effect[1]
            effect_amount = item_effect[2]
            #if the effect is health
            if effect == "health":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's health
                    await db_manager.remove_health_boost(user_id, effect_amount)
                    await db_manager.remove_health(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you -`{effect_amount}` health.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's health
                    await db_manager.add_health_boost(user_id, effect_amount)
                    await db_manager.add_health(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you +`{effect_amount}` health.")
            #if the effect is damage
            elif effect == "damage":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's damage
                    await db_manager.remove_damage_boost(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you -`{effect_amount}` damage.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's damage
                    await db_manager.add_damage_boost(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you +`{effect_amount}` damage.")
            #if the effect is luck
            elif effect == "luck":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's luck
                    await db_manager.remove_luck(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you -`{effect_amount}` luck.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's luck
                    await db_manager.add_luck(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you +`{effect_amount}` luck.")
                    
            #if the effect is crit chance
            elif effect == "crit_chance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's crit chance
                    await db_manager.remove_crit_chance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you -`{effect_amount}` crit chance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's crit chance
                    await db_manager.add_crit_chance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you +`{effect_amount}` crit chance.")
                
            #if the effect is fire resistance
            elif effect == "fire_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's fire resistance
                    await db_manager.remove_fire_resistance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you -`{effect_amount}` fire resistance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's fire resistance
                    await db_manager.add_fire_resistance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you +`{effect_amount}` fire resistance.")
            
            #if the effect is poison resistance
            elif effect == "poison_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's poison resistance
                    await db_manager.remove_poison_resistance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you -`{effect_amount}` poison resistance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's poison resistance
                    await db_manager.add_poison_resistance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you +`{effect_amount}` poison resistance.")
                    
            #if the effect is frost resistance
            elif effect == "frost_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's frost resistance
                    await db_manager.remove_frost_resistance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you -`{effect_amount}` frost resistance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's frost resistance
                    await db_manager.add_frost_resistance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you +`{effect_amount}` frost resistance.")
                    
            #if the effect is paralysis resistance
            elif effect == "paralysis_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's paralysis resistance
                    await db_manager.remove_paralysis_resistance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you -`{effect_amount}` paralysis resistance.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's paralysis resistance
                    await db_manager.add_paralysis_resistance(user_id, effect_amount)
                    await ctx.send(f"You unequipped `{item_name}`. It gave you +`{effect_amount}` paralysis resistance.")
            await db_manager.unequip_item(user_id, item)
            await ctx.send(f"You unequipped `{item_name}`")
        else:
            await ctx.send(f"`{item_name}` is not equipped.")
            
    #command to get info about an item
    @commands.hybrid_command(
        name="iteminfo",
        description="This command will get info about an item.",
    )
    async def iteminfo(self, ctx: Context, item: str):
        #convert the item to an item id
        #if the item has a space in it, remove it 
        if " " in item:
            item_id = item.replace(" ", "")
        else:
            item_id = item
        #if the item is lowercase, make it uppercase
        #get the item info from the database
        item_info = await db_manager.get_basic_item_name(item_id)
        print(item_info)
        #if the item doesn't exist, send a message
        if item_info == 0:
            await ctx.send(f"Item `{item_id}` doesn't exist.")
            return
        #get the item rarity
        item_rarity = await db_manager.get_basic_item_rarity(item_id)
        #get the item emoji
        is_item_basic = await db_manager.check_basic_item(item_id)
        is_item_streamer = await db_manager.check_streamer_item(item_id)
        basic_item_emote = await db_manager.get_basic_item_emote(item_id)
        check_emoji = await db_manager.check_emoji(basic_item_emote)
        print(check_emoji)
        print("is BASIC: " + str(is_item_basic))
        print("is STREAMER: " + str(is_item_streamer))
        if check_emoji == 0:
            if is_item_basic == 1:
                basic_item_emote = await db_manager.get_basic_item_emote(item_id)
                print(basic_item_emote)
                emoji_unicode = ('{:X}'.format(ord(basic_item_emote)))
                emoji_unicode = emoji_unicode.lower()
                #make a web request to get the emoji name
                emoji_url = f"https://images.emojiterra.com/google/noto-emoji/v2.034/128px/{emoji_unicode}.png"
                #get the emoji object
                #convert emoji unicode to image url
                #get the image url of the unicode emoji
                #get the item damage
                item_damage = await db_manager.get_basic_item_damage(item_id)
                #get the item type
                item_type = await db_manager.get_basic_item_type(item_id)
                item_element = await db_manager.get_basic_item_element(item_id)
                print(item_element)
                item_crit_chance = await db_manager.get_basic_item_crit_chance(item_id)
                #get the item price
                item_price = await db_manager.get_basic_item_price(item_id)
                #get the item description
                item_description = await db_manager.get_basic_item_description(item_id)
                #get the item name
                item_name = await db_manager.get_basic_item_name(item_id)
                #check if the item has a recipe
                hasRecipe = await db_manager.check_item_recipe(item_id)
                if hasRecipe == 1:
                    item_recipe = await db_manager.get_item_recipe(item_id)
                #get the items rarity
                rarity = await db_manager.get_basic_item_rarity(item_id)
                rarity = str(rarity)
                if rarity == "Common":
                    rarity_color="0x808080"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Uncommon":
                    rarity_color="0x00B300"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Rare":
                    rarity_color="0x0057C4"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Epic":
                    rarity_color="0xa335ee"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Legendary":
                    rarity_color="0xff8000"
                    rarity_color = int(rarity_color, 16)
                #create an embed
                embed = discord.Embed(
                    title=f"{item_name}",
                    description=f"{item_description}",
                    color=rarity_color
                )
                #add the rarity to the embed
                #set the thumbnail to the item emoji
                print(emoji_url)
                embed.set_thumbnail(url=emoji_url)
                embed.add_field(name="Rarity", value=f"{item_rarity}")
                #if the item is a weapon, add the damage
                if item_type == "Weapon":
                    embed.add_field(name="Damage", value=f"{item_damage}")
                    embed.add_field(name="Crit Chance", value=f"{item_crit_chance}")
                #if the item is armor, add the Defence
                elif item_type == "Armor":
                    embed.add_field(name="Defence", value=f"{item_damage}")
                #add the price to the embed
                embed.add_field(name="Price", value=f"{item_price}")
                if hasRecipe == 1:
                    embed.add_field(name="Recipe", value="Yes")
                    print(item_recipe)
                #if the item has a recipe, add the recipe to the embed
                if hasRecipe == 0:
                    pass
                else:
                    for feild in embed.fields:
                        for item in item_recipe:
                            if feild.name == "Recipe":
                            #convert the item to a string
                                item = str(item)
                                #remove the item_id from the string 
                                item = item.replace("(", "")
                                item = item.replace(")", "")
                                item = item.replace(",", "")
                                item = item.replace("'", "")
                                item = item.replace(item_id, "")
                                itemNumber = re.sub(r'\D', '', item)
                                print(itemNumber)
                                itemId = re.sub(r'\d', '', item)
                                print(itemId)
                                #remove any spaces from the string
                                itemId = itemId.replace(" ", "")
                                #get the item name from the item id
                                itemName = await db_manager.get_basic_item_name(itemId)
                                #convert it to a string
                                itemName = str(itemName)
                                #remove the item id from the string
                                itemName = itemName.replace("(", "")
                                itemName = itemName.replace(")", "")
                                itemName = itemName.replace(",", "")
                                itemName = itemName.replace("'", "")
                                #itemName = itemName.replace(itemId, "")
                                #remove any spaces from the string
                                print(itemName)
                                #remove any numbers from the string
                                #add each item to the feild
                                #remove Yes from the feild
                                feild.value = feild.value.replace("Yes", "")
                                feild.value = feild.value + "\n" + f"{itemName} x{itemNumber}"
                                #remove yes from the feild
                                embed_dict = embed.to_dict()
                                for field in embed_dict['fields']:
                                    if field['name'] == 'Recipe':
                                        field['value'] = feild.value
                                        
                                # Converting the embed to a `discord.Embed` obj
                                edited_embed = discord.Embed.from_dict(embed_dict)
                                
                #add the crit chance to the embed
                embed.add_field(name="Type", value=f"{item_type}")
                if item_element == "None" or item_element == "none" or item_element == 0:
                    pass
                else:
                    embed.add_field(name="Sub-Type", value=f"{item_element}")
                embed.set_footer(text="Item ID: " + item_id)
                #send the embed
                if hasRecipe == 1 or hasRecipe == True:
                    edited_embed.add_field(name="Type", value=f"{item_type}")
                    if item_element == "None" or item_element == "none" or item_element == 0:
                        pass
                    else:
                        edited_embed.add_field(name="Sub-Type", value=f"{item_element}")
                        edited_embed.set_footer(text="Item ID: " + item_id)
                    await ctx.send(embed=edited_embed)
                    return
                else:
                    await ctx.send(embed=embed)
                    return
            elif is_item_streamer == 1:
                streamer_item_emote = await db_manager.get_streamer_item_emote(item_id)
                streamer_name = await db_manager.get_streamer_name_from_item(item_id)
                emoji_unicode = ('{:X}'.format(ord(streamer_item_emote)))
                emoji_unicode = emoji_unicode.lower()
                #make a web request to get the emoji name
                emoji_url = f"https://images.emojiterra.com/google/noto-emoji/v2.034/128px/{emoji_unicode}.png"
                #get the item damage
                #get the item type
                item_type = await db_manager.get_streamer_item_type(item_id)
                #get the item price
                item_price = await db_manager.get_streamer_item_price(item_id)
                #get the item description
                #get the item name
                item_name = await db_manager.get_streamer_item_name(item_id)
                item_crit_chance = await db_manager.get_streamer_item_crit_chance(item_id)
                item_damage = await db_manager.get_streamer_item_damage(item_id)
                #create an embed
                #get the items rarity
                rarity = await db_manager.get_basic_item_rarity(item_id)
                rarity = str(rarity)
                if rarity == "Common":
                    rarity_color="0x808080"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Uncommon":
                    rarity_color="0x00B300"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Rare":
                    rarity_color="0x0057C4"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Epic":
                    rarity_color="0xa335ee"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Legendary":
                    rarity_color="0xff8000"
                    rarity_color = int(rarity_color, 16)
                #create an embed
                embed = discord.Embed(
                    title=f"{item_name}",
                    description=f"{item_description}",
                    color=rarity_color
                )
                #add the rarity to the embed
                #set the thumbnail to the item emoji
                print(emoji_url)
                embed.set_thumbnail(url=emoji_url)
                embed.add_field(name="Rarity", value=f"{item_rarity}")
                #if the item is a weapon, add the damage
                if item_type == "Weapon":
                    embed.add_field(name="Damage", value=f"{item_damage}")
                    embed.add_field(name="Crit Chance", value=f"{item_crit_chance}")
                #if the item is armor, add the Defence
                elif item_type == "Armor":
                    embed.add_field(name="Defence", value=f"{item_damage}")
                #add the price to the embed
                embed.add_field(name="Price", value=f"{item_price}")
                #add the crit chance to the embed
                embed.add_field(name="Type", value=f"{item_type}")
                if item_element == "None" or item_element == "none" or item_element == 0:
                    pass
                else:
                    embed.add_field(name="Sub-Type", value=f"{item_element}")
                

                embed.set_footer(text="Item ID: " + item_id)
                #send the embed
                await ctx.send(embed=embed)
                return
        elif check_emoji == 1:
            if is_item_basic == 1:
                basic_item_emote = await db_manager.get_basic_item_emote(item_id)
                basic_item_emote = basic_item_emote.replace("<", "")
                basic_item_emote = basic_item_emote.replace(">", "")
                colon_index = basic_item_emote.index(":")
                colon_index = basic_item_emote.index(":", colon_index + 1)
                # Create a new string starting from the character after the second colon
                new_s = basic_item_emote[colon_index + 1:]
                #remove evrything from the string, after the second :, then itll work :)
                print(new_s)
                emoji_url = f"https://cdn.discordapp.com/emojis/{new_s}.png"
                #convert the unicode emoji to a string
                print(emoji_url)
                #get the item damage
                item_damage = await db_manager.get_basic_item_damage(item_id)
                #get the item type
                item_type = await db_manager.get_basic_item_type(item_id)
                item_element = await db_manager.get_basic_item_element(item_id)
                print(item_element)
                item_crit_chance = await db_manager.get_basic_item_crit_chance(item_id)
                #get the item price
                item_price = await db_manager.get_basic_item_price(item_id)
                #get the item description
                item_description = await db_manager.get_basic_item_description(item_id)
                #get the item name
                item_name = await db_manager.get_basic_item_name(item_id)
                #check if the item has a recipe
                hasRecipe = await db_manager.check_item_recipe(item_id)
                if hasRecipe == 1:
                    item_recipe = await db_manager.get_item_recipe(item_id)
                #get the items rarity
                rarity = await db_manager.get_basic_item_rarity(item_id)
                rarity = str(rarity)
                if rarity == "Common":
                    rarity_color="0x808080"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Uncommon":
                    rarity_color="0x00B300"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Rare":
                    rarity_color="0x0057C4"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Epic":
                    rarity_color="0xa335ee"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Legendary":
                    rarity_color="0xff8000"
                    rarity_color = int(rarity_color, 16)
                #create an embed
                embed = discord.Embed(
                    title=f"{item_name}",
                    description=f"{item_description}",
                    color=rarity_color
                )
                #add the rarity to the embed
                #set the thumbnail to the item emoji
                print(emoji_url)
                embed.set_thumbnail(url=emoji_url)
                embed.add_field(name="Rarity", value=f"{item_rarity}")
                #if the item is a weapon, add the damage
                if item_type == "Weapon":
                    embed.add_field(name="Damage", value=f"{item_damage}")
                    embed.add_field(name="Crit Chance", value=f"{item_crit_chance}")
                #if the item is armor, add the Defence
                elif item_type == "Armor":
                    embed.add_field(name="Defence", value=f"{item_damage}")
                #add the price to the embed
                embed.add_field(name="Price", value=f"{item_price}")
                if hasRecipe == 1 or hasRecipe == True:
                    embed.add_field(name="Recipe", value="Yes")
                    print(item_recipe)
                #if the item has a recipe, add the recipe to the embed
                if hasRecipe == 0 or hasRecipe == False:
                    pass
                else:
                    for feild in embed.fields:
                        for item in item_recipe:
                            if feild.name == "Recipe":
                            #convert the item to a string
                                item = str(item)
                                #remove the item_id from the string 
                                item = item.replace("(", "")
                                item = item.replace(")", "")
                                item = item.replace(",", "")
                                item = item.replace("'", "")
                                item = item.replace(item_id, "")
                                itemNumber = re.sub(r'\D', '', item)
                                print(itemNumber)
                                itemId = re.sub(r'\d', '', item)
                                print(itemId)
                                #remove any spaces from the string
                                itemId = itemId.replace(" ", "")
                                #get the item name from the item id
                                itemName = await db_manager.get_basic_item_name(itemId)
                                #convert it to a string
                                itemName = str(itemName)
                                #remove the item id from the string
                                itemName = itemName.replace("(", "")
                                itemName = itemName.replace(")", "")
                                itemName = itemName.replace(",", "")
                                itemName = itemName.replace("'", "")
                                #itemName = itemName.replace(itemId, "")
                                #remove any spaces from the string
                                print(itemName)
                                #remove any numbers from the string
                                #add each item to the feild
                                #remove Yes from the feild
                                feild.value = feild.value.replace("Yes", "")
                                feild.value = feild.value + "\n" + f"{itemName} x{itemNumber}"
                                #remove yes from the feild
                                #get the index of the Recipe feild
                                embed_dict = embed.to_dict()
                                for field in embed_dict['fields']:
                                    if field['name'] == 'Recipe':
                                        field['value'] = feild.value
                                        
                                # Converting the embed to a `discord.Embed` obj
                                edited_embed = discord.Embed.from_dict(embed_dict)
                #add the crit chance to the embed
                embed.add_field(name="Type", value=f"{item_type}")
                if item_element == "None" or item_element == "none" or item_element == 0:
                    pass
                else:
                    embed.add_field(name="Sub-Type", value=f"{item_element}")
                embed.set_footer(text="Item ID: " + item_id)
                #send the embed
                if hasRecipe == 1 or hasRecipe == True:
                    edited_embed.add_field(name="Type", value=f"{item_type}")
                    if item_element == "None" or item_element == "none" or item_element == 0:
                        pass
                    else:
                        edited_embed.add_field(name="Sub-Type", value=f"{item_element}")
                        edited_embed.set_footer(text="Item ID: " + item_id)
                    await ctx.send(embed=edited_embed)
                    return
                else:
                    await ctx.send(embed=embed)
                    return
            elif is_item_streamer == 1:
                streamer_item_emote = await db_manager.get_streamer_item_emote(item_id)
                streamer_name = await db_manager.get_streamer_name_from_item(item_id)
                print(streamer_item_emote)
                #strip the item emoji of : and <> and numbers
                #remove the < and > from the string
                streamer_item_emote = streamer_item_emote.replace("<", "")
                streamer_item_emote = streamer_item_emote.replace(">", "")
                colon_index = streamer_item_emote.index(":")
                colon_index = streamer_item_emote.index(":", colon_index + 1)
                # Create a new string starting from the character after the second colon
                new_s = streamer_item_emote[colon_index + 1:]
                #remove evrything from the string, after the second :, then itll work :)
                print(new_s)
                emoji_url = f"https://cdn.discordapp.com/emojis/{new_s}.png"
                #convert the unicode emoji to a string
                print(emoji_url)
                #get the emoji object
                #convert emoji unicode to image url
                #get the image url of the unicode emoji
                #get the item damage
                #get the item type
                item_type = await db_manager.get_streamer_item_type(item_id)
                #get the item price
                item_price = await db_manager.get_streamer_item_price(item_id)
                #get the item description
                #get the item name
                item_name = await db_manager.get_streamer_item_name(item_id)
                item_crit_chance = await db_manager.get_streamer_item_crit_chance(item_id)
                item_damage = await db_manager.get_streamer_item_damage(item_id)
                 #get the items rarity
                rarity = await db_manager.get_basic_item_rarity(item_id)
                rarity = str(rarity)
                if rarity == "Common":
                    rarity_color="0x808080"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Uncommon":
                    rarity_color="0x00B300"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Rare":
                    rarity_color="0x0057C4"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Epic":
                    rarity_color="0xa335ee"
                    rarity_color = int(rarity_color, 16)

                elif rarity == "Legendary":
                    rarity_color="0xff8000"
                    rarity_color = int(rarity_color, 16)
                #create an embed
                embed = discord.Embed(
                    title=f"{item_name}",
                    description=f"{item_description}",
                    color=rarity_color
                )
                #add the rarity to the embed
                #set the thumbnail to the item emoji
                embed.set_thumbnail(url=emoji_url)
                embed.add_field(name="Rarity", value=f"{item_rarity}")
                #if the item is a weapon, add the damage
                if item_type == "Weapon":
                    embed.add_field(name="Damage", value=f"{item_damage}")
                    embed.add_field(name="Crit Chance", value=f"{item_crit_chance}")
                #if the item is armor, add the Defence
                elif item_type == "Armor":
                    embed.add_field(name="Defence", value=f"{item_damage}")
                #add the price to the embed
                embed.add_field(name="Price", value=f"{item_price}")
                #add the crit chance to the embed
                embed.add_field(name="Type", value=f"{item_type}")
                if item_element == "None" or item_element == "none" or item_element == 0:
                    pass
                else:
                    embed.add_field(name="Sub-Type", value=f"{item_element}")
                embed.set_footer(text="Item ID: " + item_id)
                #send the embed
                await ctx.send(embed=embed)
    #hybrid command to battle another player
    @commands.hybrid_command(
        name="deathbattle",
        description="Battle another player",
    )
    async def deathbattle(self, ctx: Context, user: discord.Member):
        #run the battle function from helper/battle.py
        enemy_id = user.id
        user_id = ctx.author.id

        #check if the user is in the database
        user_in_db = await db_manager.check_if_user_in_db(user_id)
        if user_in_db == False:
            await ctx.send("You are not in the database yet, please use the start command to start your adventure!")
            return
        #check if the enemy is in the database
        enemy_in_db = await db_manager.check_if_user_in_db(enemy_id)
        if enemy_in_db == False:
            await ctx.send("The enemy is not in the database yet, they need to use the start command to start their adventure!")
            return
        #check if the user is in a battle
        user_in_battle = await db_manager.is_in_combat(user_id)
        if user_in_battle == True:
            await ctx.send("You are already in a battle!")
            return
        #check if the enemy is in a battle
        enemy_in_battle = await db_manager.is_in_combat(enemy_id)
        if enemy_in_battle == True:
            await ctx.send("The enemy is already in a battle!")
            return
        #check if the user is dead
        user_is_alive = await db_manager.is_alive(user_id)
        if user_is_alive == False:
            await ctx.send("You are dead! wait to respawn! or use an item to revive!")
            return
        #check if the enemy is dead
        enemy_is_alive = await db_manager.is_alive(enemy_id)
        if enemy_is_alive == False:
            await ctx.send("The enemy is dead! wait for them to respawn! or tell them to use an item to revive!")
            return

        await ctx.send(f"{ctx.author.name} is challenging {user.name} to a death battle!")
        author_name = ctx.author.name
        enemy_name = user.name
        await battle.deathbattle(ctx, user_id, enemy_id, author_name, enemy_name)
        
    #hybrid command to battle a monster
    @commands.hybrid_command(
        name="battle",
        description="Battle a monster",
    )
    async def battle(self, ctx: Context, monsterid: str):
        #run the battle function from helper/battle.py
        user_id = ctx.author.id
        #check if the user is in the database
        user_in_db = await db_manager.check_if_user_in_db(user_id)
        if user_in_db == False:
            await ctx.send("You are not in the database yet, please use the `/start` command to start your adventure!")
            return
        #check if the user is in a battle
        user_in_battle = await db_manager.is_in_combat(user_id)
        if user_in_battle == True:
            await ctx.send("You are already in a battle!")
            return
        #check if the user is dead
        user_is_alive = await db_manager.is_alive(user_id)
        if user_is_alive == False:
            await ctx.send("You are dead! wait to respawn! or use an item to revive!")
            return
        #check if the monster is in the database
        monster_in_db = await db_manager.check_enemy(monsterid)
        if monster_in_db == False:
            await ctx.send("This monster does not exist!")
            return
        
        #get the monster name from its ID
        monsterName = await db_manager.get_enemy_name(monsterid)
        
        #check if the monster is alive
        #check if the monster is in a battle
        await ctx.send(f"{ctx.author.name} is challenging {monsterid} to a battle!")
        author_name = ctx.author.name
        await battle.deathbattle_monster(ctx, user_id, author_name, monsterid, monsterName)
    
        
    #command to connect their discord account to their twitch account
    @commands.hybrid_command(
        name="connect",
        description="Connect your twitch account to your discord account!",
    )
    async def connect(self, ctx: Context):
        #create an embed to send to the user, then add a button to connect their twitch account
        embed = discord.Embed(
            title="Connect your twitch account to your discord account!",
            description="Click the button below to connect your twitch account to your discord account!",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/881056455321487390/881056516333762580/unknown.png")
        embed.set_footer(text="DankStreamer")
        #make a discord.py button interaction
        class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
            def __init__(self, url: str):
                super().__init__()
                self.url = url
                self.add_item(discord.ui.Button(label="Register With Twitch!", url=self.url))
        #send the embed to the user in DMs
        #get the guild object from the guild ID
        guild = self.bot.get_guild(1070882685855211641)
        #create a new channel in the guild
        channel = await guild.create_text_channel("twitch-auth")
        #create a webhook in the channel
        webhook = await channel.create_webhook(name="twitch-auth")
        #get the webhook url
        webhook_url = webhook.url
        await ctx.send("Check your DMs :)")
        await ctx.author.send(embed=embed, view=MyView(f"https://dankstreamer.lol/webhook?url={webhook_url}")) # Send a message with our View class that contains the button
        #send the users discord ID to the webhook 
        #webhook_url = "https://discord.com/api/webhooks/1069631304196436029/4kR9H23BJ5f14U1U3ZuTXEo9vhoBC5zBN9E1j1nz7etj1pHf2Vq14eiE1aWb50JpYDG3"
        webhook = SyncWebhook.from_url(webhook_url)
        webhook.send(f"DISCORD ID: {ctx.author.id}")

        #WATCH THIS VIDEO FOR HELP https://www.youtube.com/watch?v=Ip0M_yxUwfg&ab_channel=Glowstik
            
        ##put the twitch name in lowercase
        #twitch_name = twitch_name.lower()
        ##get the streamerID from the database
        #twitchID = await db_manager.get_twitch_id(twitch_name)
        #print(twitchID)
        ##are they already connected?
        #await db_manager.connect_twitch(ctx.author.id, twitchID)
        #isConnected = await db_manager.is_connected(ctx.author.id)
        #print(isConnected)
        #exists = await db_manager.twitch_exists(twitchID)
        ##check if the streamerID is in the database
        #if exists == True:
        #    await ctx.send(f"This twitch account is already connected to a discord account, or does not exist!")
        #elif exists == False:
        #    await ctx.send(f"Your twitch account is now connected to your discord account!, You can now earn items and money by watching streamers connected to DankStreamer!")

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
        
    @commands.hybrid_command(
        name="fight",
        description="Fight a user!",
    )
    async def fight(self, ctx: Context, user: discord.Member):
        #check if the user is in a battle
        #check if the user is in a battle
        user_is_in_battle = await db_manager.is_in_combat(ctx.author.id)
        if user_is_in_battle == True:
            await ctx.send("You are already in a battle!")
            return
        #check if the user is dead
        user_is_alive = await db_manager.is_alive(ctx.author.id)
        if user_is_alive == False:
            await ctx.send("You are dead! wait to respawn! or use an item to revive!")
            return
        #check if the user is in a battle
        user_is_in_battle = await db_manager.is_in_combat(user.id)
        if user_is_in_battle == True:
            await ctx.send("This user is already in a battle!")
            return
        #check if the user is dead
        user_is_alive = await db_manager.is_alive(user.id)
        if user_is_alive == False:
            await ctx.send("This user is dead! wait till they respawn! or they use an item to revive!")
            return
        
        user_exists = await db_manager.check_user(user.id)
        if user_exists == None:
            await ctx.send("This user does not exist!, tell them to do /start to start playing!")
            return
        
        #ask the user if they want to fight
        await ctx.send(f"{user.mention} is Challenging {ctx.author.mention} to a fight! Do you accept? (yes/no)")
        #wait for a response
        def check(m):
            return m.author == user and m.channel == ctx.channel
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("They did not accept the fight!")
            return
        if msg.content.lower() == "yes":
            await ctx.send("The fight has begun!")
            await battle.deathbattle(ctx, ctx.author.id, user.id, ctx.author.name, user.name)
        elif msg.content.lower() == "no":
            await ctx.send("They did not accept the fight!")
            return
        
    #hunt command
    #command cooldown of 2 hours
    @commands.hybrid_command(
        name="hunt",
        description="Hunt for items in the Forest!",
    )
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def hunt(self, ctx: Context):
        #restset the cooldown
            #check if the user has a bow
        if await db_manager.check_user(ctx.author.id) == 0:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.hunt.reset_cooldown(ctx)
            return
        isbowThere = await db_manager.is_item_in_inventory(ctx.author.id, "huntingbow")
        if isbowThere == False or isbowThere == None or isbowThere == 0:
            await ctx.send("You need a Bow to go Hunting!")
            self.hunt.reset_cooldown(ctx)
            return
        else:
            await hunt.hunt(ctx)
        
    #mine command
    #command cooldown of 2 hours
    @commands.hybrid_command(
        name="mine",
        description="Mine for items in the Caves!",
    )
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def mine(self, ctx: Context):
        if await db_manager.check_user(ctx.author.id) == 0:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.mine.reset_cooldown(ctx)
            return
        # check if the user has a pickaxe
        is_pickaxe_there = await db_manager.is_item_in_inventory(ctx.author.id, "pickaxe")
        if not is_pickaxe_there:
            await ctx.send("You need a pickaxe to mine! You can buy one in the shop.")
            self.mine.reset_cooldown(ctx)
            return
        else:
            await mine.mine(ctx)

    @commands.hybrid_command(
        name="use",
        description="This command will use an item.",
    )
    async def use(self, ctx: Context, item: str):
        """
        This command will use an item.
        :param ctx: The context in which the command was called.
        :param item: The item that should be used.
        """
        if await db_manager.check_user(ctx.author.id) == 0:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.use.reset_cooldown(ctx)
            return
        user_id = ctx.message.author.id
        item_name = await db_manager.get_basic_item_name(item_id)
        isUsable = await db_manager.is_basic_item_usable(item_id)
        if isUsable == 1:
            #remove item from inventory
            await db_manager.remove_item_from_inventory(user_id, item_id, 1)
            #STUB - item effects
            #if the item's name is "Potion", add 10 health to the user
            #get the items effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            #if the item effect is "None":
            if item_effect == "None":
                item_effect = "None"
            else:
                #split the item effect by space
                item_effect = item_effect.split(" ")
                #get the item effect type
                item_effect_type = item_effect[0]
                #get the item effect amount
                item_effect_amount = item_effect[2]
            #if the item effect type is "health"
            if item_effect_type == "heal":
                userHealth = await db_manager.get_health(user_id)
                #if the user is full health, don't add health and send a message
                if userHealth == 100:
                    await ctx.send("You are already at full health!")
                    return
                #add the item effect amount to the users health
                await db_manager.add_health(user_id, item_effect_amount)
                await ctx.send(f"You used `{item_name}` and healed for {item_effect_amount} health!")

            #if the item effect is "revive"
            if item_effect_type == "revive":
                #if the user is alive, don't revive them and send a message
                if await db_manager.is_alive(user_id) == True or 1:
                    await ctx.send("You are already alive!")
                    return
                #revive the user
                await db_manager.set_alive(user_id)
                #add the item effect amount to the users health
                await db_manager.add_health(user_id, 100)
                await ctx.send(f"You used `{item_name}` and revived!")
                return

            #split the item_id by the "_"
            chest_name = await db_manager.get_basic_item_name(item_id)
            item_id = item_id.split("_")
            luck = await db_manager.get_luck(user_id)
            #if item[0] is chest
            if item_id[0] == "chest":

                outcomePhrases = [
                    "You opened the chest and found ",
                    "As you pried open the chest, you discovered ",
                    "With a satisfying creak, the chest opened to reveal ",
                    "Inside the chest, you found ",
                    "You eagerly opened the chest to reveal ",
                    "With bated breath, you lifted the lid of the chest and uncovered ",
                    "The chest was heavy, but it was worth it when you saw ",
                    "With a sense of anticipation, you opened the chest and saw ",
                    "You were rewarded for your efforts with ",
                    "Inside the chest, you were delighted to find "
                ]

                #get the chest contents
                chest_contents = await db_manager.get_chest_contents(item_id)
                #calculate the chest contents chances
                #organize the chest items by their chest chance
                chest_contents.sort(key=lambda x: x[2], reverse=True)
                #get the user's luck
                luck = await db_manager.get_luck(ctx.author.id)

                #roll a number between 1 and 100, the higher the luck, the higher the chance of getting a higher number, the higher the number, the higher the chance of getting a better item, which is determined by the hunt chance of each item, the higher the hunt chance, the higher the chance of getting that item
                roll = random.randint(1, 100) - luck
                #if the roll is greater than 100, set it to 100
                if roll > 100:
                    roll = 100

                #if the roll is less than 1, set it to 1
                if roll < 1:
                    roll = 1


                lowchanceitems = []
                for item in chest_contents:
                    if item[2] <= 0.1:
                        lowchanceitems.append(item)

                midchanceitems = []
                for item in chest_contents:
                    if item[2] > 0.1 and item[2] <= 0.5:
                        midchanceitems.append(item)

                highchanceitems = []
                for item in chest_contents:
                    if item[2] > 0.5 and item[2] <= 1:
                        highchanceitems.append(item)

                #based on the roll, get the item
                if roll <= 10:
                    item = random.choice(lowchanceitems)
                elif roll > 10 and roll <= 50:
                    item = random.choice(midchanceitems)
                elif roll > 50 and roll <= 90:
                    item = random.choice(highchanceitems)
                elif roll > 90:
                    #they found nothing
                    await ctx.send(f"It seems {chest_name} ened up being empty!")
                    return
                
                await db_manager.add_item_to_inventory(ctx.author.id, item[0])
                item_name = await db_manager.get_basic_item_name(item[0])
                item_emoji = await db_manager.get_basic_item_emote(item[0])
                #tell the user what they got
                await ctx.send(random.choice(outcomePhrases) + f"{item_emoji} **{item_name}** - {item[1]}")
                return   
        else:
            await ctx.send(f"`{item_name}` is not usable.")
            
            
    #explore command
    @commands.hybrid_command()
    #command cooldown of 5 minutes
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def explore(self, ctx: Context, structure: str):
        #check if the user exists in the database
        if await db_manager.check_user(ctx.author.id) == 0:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.explore.reset_cooldown(ctx)
            return
        #get the current structure in the channel
        await db_manager.add_explorer_log(ctx.guild.id, ctx.author.id)
        structure_outcomes = await db_manager.get_structure_outcomes(structure)
        msg = ctx.message
        #get the structure outcomes
        luck = await db_manager.get_luck(msg.author.id)
        #for each outcome, calculate the chance of it happening based on the outcome chance and the users luck
            #get the hunt chance for each item in the huntitems list
        outcomes = []
        for outcome in structure_outcomes:
            print(outcome)
            print(len(outcome))
            #`structure_quote` varchar(255) NOT NULL,
            #`structure_state` varchar(255) NOT NULL,
            #`outcome_chance` int(11) NOT NULL,
            #`outcome_type` varchar(255) NOT NULL,
            #`outcome` varchar(255) NOT NULL,
            #`outcome_amount` varchar(11) NOT NULL,
            #`outcome_money` varchar(11) NOT NULL,
            #`outcome_xp` varchar(11) NOT NULL,

            quote = outcome[1]
            state = outcome[2]
            outcome_chance = outcome[3]
            outcome_type = outcome[4]
            outcome_thing = outcome[5]
            outcome_amount = outcome[6]
            outcome_money = outcome[7]
            outcome_xp = outcome[8]
            #add the outcome to the outcomes list
            outcomes.append([quote, state, outcome_chance, outcome_type, outcome_thing, outcome_amount, outcome_money, outcome_xp])
        
        #sort the outcomes list by the chance of the outcome happening
        outcomes.sort(key=lambda x: x[2], reverse=True)

        #roll a number between 1 and 100, the higher the luck, the higher the chance of getting a higher number, the higher the number, the higher the chance of getting a better item, which is determined by the hunt chance of each item, the higher the hunt chance, the higher the chance of getting that item
        roll = random.randint(1, 100) - luck
        #if the roll is greater than 100, set it to 100
        if roll > 100:
            roll = 100

        #if the roll is less than 1, set it to 1
        if roll < 1:
            roll = 1

        #get the items with the hunt chance 0.01 or lower
        lowchanceitems = []
        for item in outcomes:
            if item[2] <= 0.1:
                lowchanceitems.append(item)

        midchanceitems = []
        for item in outcomes:
            if item[2] > 0.1 and item[2] <= 0.5:
                midchanceitems.append(item)

        highchanceitems = []
        for item in outcomes:
            if item[2] > 0.5 and item[2] <= 1:
                highchanceitems.append(item)

        #based on the roll, get the item
        if roll <= 10:
            try:
                item = random.choice(lowchanceitems)
            except(IndexError):
                item = random.choice(outcomes)
        elif roll > 10 and roll <= 50:
            try:
                item = random.choice(midchanceitems)
            except(IndexError):
                item = random.choice(lowchanceitems)
        elif roll > 50 and roll <= 100:
            try:
                item = random.choice(highchanceitems)
            except(IndexError):
                item = random.choice(midchanceitems)
        
        #get the info of the item
        outcome_quote = item[0]
        outcome_state = item[1]
        outcome_chance = item[2]
        outcome_type = item[3]
        outcome_thing = item[4]
        outcome_amount = item[5]
        outcome_money = item[6]
        outcome_xp = item[7]
        
        #the outcome_types are: item_gain, item_loss, health_loss, health_gain, money_gain, money_loss, battle
        #if the outcome type is item_gain
        #get the outcome_icon
        #remove the line breaks from the outcome_quote
        outcome_thing = str(outcome_thing)
        outcome_quote = str(outcome_quote)
        outcome_quote = outcome_quote.strip()
        if outcome_type == "item_gain":
            #if outcome things first word is chest, then add a to the end of the outcome_quote
            if outcome_thing.split("_")[0] == "chest":
                outcome_icon = await db_manager.get_chest_icon(outcome_thing)
                outcome_name = await db_manager.get_chest_name(outcome_thing)
            else:
                outcome_name = await db_manager.get_basic_item_name(outcome_thing)
                outcome_icon = await db_manager.get_basic_item_emote(outcome_thing)
            #send a message saying the outcome, and the item gained
            await ctx.send(f"{outcome_quote} + {outcome_amount} {outcome_icon} **{outcome_name}**")
            #add the item to the users inventory
            await db_manager.add_item_to_inventory(msg.author.id, outcome_thing, outcome_amount)
        #if the outcome type is item_loss
        elif outcome_type == "item_loss":
            if outcome_thing.split("_")[0] == "chest":
                outcome_icon = await db_manager.get_chest_icon(outcome_thing)
                outcome_name = await db_manager.get_chest_name(outcome_thing)
            else:
                outcome_name = await db_manager.get_basic_item_name(outcome_thing)
                outcome_icon = await db_manager.get_basic_item_emote(outcome_thing)
            #send a message saying the outcome, and the item lost
            await ctx.send(f"{outcome_quote} + {outcome_amount} {outcome_icon} **{outcome_name}**")
            #remove the item from the users inventory
            await db_manager.remove_item_from_inventory(msg.author.id, outcome_thing, outcome_amount)
        #if the outcome type is health_loss
        elif outcome_type == "health_loss":
            #send a message saying the outcome, and the health lost
            await ctx.send(f"{outcome_quote} - {outcome_amount} health!")
            #remove the health from the users health
            await db_manager.remove_health(msg.author.id, outcome_amount)
        #if the outcome type is health_gain
        elif outcome_type == "health_gain":
            #send a message saying the outcome, and the health gained
            await ctx.send(f"{outcome_quote} + {outcome_amount} health!")
            #add the health to the users health
            await db_manager.add_health(msg.author.id, outcome_amount)
        #if the outcome type is money_gain
        elif outcome_type == "money_gain":
            #send a message saying the outcome, and the money gained
            await ctx.send(f"{outcome_quote} + {cash}{outcome_amount}")
            #add the money to the users money
            await db_manager.add_money(msg.author.id, outcome_amount)
        #if the outcome type is money_loss
        elif outcome_type == "money_loss":
            #send a message saying the outcome, and the money lost
            await ctx.send(f"{outcome_quote} - {cash}{outcome_amount}")
            #remove the money from the users money
            await db_manager.remove_money(msg.author.id, outcome_amount)
        #if the outcome type is battle
        elif outcome_type == "spawn":
            #send a message saying the outcome
            await ctx.send(f"{outcome_quote}")
            #start a battle
            outcome_name = await db_manager.get_enemy_name(outcome_thing)
            await battle.spawn_monster(ctx, outcome_thing)
            
    #craft command
    @commands.hybrid_command()
    async def craft(self, ctx: Context, item: str):
        """Craft an item"""
        #get the users inventory
        inventory = await db_manager.view_inventory(ctx.author.id)
        #if the user has no items
        if inventory == None or [] or [ ]:
            #send a message saying the user has no items
            await ctx.send("You have no items in your Inventory!")
            return
        #get the item info
        item_info = await db_manager.view_basic_item(item)
        print(item_info)
        #if the item is not found
        if item_info == None or [] or [ ]:
            #send a message saying the item is not found
            await ctx.send("Item not found!")
            return
        #if the item is found
        else:
            #get the item name
            item_name = item_info[0][1]
            #get the item emote
            item_emote = item_info[0][3]
            #get the item recipe
            item_recipe = await db_manager.get_item_recipe(item)
            hasRecipe = await db_manager.check_item_recipe(item)
            if hasRecipe == False:
                await ctx.send(f"You can not craft {item_emote} **{item_name}**!")
                return
            for item in item_recipe:
            #check if the user has the items needed to craft the item
                if item in inventory:
                    #if the user has the items, remove the items from the users inventory
                    await db_manager.remove_item_from_inventory(ctx.author.id, item_recipe[0], item_recipe[1])
                    #add the item to the users inventory
                else:
                    #if the user does not have the items, send a message saying they do not have the items
                    await ctx.send(f"You do not have the items needed to craft {item_emote} **{item_name}**!")
                    #give the user the items back
                    return
            await db_manager.add_item_to_inventory(ctx.author.id, item, 1)
            
            
#attack command
    @commands.hybrid_command()
    async def attack(self, ctx: Context, enemy: str):
        """Attack an enemy"""
        userID = ctx.author.id
        userName = ctx.author.name
        monsterID = enemy
        monsterName = await db_manager.get_enemy_name(enemy)
        #check if the monster is spawned
        monsterSpawned = await db_manager.check_current_spawn(monsterID, ctx.guild.id)
        #if the monster is spawned
        #if monsterSpawned == 1:
            #start the battle
        monsterHealth = await db_manager.get_enemy_health(monsterID)
        await battle.attack(ctx, userID, userName, monsterID, monsterName)
        #if the monster is not spawned
        #else:
        #    #send a message saying the monster is not spawned
        #    await ctx.send(f"{monsterName} is not spawned, wait for the current Monster to be defeated!")
        #    return
        


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Basic(bot))