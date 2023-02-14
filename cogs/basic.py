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

from helpers import battle, checks, db_manager, randomEncounter, start, use


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
    @commands.hybrid_command(
        name="inventory",
        description="This command will view your inventory.",
    )
    async def inventory(self, ctx: Context):
        user_id = ctx.message.author.id
        inventory = await db_manager.view_inventory(user_id)
        #create a list of all the items in the inventory
        allWeapons = []
        allProjectiles = []
        allTools = []
        allArmor = []
        allConsumables = []
        allMaterials = []
        allMisc = []
        
        #define the lists whetre the embeds will be stored
        weapons = []
        armor = []
        consumables = []
        materials = []
        misc = []
        
        #sort the inventory by item type
        for i in inventory:
            print(i)
            item_type = i[7]
            item_type = str(item_type)
            if item_type == "Weapon":
                allWeapons.append(i)
            elif item_type == "Projectile":
                allProjectiles.append(i)
            elif item_type == "Tool":
                allTools.append(i)
            elif item_type == "Armor":
                allArmor.append(i)
            elif item_type == "Consumable":
                allConsumables.append(i)
            elif item_type == "Material":
                allMaterials.append(i)
            elif item_type == "Misc":
                allMisc.append(i)
        #for each item in each type of item, create an embed of the item and add it to a list named the item type
        #weapons
        #combine allProjectiles and allWeapon 
        allWeapons = allWeapons + allProjectiles + allTools
        for i in allWeapons:
            item_id = i[1]
            item_name = i[2]
            item_price = i[3]
            item_emote = i[4]
            item_rarity = i[5]
            item_type = i[7]
            item_type = str(item_type)
            item_damage = i[8]
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            if item_effect == "None":
                item_effect = "No Effect"
            item_amount = await db_manager.get_item_amount_from_inventory(user_id, item_id)
            item_info = await db_manager.get_basic_item_description(item_id)
            #check if the item is equipped
            item_equipped = await db_manager.check_item_equipped(user_id, item_id)
            item_info = str(item_info)
            rarity = str(item_rarity)
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
            
            #create an embed for this item
            if item_equipped == 1:
                item_amount = item_amount - 1
                if item_amount == 0:
                    item_amount = " Equipped"
                item = discord.Embed(
                    title=f"{item_name}{item_emote} x{item_amount}",
                    description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                    color=rarity_color
                )
                item.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.avatar.url)
            else:
                item = discord.Embed(
                    title=f"{item_name}{item_emote} x{item_amount}",
                    description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                    color=rarity_color
                )
                item.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.avatar.url)

            #add the embed to the list
            weapons.append(item)
        #armor
        for i in allArmor:
            item_id = i[1]
            item_name = i[2]
            item_price = i[3]
            item_emote = i[4]
            item_rarity = i[5]
            item_type = i[7]
            item_type = str(item_type)
            item_damage = i[8]
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            if item_effect == "None":
                item_effect = "No Effect"
            item_amount = await db_manager.get_item_amount_from_inventory(user_id, item_id)
            item_info = await db_manager.get_basic_item_description(item_id)
            item_equipped = await db_manager.check_item_equipped(user_id, item_id)
            item_info = str(item_info)
            rarity = str(item_rarity)
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
            #create an embed for this item
            if item_equipped == 1:
                item_amount = item_amount - 1
                if item_amount == 0:
                    item_amount = " Equipped"
                item = discord.Embed(
                    title=f"{item_name}{item_emote} x{item_amount}",
                    description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                    color=rarity_color
                )
                item.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.avatar.url)
            else:
                item = discord.Embed(
                    title=f"{item_name}{item_emote} x{item_amount}",
                    description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                    color=rarity_color
                )
                item.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.avatar.url)

            #add the embed to the list
            armor.append(item)
        #consumables
        for i in allConsumables:
            item_id = i[1]
            item_name = i[2]
            item_price = i[3]
            item_emote = i[4]
            item_rarity = i[5]
            item_type = i[7]
            item_type = str(item_type)
            item_damage = i[8]
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            if item_effect == "None":
                item_effect = "No Effect"
            item_amount = await db_manager.get_item_amount_from_inventory(user_id, item_id)
            item_info = await db_manager.get_basic_item_description(item_id)
            item_equipped = await db_manager.check_item_equipped(user_id, item_id)
            item_info = str(item_info)
            rarity = str(item_rarity)
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
            #create an embed for this item
            if item_equipped == 1:
                item_amount = item_amount - 1
                if item_amount == 0:
                    item_amount = " Equipped"
                item = discord.Embed(
                    title=f"{item_name}{item_emote} x{item_amount}",
                    description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                    color=rarity_color
                )
                item.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.avatar.url)
            else:
                item = discord.Embed(
                    title=f"{item_name}{item_emote} x{item_amount}",
                    description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                    color=rarity_color
                )
                item.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.avatar.url)

            #add the embed to the list
            consumables.append(item)
        #misc
        allMisc = allMisc + allMaterials
        for i in allMisc:
            item_id = i[1]
            item_name = i[2]
            item_price = i[3]
            item_emote = i[4]
            item_rarity = i[5]
            item_type = i[7]
            item_type = str(item_type)
            item_damage = i[8]
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            if item_effect == "None":
                item_effect = "No Effect"
            item_amount = await db_manager.get_item_amount_from_inventory(user_id, item_id)
            item_info = await db_manager.get_basic_item_description(item_id)
            item_info = str(item_info)
            rarity = str(item_rarity)
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
            #create an embed for this item
            item_equipped = await db_manager.check_item_equipped(user_id, item_id)
            if item_equipped == 1:
                item_amount = item_amount - 1
                if item_amount == 0:
                    item_amount = " Equipped"
                item = discord.Embed(
                    title=f"{item_name}{item_emote} x{item_amount}",
                    description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                    color=rarity_color
                )
                item.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.avatar.url)
            else:
                item = discord.Embed(
                    title=f"{item_name}{item_emote} x{item_amount}",
                    description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                    color=rarity_color
                )
                item.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.avatar.url)
            #add the embed to the list
            misc.append(item)
            
        #create a shop embed to send in the beginning
        invembed = discord.Embed(
            title=f"{ctx.author.name}'s Inventory",
            description="This is your Inventory, its Organized just like the shop",
            color=discord.Color.blurple()
        )
        invembed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        #react to the shop embed with, sword, shield, potion, and house
        message = await ctx.send(embed=invembed)
        await message.add_reaction("🗡")
        await message.add_reaction("<:ironarmor:1061292989047132190>")
        await message.add_reaction("🧪")
        await message.add_reaction("<:diamond:1061287200756596806>")
        await message.add_reaction("🏠")
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        await message.add_reaction("✅")
        await message.add_reaction("❌")

      
        #switch between the different embeds based on the reaction
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["🗡", "<:ironarmor:1061292989047132190>", "🧪", "<:diamond:1061287200756596806>", "🏠", "⬅️", "➡️", "✅", "❌"]
        page = 0
        i = 0
        reaction = None
        while True:
            if str(reaction) == "🗡":
                await message.remove_reaction("🗡", ctx.author)
                try: 
                    page = 1
                    await message.edit(embed=weapons[i])
                except(IndexError):
                    await ctx.send("There are no weapons in your inventory")
            elif str(reaction) == "<:ironarmor:1061292989047132190>":
                await message.remove_reaction("<:ironarmor:1061292989047132190>", ctx.author)
                try:
                    page = 2
                    await message.edit(embed=armor[i])
                except(IndexError):
                    await ctx.send("There is no armor in your inventory")
            elif str(reaction) == "🧪":
                await message.remove_reaction("🧪", ctx.author)
                try:
                    page = 3
                    await message.edit(embed=consumables[i])
                except(IndexError):
                    await ctx.send("There are no consumables in your inventory")
            elif str(reaction) == "<:diamond:1061287200756596806>":
                await message.remove_reaction("<:diamond:1061287200756596806>", ctx.author)
                try:
                    page = 4
                    await message.edit(embed=misc[i])
                except(IndexError):
                    await ctx.send("There are no misc items in your inventory")
            elif str(reaction) == "🏠":
                page = 0
                await message.edit(embed=invembed)
                await message.remove_reaction("🏠", ctx.author)
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
                #if the page is 1 (weapons) and the reaction is the arrow forward, go to the item in the list of weapons
                if page == 1 and str(reaction) == "➡️":
                    if i < len(weapons)-1:
                        i += 1
                        await message.edit(embed=weapons[i])
                        await message.remove_reaction("➡️", ctx.author)
                    else:
                        i = 0
                        await message.edit(embed=weapons[i])
                        await message.remove_reaction("➡️", ctx.author)
                #if the page is 1 (weapons) and the reaction is the arrow backward, go to the previous item in the list of weapons
                elif page == 1 and str(reaction) == "⬅️":
                    if i > 0:
                        i -= 1
                        await message.edit(embed=weapons[i])
                        await message.remove_reaction("⬅️", ctx.author)
                    else:
                        i = len(weapons)-1
                        await message.edit(embed=weapons[i])
                        await message.remove_reaction("⬅️", ctx.author)
        
                #if the page is 2 (armor) and the reaction is the arrow forward, go to the item in the list of armor
                elif page == 2 and str(reaction) == "➡️":
                    if i < len(armor)-1:
                        i += 1
                        await message.edit(embed=armor[i])
                        await message.remove_reaction("➡️", ctx.author)
                    else:
                        i = 0
                        await message.edit(embed=armor[i])
                        await message.remove_reaction("➡️", ctx.author)
                #if the page is 2 (armor) and the reaction is the arrow backward, go to the previous item in the list of armor
                elif page == 2 and str(reaction) == "⬅️":
                    if i > 0:
                        i -= 1
                        await message.edit(embed=armor[i])
                        await message.remove_reaction("⬅️", ctx.author)
                    else:
                        i = len(armor)-1
                        await message.edit(embed=armor[i])
                        await message.remove_reaction("⬅️", ctx.author)   
                        
                #if the page is 3 (consumables) and the reaction is the arrow forward, go to the item in the list of consumables
                elif page == 3 and str(reaction) == "➡️":
                    if i < len(consumables)-1:
                        i += 1
                        await message.edit(embed=consumables[i])
                        await message.remove_reaction("➡️", ctx.author)
                    else:
                        i = 0
                        await message.edit(embed=consumables[i])
                        await message.remove_reaction("➡️", ctx.author)
                #if the page is 3 (consumables) and the reaction is the arrow backward, go to the previous item in the list of consumables
                elif page == 3 and str(reaction) == "⬅️":
                    if i > 0:
                        i -= 1
                        await message.edit(embed=consumables[i])
                        await message.remove_reaction("⬅️", ctx.author)
                    else:
                        i = len(consumables)-1
                        await message.edit(embed=consumables[i])
                        await message.remove_reaction("⬅️", ctx.author)                        

                #if the page is 4 (misc) and the reaction is the arrow forward, go to the item in the list of misc
                elif page == 4 and str(reaction) == "➡️":
                    if i < len(misc)-1:
                        i += 1
                        await message.edit(embed=misc[i])
                        await message.remove_reaction("➡️", ctx.author)
                    else:
                        i = 0
                        await message.edit(embed=misc[i])
                        await message.remove_reaction("➡️", ctx.author)
                #if the page is 4 (misc) and the reaction is the arrow backward, go to the previous item in the list of misc
                elif page == 4 and str(reaction) == "⬅️":
                    if i > 0:
                        i -= 1
                        await message.edit(embed=misc[i])
                        await message.remove_reaction("⬅️", ctx.author)
                    else:
                        i = len(misc)-1
                        await message.edit(embed=misc[i])
                        await message.remove_reaction("⬅️", ctx.author)
                #if the reaction is the check mark, buy the item
                #EQUIP PROCESSING
                elif str(reaction) == "✅":
                    #remove the reaction
                    await message.remove_reaction("✅", ctx.author)
                    #if the page is 1 (weapons), check if the user already has the weapon, if not, add it to their inventory, otherwise tell them they already have it
                    if page == 1:
                        user_items = await db_manager.view_inventory(ctx.author.id)
                        print(user_items)
                        #get shop items 
                        user_weapons = allWeapons
                        print(user_weapons[i])
                        user_item_type = user_weapons[i][5]
                        print(user_item_type)
                        #check if the users inventory is empty
                        #sort the users inventory by weapon
                        user_item_id = user_weapons[i][1]
                        user_item_name = user_weapons[i][2]
                        user_item_price = user_weapons[i][3]
                        user_item_price = int(user_item_price)
                        user_item_emoji = user_weapons[i][4]
                        user_item_rarity = user_weapons[i][5]
                        user_item_type = user_weapons[i][7]
                        user_item_damage = user_weapons[i][8]
                        user_item_element = await db_manager.get_basic_item_element(user_item_id)
                        user_item_crit_chance = await db_manager.get_basic_item_crit_chance(user_item_id)
                        user_item_projectile = await db_manager.get_basic_item_projectile(user_item_id)
                        #get all the rwquirmenst for the add_item_to_inventory command
                        #check if                         #get the item name from the weapon list
                        print(user_item_id)
                        #check if the user can afford to buy the item
                        user_cash = await db_manager.get_money(ctx.author.id)
                        #convert it to a int
                        user_cash = int(user_cash[0])
                        #check if the item is equippable
                        isEquippable = await db_manager.check_item_equipped(user_id, user_item_id)
                        item_equipped_id = await db_manager.id_of_item_equipped(user_id, user_item_id)
                        #check if the item is a weapon or armor, and see if the user already has it
                        if item_equipped_id == user_item_id:
                            await ctx.send(f"`{item_name}` is already equipped.")
                            return
                        if item_type == "Weapon":
                            weapon_equipped = await db_manager.is_weapon_equipped(user_id)
                            if weapon_equipped == True:
                                await ctx.send(f"You already have a weapon equipped.")
                                return
                        elif item_type == "Armor":
                            armor_equipped = await db_manager.is_armor_equipped(user_id)
                            if armor_equipped == True:
                                await ctx.send(f"You already have armor equipped.")
                                return
                        isEquippable = await db_manager.is_basic_item_equipable(user_item_id)
                        if isEquippable == 1:
                            await db_manager.equip_item(user_id, item_id)
                            #get the item effect
                            item_effect = await db_manager.get_basic_item_effect(user_item_id)
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
                                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` health.")
                                #if the effect is minus
                                elif effect_add_or_minus == "-":
                                    #remove the effect amount from the user's health
                                    await db_manager.remove_health_boost(user_id, effect_amount)
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

                            #if the item has no effect
                            else:
                                await ctx.send(f"You equipped `{item_name}`")
                        else:
                            await ctx.send(f"that is not equippable.")
                        #if its not a weapon or armor, tell the user that they equiped it
                    #if the page is 2 (armor), check if the user already has the armor, if not, add it to their inventory, otherwise tell them they already have it
                    elif page == 2:
                        user_items = await db_manager.view_inventory(ctx.author.id)
                        print(user_items)
                        #get shop items 
                        user_armor = allArmor
                        print(user_armor[i])
                        user_item_type = user_armor[i][7]
                        print(user_item_type)
                        #check if the users inventory is empty
                        #sort the users inventory by weapon
                        user_item_id = user_armor[i][1]
                        user_item_name = user_armor[i][2]
                        user_item_price = user_armor[i][3]
                        user_item_price = int(user_item_price)
                        user_item_emoji = user_armor[i][4]
                        user_item_rarity = user_armor[i][5]
                        user_item_type = user_armor[i][7]
                        user_item_damage = user_armor[i][8]
                        user_item_element = await db_manager.get_basic_item_element(user_item_id)
                        user_item_crit_chance = await db_manager.get_basic_item_crit_chance(user_item_id)
                        user_item_projectile = await db_manager.get_basic_item_projectile(user_item_id)
                        #get all the rwquirmenst for the add_item_to_inventory command
                        #check if                         #get the item name from the weapon list
                        print(user_item_id)
                        #check if the user can afford to buy the item
                        user_cash = await db_manager.get_money(ctx.author.id)
                        #convert it to a int
                        user_cash = int(user_cash[0])
                        #check if the item is equippable
                        isEquippable = await db_manager.check_item_equipped(user_id, user_item_id)
                        item_equipped_id = await db_manager.id_of_item_equipped(user_id, user_item_id)
                        #check if the item is a weapon or armor, and see if the user already has it
                        if item_equipped_id == user_item_id:
                            await ctx.send(f"`{item_name}` is already equipped.")
                            return
                        if item_type == "Weapon":
                            weapon_equipped = await db_manager.is_weapon_equipped(user_id)
                            if weapon_equipped == True:
                                await ctx.send(f"You already have a weapon equipped.")
                                return
                        elif item_type == "Armor":
                            armor_equipped = await db_manager.is_armor_equipped(user_id)
                            if armor_equipped == True:
                                await ctx.send(f"You already have armor equipped.")
                                return
                        isEquippable = await db_manager.is_basic_item_equipable(user_item_id)
                        if isEquippable == 1:
                            await db_manager.equip_item(user_id, user_item_id)
                            #get the item effect
                            item_effect = await db_manager.get_basic_item_effect(user_item_id)
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
                                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` health.")
                                #if the effect is minus
                                elif effect_add_or_minus == "-":
                                    #remove the effect amount from the user's health
                                    await db_manager.remove_health_boost(user_id, effect_amount)
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

                            #if the item has no effect
                            else:
                                await ctx.send(f"You equipped `{item_name}`")
                        else:
                            await ctx.send(f"that is not equippable.")
                     #page 3
                    elif page == 3:
                        #consumables
                        user_items = await db_manager.view_inventory(ctx.author.id)
                        print(user_items)
                        #get shop items 
                        user_consumables = allConsumables
                        print(user_consumables[i])
                        user_item_type = user_consumables[i][7]
                        print(user_item_type)
                        #check if the users inventory is empty
                        #sort the users inventory by weapon
                        user_item_id = user_consumables[i][1]
                        user_item_name = user_consumables[i][2]
                        user_item_price = user_consumables[i][3]
                        user_item_price = int(user_item_price)
                        user_item_emoji = user_consumables[i][4]
                        user_item_rarity = user_consumables[i][5]
                        user_item_type = user_consumables[i][7]
                        user_item_damage = user_consumables[i][8]
                        user_item_element = await db_manager.get_basic_item_element(user_item_id)
                        user_item_crit_chance = await db_manager.get_basic_item_crit_chance(user_item_id)
                        user_item_projectile = await db_manager.get_basic_item_projectile(user_item_id)
                        #get all the rwquirmenst for the add_item_to_inventory command
                        #check if                         #get the item name from the weapon list
                        print(user_item_id)
                        #check if the user can afford to buy the item
                        user_cash = await db_manager.get_money(ctx.author.id)
                        #convert it to a int
                        user_cash = int(user_cash[0])
                        #check if the item is equippable
                        isEquippable = await db_manager.check_item_equipped(user_id, user_item_id)
                        item_equipped_id = await db_manager.id_of_item_equipped(user_id, user_item_id)
                        #check if the item is a weapon or armor, and see if the user already has it
                        if item_equipped_id == user_item_id:
                            await ctx.send(f"`{item_name}` is already equipped.")
                            return
                        if item_type == "Weapon":
                            weapon_equipped = await db_manager.is_weapon_equipped(user_id)
                            if weapon_equipped == True:
                                await ctx.send(f"You already have a weapon equipped.")
                                return
                        elif item_type == "Armor":
                            armor_equipped = await db_manager.is_armor_equipped(user_id)
                            if armor_equipped == True:
                                await ctx.send(f"You already have armor equipped.")
                                return
                        isEquippable = await db_manager.is_basic_item_equipable(user_item_id)
                        if isEquippable == 1:
                            await db_manager.equip_item(user_id, user_item_id)
                            #get the item effect
                            item_effect = await db_manager.get_basic_item_effect(user_item_id)
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
                                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` health.")
                                #if the effect is minus
                                elif effect_add_or_minus == "-":
                                    #remove the effect amount from the user's health
                                    await db_manager.remove_health_boost(user_id, effect_amount)
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

                            #if the item has no effect
                            else:
                                await ctx.send(f"You equipped `{item_name}`")
                        else:
                            await ctx.send(f"that is not equippable.")
                    
                    elif page == 4:
                        #misc
                        user_items = await db_manager.view_inventory(ctx.author.id)
                        print(user_items)
                        #get shop items 
                        user_misc = allMisc
                        print(user_misc[i])
                        user_item_type = user_misc[i][7]
                        print(user_item_type)
                        #check if the users inventory is empty
                        #sort the users inventory by weapon
                        user_item_id = user_misc[i][1]
                        user_item_name = user_misc[i][2]
                        user_item_price = user_misc[i][3]
                        user_item_price = int(user_item_price)
                        user_item_emoji = user_misc[i][4]
                        user_item_rarity = user_misc[i][5]
                        user_item_type = user_misc[i][7]
                        user_item_damage = user_misc[i][8]
                        user_item_element = await db_manager.get_basic_item_element(user_item_id)
                        user_item_crit_chance = await db_manager.get_basic_item_crit_chance(user_item_id)
                        user_item_projectile = await db_manager.get_basic_item_projectile(user_item_id)
                        #get all the rwquirmenst for the add_item_to_inventory command
                        #check if                         #get the item name from the weapon list
                        print(user_item_id)
                        #check if the user can afford to buy the item
                        user_cash = await db_manager.get_money(ctx.author.id)
                        #convert it to a int
                        user_cash = int(user_cash[0])
                        #check if the item is equippable
                        isEquippable = await db_manager.check_item_equipped(user_id, user_item_id)
                        item_equipped_id = await db_manager.id_of_item_equipped(user_id, item_id)
                        #check if the item is a weapon or armor, and see if the user already has it
                        if item_equipped_id == item_id:
                            await ctx.send(f"`{item_name}` is already equipped.")
                            return
                        if item_type == "Weapon":
                            weapon_equipped = await db_manager.is_weapon_equipped(user_id)
                            if weapon_equipped == True:
                                await ctx.send(f"You already have a weapon equipped.")
                                return
                        elif item_type == "Armor":
                            armor_equipped = await db_manager.is_armor_equipped(user_id)
                            if armor_equipped == True:
                                await ctx.send(f"You already have armor equipped.")
                                return
                        isEquippable = await db_manager.check_item_equipped(user_id, user_item_id)
                        item_equipped_id = await db_manager.id_of_item_equipped(user_id, user_item_id)
                        #check if the item is a weapon or armor, and see if the user already has it
                        if item_equipped_id == user_item_id:
                            await ctx.send(f"`{item_name}` is already equipped.")
                            return
                        if item_type == "Weapon":
                            weapon_equipped = await db_manager.is_weapon_equipped(user_id)
                            if weapon_equipped == True:
                                await ctx.send(f"You already have a weapon equipped.")
                                return
                        elif item_type == "Armor":
                            armor_equipped = await db_manager.is_armor_equipped(user_id)
                            if armor_equipped == True:
                                await ctx.send(f"You already have armor equipped.")
                                return
                        isEquippable = await db_manager.is_basic_item_equipable(user_item_id)
                        if isEquippable == 1:
                            await db_manager.equip_item(user_id, user_item_id)
                            #get the item effect
                            item_effect = await db_manager.get_basic_item_effect(user_item_id)
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
                                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` health.")
                                #if the effect is minus
                                elif effect_add_or_minus == "-":
                                    #remove the effect amount from the user's health
                                    await db_manager.remove_health_boost(user_id, effect_amount)
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

                            #if the item has no effect
                            else:
                                await ctx.send(f"You equipped `{item_name}`")
                        else:
                            await ctx.send(f"that is not equippable.")
                elif str(reaction) == "❌":
                    #delete the embed
                    await message.delete()
                    return  
            
            except Exception as e:
                print(e)
        

    #command to create a new item in the database item table, using the create_streamer_item function from helpers\db_manager.py
    @commands.hybrid_command(
        name="createitem",
        description="This command will create a new item in the database.",
    )
    @checks.is_streamer()
    async def create_item(self, ctx: Context, item_name: str, item_emote: discord.Emoji or discord.PartialEmoji):
        """
        This command will create a new item in the database.

        :param ctx: The context in which the command was called.
        :param item_name: The name of the item that should be added.
        :param item_price: The price of the item that should be added.
        """
        user_id = ctx.message.author.id
        #check if the item already exists in the database
        #grab the streamersID from the database
        streamerPrefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        streamerChannel = await db_manager.get_streamerChannel(user_id)
        twitchID = await db_manager.get_twitchID(user_id)
        twitchID = int(twitchID)
        items = await db_manager.view_streamer_items(streamerChannel)
        item_emote_url = item_emote.url
        emojiString = f'<:{item_emote.name}:{item_emote.id}>'
        print(items)
        for i in items:
            if item_name in i:
                await ctx.send(f"`{item_name}`already exists in the database.")
                return
        critChances = ['1%','2%', '3%', '4%', '5%', '6%', '7%', '8%', '9%', '10%', '11%', '12%', '13%', '14%', '15%', '16%', '17%', '18%', '19%', '20%', '21%', '22%', '23%', '24%', '25%']
        #get the presets from the json file
        with open('assets/streamer_item_presets.json') as f:
            presets = json.load(f)
        #pick a random preset
        preset = random.choice(presets)
        item_price = preset['item_price']
        item_rarity = preset['item_rarity']
        item_type = preset['item_type']
        item_damage = preset['item_damage']
        item_element = preset['item_element']
        item_crit_chance = preset['item_crit_chance']
        item_effect = preset['item_effect']
        isUsable = preset['isUsable']
        isEquippable = preset['isEquippable']

        if item_rarity == "Common":
            rarity_color="0x808080"
            rarity_color = int(rarity_color, 16)
            
        elif item_rarity == "Uncommon":
            rarity_color="0x00B300"
            rarity_color = int(rarity_color, 16)
            
        elif item_rarity == "Rare":
            rarity_color="0x0057C4"
            rarity_color = int(rarity_color, 16)
            
        elif item_rarity == "Epic":
            rarity_color="0xa335ee"
            rarity_color = int(rarity_color, 16)
            
        elif item_rarity == "Legendary":
            rarity_color="0xff8000"
            rarity_color = int(rarity_color, 16)

        #add the item to the database
        #send an embed to the streamer with the item info
        #global embed
        if item_type == "Weapon":
            embed = discord.Embed(title=f"Item Created", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}\nItem Damage: {item_damage}", color=rarity_color)
        elif item_type == "Armor":
            embed = discord.Embed(title=f"Item Created", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}\nItem Defence: {item_damage}", color=rarity_color)
        elif item_type == "Consumable":
            embed = discord.Embed(title=f"Item Created", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}\nItem Effect: {item_effect}", color=rarity_color)
        elif item_type == "Misc":
            embed = discord.Embed(title=f"Item Created", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}", color=rarity_color)

        #make the embed a global variable

        #make the embed author the streamer
        embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar.url)
        #set the embed thumbnail to the emoji url
        embed.set_thumbnail(url=item_emote_url)
        #create a button to confirm the item creation
        class Buttons(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.value = None

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button ):
                await interaction.response.send_message("Item created.")
                await interaction.message.delete()
                await db_manager.create_streamer_item(streamerPrefix, item_name, item_price, item_rarity, emojiString, twitchID, item_type, item_damage, item_element, item_crit_chance, item_effect, isUsable, isEquippable)
                
                self.value = True
                self.stop()

            #reroll button
            @discord.ui.button(label="Reroll", style=discord.ButtonStyle.grey)
            async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
                #reroll the item
                #pick a random preset
                preset = random.choice(presets)
                item_price = preset['item_price']
                item_rarity = preset['item_rarity']
                item_rarity = str(item_rarity)
                if item_rarity == "Common":
                    rarity_color="0x808080"
                    rarity_color = int(rarity_color, 16)

                elif item_rarity == "Uncommon":
                    rarity_color="0x00B300"
                    rarity_color = int(rarity_color, 16)

                elif item_rarity == "Rare":
                    rarity_color="0x0057C4"
                    rarity_color = int(rarity_color, 16)

                elif item_rarity == "Epic":
                    rarity_color="0xa335ee"
                    rarity_color = int(rarity_color, 16)

                elif item_rarity == "Legendary":
                    rarity_color="0xff8000"
                    rarity_color = int(rarity_color, 16)
                item_type = preset['item_type']
                item_damage = preset['item_damage']
                #send an embed to the streamer with the item info
                embed = discord.Embed(title=f"Item Preset", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}\nItem Damage: {item_damage}", color=rarity_color)
                #set the embed thumbnail to the emoji url
                embed.set_thumbnail(url=item_emote_url)
                embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar.url)
                await interaction.response.edit_message(embed=embed, view=self)

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message("Item creation cancelled.")
                #delete the message
                await interaction.message.delete()
                self.value = False
                self.stop()


        view = Buttons()
        await ctx.send("Here is your Item", embed=embed, view=view)

        #await db_manager.create_streamer_item(streamerPrefix, item_name, item_rarity, emojiString, twitchID, item_type, item_damage)

    #command to remove an item from the database item table, using the remove_item function from helpers\db_manager.py, make sure only streamers can remove their own items
    @commands.hybrid_command(
        name="removeitem",
        description="This command will remove an item from the database.",
    )
    @checks.is_streamer()
    async def remove_item(self, ctx: Context, item_id: str):
        """
        This command will remove an item from the database.

        :param ctx: The context in which the command was called.
        :param item_id: The id of the item that should be removed.
        """
        user_id = ctx.message.author.id
        #check if the item exists in the database
        items = await db_manager.view_streamer_items(user_id)
        for i in items:
            if item_id in i:
                await db_manager.remove_item(item_id)
                await ctx.send(f"Removed item with the ID `{item_id}` from your items.")
                return
        await ctx.send(f"Item with the ID `{item_id}` does not exist in the database or you are not the streamer of this item.")


#command to view the items of a specific streamer by their ID, using the view_streamer_items function from helpers\db_manager.py
    @commands.hybrid_command(
        name="view_streamer_items",
        description="This command will view all items of a specific streamer.",
    )
    @checks.is_owner()
    #the user needs to input the streamers ID
    async def view_streamer_items(self, ctx: Context, streamer_channel: str):
        """
        This command will view all items of a specific streamer.

        :param ctx: The context in which the command was called.
        :param streamer_prefix: The ID of the streamer whose items should be viewed.
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
                items = await db_manager.view_streamer_items(streamer_channel)
                embed = discord.Embed(title="Items", description=f"All of `{streamer_channel_name}'s` Items.", color=0x00ff00)
                print(items)
                for i in items:
                    #remove the streamerPrefix from the name of the item
                    print(i)
                    item_id = i[1]
                    item_name = i[2]
                    item_price = i[3]
                    item_emote = i[4]
                    embed.add_field(name=f"`ID:{item_id}` {item_name}{item_emote}", value=f"Price: {item_price}", inline=True)
                await ctx.send(embed=embed)
                return
        await ctx.send(f"Streamer doesn't exist in the database.")

#shop command to view the shop using the display_shop function from helpers\db_manager.py
#    @commands.hybrid_command(
#        name="shop",
#        description="This command will display the shop.",
#    )
#    async def shop(self, ctx: Context):
#        """
#        This command will display the shop.
#
#        :param ctx: The context in which the command was called.
#        """
#        shop = await db_manager.display_shop_items()
#        embed = discord.Embed(title="Shop", description="All of the items in the shop.", color=0x00ff00)
#        weaponembed = discord.Embed(title="Weapons", description="All of the weapons in the shop.", color=0x00ff00)
#        armorembed = discord.Embed(title="Armor", description="All of the armor in the shop.", color=0x00ff00)
#        heals = discord.Embed(title="Heals", description="All of the healing items in the shop.", color=0x00ff00)
#        misc = discord.Embed(title="Misc", description="All of the misc items in the shop.", color=0x00ff00)
#        #create a separate embed for each item type
#        for i in shop:
#            item_id = i[0]
#            item_name = i[1]
#            item_price = i[2]
#            item_emote = i[3]
#            item_rarity = i[4]
#            item_type = i[5]
#            item_type = str(item_type)
#            item_damage = i[6]
#            #get the item effect
#            item_effect = await db_manager.get_basic_item_effect(item_id)
#            item_amount = await db_manager.get_shop_item_amount(item_id)
#            item_info = await db_manager.get_basic_item_description(item_id)
#            item_info = str(item_info)
#
#            #grab the int out of the coroutine=
#            if item_type == "Weapon" or item_type == "Projectile":
#                #for each item in the item 
#                #create an embed for this item type
#                weaponembed.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Rarity**: `{item_rarity}` ", inline=True)
#            if item_type == "Armor" or item_type == "Shield" or item_type == "Cosmetic":
#                #create an embed for this item type
#                armorembed.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Defence**: `{item_damage}` \n **Rarity**: `{item_rarity}` ", inline=True)
#            #if its a consumable, and the item effect has the word heal in it, then display the heal amount
#            #check if the word heal is in the item effect
#            if item_type == "Consumable" and ("heal" in item_effect or "revive" in item_effect):
#                #create an embed for this item type
#                heals.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Heal**: `{item_damage}` \n **Rarity**: `{item_rarity}` ", inline=True)
#            #if its a consumable, and the item effect has the word damage in it, then display the damage amount
#            else:
#                if item_damage == 0:
#                    #create an embed for this item type whitch is misc
#                    misc.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Rarity**: `{item_rarity}` ", inline=True)
#        #await ctx.send(embed=embed)
#
#        #create buttons to switch between the different embeds
#        #create a list of all the embeds
#        #make sure the emebds exist before adding them to the list
#        embeds = []
#        #add the embeds to the list
#        if weaponembed.fields:
#            embeds.append(weaponembed)
#        if armorembed.fields:
#            embeds.append(armorembed)
#        if heals.fields:
#            embeds.append(heals)
#        if misc.fields:
#            embeds.append(misc)
#
#
#        #send the first embed, and add reactions to it to switch between the different embeds
#        message = await ctx.send(embed=embeds[0])
#        await message.add_reaction("⬅️")
#        await message.add_reaction("➡️")
#
#
#
#
#
#
#        #create a function to check if the reaction is the one we want
#        def check(reaction, user):
#            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]
#        
#        #switch between the different embeds
#        i = 0
#        reaction = None
#        while True:
#            if str(reaction) == "⬅️":
#                if i > 0:
#                    i -= 1
#                    await message.edit(embed=embeds[i])
#            elif str(reaction) == "➡️":
#                if i < len(embeds)-1:
#                    i += 1
#                    await message.edit(embed=embeds[i])
#            try:
#                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
#                await message.remove_reaction(reaction, user)                
#            except asyncio.TimeoutError:
#                break

#STUB - shop command
    @commands.hybrid_command(
        name="shop",
        description="This command will show the shop.",
    )
    async def shop(self, ctx: Context):
        #get all the shop items
        shop = await db_manager.display_shop_items()
        allWeapons = await db_manager.get_all_shop_items_off_one_type("Weapon")
        weapons = []
        allArmor = await db_manager.get_all_shop_items_off_one_type("Armor")
        armor = []
        allConsumables = await db_manager.get_all_shop_items_off_one_type("Consumable")
        consumables = []
        allMisc = await db_manager.get_all_shop_items_off_one_type("Misc")
        misc = []
        allProjectiles = await db_manager.get_all_shop_items_off_one_type("Projectile")
        projectiles = []
        allShields = await db_manager.get_all_shop_items_off_one_type("Shield")
        shields = []
        allCosmetics = await db_manager.get_all_shop_items_off_one_type("Cosmetic")
        cosmetics = []
        allMaterals = await db_manager.get_all_shop_items_off_one_type("Material")
        materals = []
        allTools = await db_manager.get_all_shop_items_off_one_type("Tools")
        tools = []
        
        #for each item in each type of item, create an embed of the item and add it to a list named the item type
        #weapons
        #combine allProjectiles and allWeapon 
        allWeapons = allWeapons + allProjectiles + allTools
        for i in allWeapons:
            item_id = i[0]
            item_name = i[1]
            item_price = i[2]
            item_emote = i[3]
            item_rarity = i[4]
            item_type = i[5]
            item_type = str(item_type)
            item_damage = i[6]
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            item_amount = await db_manager.get_shop_item_amount(item_id)
            item_info = await db_manager.get_basic_item_description(item_id)
            item_info = str(item_info)
            rarity = str(item_rarity)
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
            #create an embed for this item
            item = discord.Embed(
                title=f"{item_name}{item_emote} x{item_amount}",
                description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                color=rarity_color
            )
            #add the embed to the list
            weapons.append(item)
        #armor
        for i in allArmor:
            item_id = i[0]
            item_name = i[1]
            item_price = i[2]
            item_emote = i[3]
            item_rarity = i[4]
            item_type = i[5]
            item_type = str(item_type)
            item_damage = i[6]
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            item_amount = await db_manager.get_shop_item_amount(item_id)
            item_info = await db_manager.get_basic_item_description(item_id)
            item_info = str(item_info)
            rarity = str(item_rarity)
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
            #create an embed for this item
            item = discord.Embed(
                title=f"{item_name}{item_emote} x{item_amount}",
                description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                color=rarity_color
            )
            #add the embed to the list
            armor.append(item)
        #consumables
        for i in allConsumables:
            item_id = i[0]
            item_name = i[1]
            item_price = i[2]
            item_emote = i[3]
            item_rarity = i[4]
            item_type = i[5]
            item_type = str(item_type)
            item_damage = i[6]
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            item_amount = await db_manager.get_shop_item_amount(item_id)
            item_info = await db_manager.get_basic_item_description(item_id)
            item_info = str(item_info)
            rarity = str(item_rarity)
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
            #create an embed for this item
            item = discord.Embed(
                title=f"{item_name}{item_emote} x{item_amount}",
                description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                color=rarity_color
            )
            #add the embed to the list
            consumables.append(item)
        #misc
        allMisc = allMisc + allMaterals
        for i in allMisc:
            item_id = i[0]
            item_name = i[1]
            item_price = i[2]
            item_emote = i[3]
            item_rarity = i[4]
            item_type = i[5]
            item_type = str(item_type)
            item_damage = i[6]
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
            item_amount = await db_manager.get_shop_item_amount(item_id)
            item_info = await db_manager.get_basic_item_description(item_id)
            item_info = str(item_info)
            rarity = str(item_rarity)
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
            #create an embed for this item
            item = discord.Embed(
                title=f"{item_name}{item_emote} x{item_amount}",
                description=f"`ID:{item_id}` \n **Info**: `{item_info}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Effect**: `{item_effect}` \n **Rarity**: `{item_rarity}` ",
                color=rarity_color
            )
            #add the embed to the list
            misc.append(item)
            
        #create a shop embed to send in the beginning
        shopembed = discord.Embed(
            title="Shop",
            description="Welcome to the shop! Here you can buy items to help you on your journey. \n The shop is in",
            color=discord.Color.blurple()
        )
        #react to the shop embed with, sword, shield, potion, and house
        message = await ctx.send(embed=shopembed)
        await message.add_reaction("⚔️")
        await message.add_reaction("🛡️")
        await message.add_reaction("🧪")
        await message.add_reaction("💎")
        await message.add_reaction("🏠")
        await message.add_reaction("⏪")
        await message.add_reaction("⏩")
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        
        #switch between the different embeds based on the reaction
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⚔️", "🛡️", "🧪", "💎", "🏠", "⏪", "⏩", "✅", "❌"]
        page = 0
        i = 0
        reaction = None
        while True:
            if str(reaction) == "⚔️":
                page = 1
                await message.edit(embed=weapons[i])
                await message.remove_reaction("⚔️", ctx.author)
            elif str(reaction) == "🛡️":
                page = 2
                await message.edit(embed=armor[i])
                await message.remove_reaction("🛡️", ctx.author)
            elif str(reaction) == "🧪":
                page = 3
                await message.edit(embed=consumables[i])
                await message.remove_reaction("🧪", ctx.author)
            elif str(reaction) == "💎":
                page = 4
                await message.edit(embed=misc[i])
                await message.remove_reaction("💎", ctx.author)
            elif str(reaction) == "🏠":
                page = 0
                await message.edit(embed=shopembed)
                await message.remove_reaction("🏠", ctx.author)
            try: 
                reaction, user = await self.bot.wait_for("reaction_add", timeout=200.0, check=check)
                #if the page is 1 (weapons) and the reaction is the arrow forward, go to the item in the list of weapons
                if page == 1 and str(reaction) == "⏩":
                    if i < len(weapons)-1:
                        i += 1
                        await message.edit(embed=weapons[i])
                        await message.remove_reaction("⏩", ctx.author)
                    else:
                        i = 0
                        await message.edit(embed=weapons[i])
                        await message.remove_reaction("⏩", ctx.author)
                #if the page is 1 (weapons) and the reaction is the arrow backward, go to the previous item in the list of weapons
                elif page == 1 and str(reaction) == "⏪":
                    if i > 0:
                        i -= 1
                        await message.edit(embed=weapons[i])
                        await message.remove_reaction("⏪", ctx.author)
                    else:
                        i = len(weapons)-1
                        await message.edit(embed=weapons[i])
                        await message.remove_reaction("⏪", ctx.author)
        
                #if the page is 2 (armor) and the reaction is the arrow forward, go to the item in the list of armor
                elif page == 2 and str(reaction) == "⏩":
                    if i < len(armor)-1:
                        i += 1
                        await message.edit(embed=armor[i])
                        await message.remove_reaction("⏩", ctx.author)
                    else:
                        i = 0
                        await message.edit(embed=armor[i])
                        await message.remove_reaction("⏩", ctx.author)
                #if the page is 2 (armor) and the reaction is the arrow backward, go to the previous item in the list of armor
                elif page == 2 and str(reaction) == "⏪":
                    if i > 0:
                        i -= 1
                        await message.edit(embed=armor[i])
                        await message.remove_reaction("⏪", ctx.author)
                    else:
                        i = len(armor)-1
                        await message.edit(embed=armor[i])
                        await message.remove_reaction("⏪", ctx.author)   
                        
                #if the page is 3 (consumables) and the reaction is the arrow forward, go to the item in the list of consumables
                elif page == 3 and str(reaction) == "⏩":
                    if i < len(consumables)-1:
                        i += 1
                        await message.edit(embed=consumables[i])
                        await message.remove_reaction("⏩", ctx.author)
                    else:
                        i = 0
                        await message.edit(embed=consumables[i])
                        await message.remove_reaction("⏩", ctx.author)
                #if the page is 3 (consumables) and the reaction is the arrow backward, go to the previous item in the list of consumables
                elif page == 3 and str(reaction) == "⏪":
                    if i > 0:
                        i -= 1
                        await message.edit(embed=consumables[i])
                        await message.remove_reaction("⏪", ctx.author)
                    else:
                        i = len(consumables)-1
                        await message.edit(embed=consumables[i])
                        await message.remove_reaction("⏪", ctx.author)                        

                #if the page is 4 (misc) and the reaction is the arrow forward, go to the item in the list of misc
                elif page == 4 and str(reaction) == "⏩":
                    if i < len(misc)-1:
                        i += 1
                        await message.edit(embed=misc[i])
                        await message.remove_reaction("⏩", ctx.author)
                    else:
                        i = 0
                        await message.edit(embed=misc[i])
                        await message.remove_reaction("⏩", ctx.author)
                #if the page is 4 (misc) and the reaction is the arrow backward, go to the previous item in the list of misc
                elif page == 4 and str(reaction) == "⏪":
                    if i > 0:
                        i -= 1
                        await message.edit(embed=misc[i])
                        await message.remove_reaction("⏪", ctx.author)
                    else:
                        i = len(misc)-1
                        await message.edit(embed=misc[i])
                        await message.remove_reaction("⏪", ctx.author)
                #if the reaction is the check mark, buy the item
                
                #BUY PROCESSING
                elif str(reaction) == "✅":
                    #remove the reaction
                    await message.remove_reaction("✅", ctx.author)
                    #if the page is 1 (weapons), check if the user already has the weapon, if not, add it to their inventory, otherwise tell them they already have it
                    if page == 1:
                         user_items = await db_manager.view_inventory(ctx.author.id)
                         print(user_items)
                         #get shop items 
                         shop_items = allWeapons
                         print(shop_items[i])
                         shop_item_type = shop_items[i][5]
                         print(shop_item_type)
                         #check if the users inventory is empty
                         if user_items == []:
                             user_weapons = []
                         else:
                             user_weapons = user_items[i][0]
                         #sort the users inventory by weapon
                         shop_item_id = shop_items[i][0]
                         shop_item_name = shop_items[i][1]
                         shop_item_price = shop_items[i][2]
                         shop_item_price = int(shop_item_price)
                         shop_item_emoji = shop_items[i][3]
                         shop_item_rarity = shop_items[i][4]
                         shop_item_type = shop_items[i][5]
                         shop_item_damage = shop_items[i][6]
                         shop_item_element = await db_manager.get_basic_item_element(shop_item_id)
                         shop_item_crit_chance = await db_manager.get_basic_item_crit_chance(shop_item_id)
                         shop_item_projectile = await db_manager.get_basic_item_projectile(shop_item_id)
                         #get all the rwquirmenst for the add_item_to_inventory command
                         #check if 

                         #get the item name from the weapon list
                         print(shop_item_id)
                         #check if the user can afford to buy the item
                         user_cash = await db_manager.get_money(ctx.author.id)
                         #convert it to a int
                         user_cash = int(user_cash[0])
                         #check if the item is a weapon or armor, and see if the user already has it
                         if shop_item_type == 'Weapon' or shop_item_type == 'Armor':
                             #check if the user already has this item
                             for item in user_items:
                                 if item[0] == shop_item_id:
                                     await ctx.send("You already have this item")
                                     return
                         #check if the user can afford this item
                         if user_cash < shop_item_price:
                             await ctx.send("You can't afford this item")
                             #send the user back to the homepage of the shop
                         else:
                             await db_manager.remove_money(ctx.author.id, shop_item_price)
                             await db_manager.add_item_to_inventory(ctx.author.id, shop_item_id, 1)
                             await ctx.send(f"You bought a {shop_item_name}!")

                    if page == 2:
                         user_items = await db_manager.view_inventory(ctx.author.id)
                         print(user_items)
                         shop_items = allArmor
                         print(shop_items[i])
                         shop_item_type = shop_items[i][5]
                         print(shop_item_type)
                         if user_items == []:
                             user_armor = []
                         else:
                             user_armor = user_items[i][0]
                         shop_item_id = shop_items[i][0]
                         shop_item_name = shop_items[i][1]
                         shop_item_price = shop_items[i][2]
                         shop_item_price = int(shop_item_price)
                         shop_item_emoji = shop_items[i][3]
                         shop_item_rarity = shop_items[i][4]
                         shop_item_type = shop_items[i][5]
                         shop_item_protection = shop_items[i][6]
                         shop_item_element = await db_manager.get_basic_item_element(shop_item_id)
                         shop_item_crit_chance = await db_manager.get_basic_item_crit_chance(shop_item_id)
                         shop_item_projectile = await db_manager.get_basic_item_projectile(shop_item_id)
                         print(shop_item_id)
                         user_cash = await db_manager.get_money(ctx.author.id)
                         user_cash = int(user_cash[0])
                         if shop_item_type == 'Weapon' or shop_item_type == 'Armor':
                             for item in user_items:
                                 if item[0] == shop_item_id:
                                     await ctx.send("You already have this item")
                                     return
                         if user_cash < shop_item_price:
                             await ctx.send("You can't afford this item")
                             #send the user back to the homepage of the shop
                         else:
                             await db_manager.remove_money(ctx.author.id, shop_item_price)
                             await db_manager.add_item_to_inventory(ctx.author.id, shop_item_id, 1)
                             await ctx.send(f"You bought a {shop_item_name}!")

                    if page == 3:
                         user_items = await db_manager.view_inventory(ctx.author.id)
                         print(user_items)
                         shop_items = allConsumables
                         print(shop_items[i])
                         shop_item_type = shop_items[i][5]
                         print(shop_item_type)
                         if user_items == []:
                             user_consumables = []
                         else:
                             user_consumables = user_items[i][0]
                         shop_item_id = shop_items[i][0]
                         shop_item_name = shop_items[i][1]
                         shop_item_price = shop_items[i][2]
                         shop_item_price = int(shop_item_price)
                         shop_item_emoji = shop_items[i][3]
                         shop_item_rarity = shop_items[i][4]
                         shop_item_type = shop_items[i][5]
                         shop_item_effect = shop_items[i][6]
                         shop_item_element = await db_manager.get_basic_item_element(shop_item_id)
                         shop_item_crit_chance = await db_manager.get_basic_item_crit_chance(shop_item_id)
                         shop_item_projectile = await db_manager.get_basic_item_projectile(shop_item_id)
                         print(shop_item_id)
                         user_cash = await db_manager.get_money(ctx.author.id)
                         user_cash = int(user_cash[0])
                         if shop_item_type == 'Weapon' or shop_item_type == 'Armor':
                             for item in user_items:
                                 if item[0] == shop_item_id:
                                     await ctx.send("You already have this item")
                                     return
                         if user_cash < shop_item_price:
                             await ctx.send("You can't afford this item")
                             #send the user back to the homepage of the shop
                         else:
                             await db_manager.remove_money(ctx.author.id, shop_item_price)
                             await db_manager.add_item_to_inventory(ctx.author.id, shop_item_id, 1)
                             await ctx.send(f"You bought a {shop_item_name}!")

                    if page == 4:
                         user_items = await db_manager.view_inventory(ctx.author.id)
                         print(user_items)
                         shop_items = allMisc
                         print(shop_items[i])
                         shop_item_type = shop_items[i][5]
                         print(shop_item_type)
                         if user_items == []:
                             user_misc = []
                         else:
                             user_misc = user_items[i][0]
                         shop_item_id = shop_items[i][0]
                         shop_item_name = shop_items[i][1]
                         shop_item_price = shop_items[i][2]
                         shop_item_price = int(shop_item_price)
                         shop_item_emoji = shop_items[i][3]
                         shop_item_rarity = shop_items[i][4]
                         shop_item_type = shop_items[i][5]
                         shop_item_description = shop_items[i][6]
                         shop_item_element = await db_manager.get_basic_item_element(shop_item_id)
                         shop_item_crit_chance = await db_manager.get_basic_item_crit_chance(shop_item_id)
                         shop_item_projectile = await db_manager.get_basic_item_projectile(shop_item_id)
                         print(shop_item_id)
                         user_cash = await db_manager.get_money(ctx.author.id)
                         user_cash = int(user_cash[0])
                         if shop_item_type == 'Weapon' or shop_item_type == 'Armor' or shop_item_type == 'Consumable':
                             for item in user_items:
                                 if item[0] == shop_item_id:
                                     await ctx.send("You already have this item")
                                     return
                         if user_cash < shop_item_price:
                             await ctx.send("You can't afford this item")
                             #send the user back to the homepage of the shop
                         else:
                             await db_manager.remove_money(ctx.author.id, shop_item_price)
                             await db_manager.add_item_to_inventory(ctx.author.id, shop_item_id, 1)
                             await ctx.send(f"You bought a {shop_item_name}!")
                elif str(reaction) == "❌":
                    #delete the embed
                    await message.delete()
                    return
            except Exception as e:
                print(e)
                    

    #command to see the quest board
    
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
            questembed.add_field(name=f"**{quest_name}**", value=f"`ID:{quest_id}` \n **Description**: `{quest_description}` \n **XP**: `{quest_xp}` \n **Reward**: `{quest_reward}` \n **Reward Amount**: `{quest_reward_amount}` \n **Level Requirement**: `{quest_level_req}` \n **Quest**: `{quest_type} {quest}` ", inline=False)
            
            #save the embed to a list
            embeds.append(questembed)
        
        #send the first embed, and add reactions to it to switch between the different embeds
        message = await ctx.send(embed=embeds[0])
        await message.add_reaction("⏪")
        await message.add_reaction("➡️")
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
        
            
     #buy command for buying items, multiple of the same item can be bought, and the user can buy multiple items at once, then removes them from the shop, and makes sure the user has enough bucks
    @commands.hybrid_command(
        name="buy",
        description="This command will buy an item from the shop.",
    )
    async def buy(self, ctx: Context, item_id: str, amount: int):
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
            if item_id in i:
                #check if the user has enough bucks
                item_price = i[2]
                item_price = int(item_price)
                total_price = item_price * amount
                if user_money >= total_price:
                    #if the item type is a weapon, check if the user has already has this weapon
                    item_type = await db_manager.get_basic_item_type(item_id)
                    if item_type == "Weapon":
                        #check if the user has this weapon
                        user_inventory = await db_manager.view_inventory(user_id)
                        for i in user_inventory:
                            if item_id in i:
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
                            if item_id in i:
                                await ctx.send(f"You already have this armor!")
                                return
                        #if the user is trying to buy more than 1 of the same weapon, tell them they can only buy 1
                        if amount > 1:
                            await ctx.send(f"You can only buy 1 of the same Armor!")
                            return
                    item_name = await db_manager.get_basic_item_name(item_id)
                    item_price = await db_manager.get_shop_item_price(item_id)
                    item_emoji = await db_manager.get_shop_item_emoji(item_id)
                    #Q, how to I get the string out of a coroutine?
                    #A, use await
                    item_rarity = await db_manager.get_basic_item_rarity(item_id)
                    item_type = await db_manager.get_basic_item_type(item_id)
                    item_damage = await db_manager.get_basic_item_damage(item_id)
                    item_name = await db_manager.get_basic_item_name(item_id)
                    item_element = await db_manager.get_basic_item_element(item_id)
                    item_crit_chance = await db_manager.get_basic_item_crit_chance(item_id)
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
                        item_type = await db_manager.get_basic_item_type(item_id)
                        if item_type == "Weapon":
                            #check if the user has this weapon
                            user_inventory = await db_manager.view_inventory(user_id)
                            for i in user_inventory:
                                if item_id in i:
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
                                if item_id in i:
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
                            await db_manager.remove_shop_item_amount(item_id, amount)
                            #add the item to the users inventory
                            await db_manager.add_item_to_inventory(user_id, item_id, amount)
                            #remove the price from the users money
                            await db_manager.remove_money(user_id, total_price)
                            await ctx.send(f"You bought `{amount}` of `{item_name}` for `{total_price}` bucks.")
                        return
                else:
                    item_name = await db_manager.get_basic_item_name(item_id)
                    await ctx.send(f"You don't have enough bucks to buy `{amount}` of `{item_name}`.")
                    return
        await ctx.send(f"Item doesn't exist in the shop.")
        
    #sell command for selling items, multiple of the same item can be sold, and the user can sell multiple items at once, then removes them from the users inventory, and adds the price to the users money
    @commands.hybrid_command(
        name="sell",
        description="This command will sell an item from your inventory.",
    )
    async def sell(self, ctx: Context, item_id: str, amount: int):
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
            if item_id in i:
                #check if the user has enough of the item
                item_amount = i[7]
                item_amount = int(item_amount)
                if item_amount >= amount:
                    item_price = i[3]
                    item_price = int(item_price)
                    total_price = item_price * amount
                    #remove the item from the users inventory
                    await db_manager.remove_item_from_inventory(user_id, item_id, amount)
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
            embed.add_field(name="Health", value=f"{user_health} / 100 (Dead)", inline=True)
        else:
            embed.add_field(name="Health", value=f"{user_health} / 100", inline=True)
        embed.add_field(name="Money", value=f"{user_money}", inline=True)
        #add xp and level
        embed.add_field(name = chr(173), value = chr(173))
        embed.add_field(name="XP", value=f"{user_xp} / {xp_needed}", inline=True)
        embed.add_field(name="Level", value=f"{user_level}", inline=True)
        for i in user_items:
            item_name = i[2]
            item_emote = i[4]
            item_amount = i[6]
            embed.add_field(name=f"{item_name}{item_emote}", value=f"{item_amount}", inline=False)
            
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
            await ctx.send("You have started your journey. Welcome to the world of **Dank Streamer**.")
        else:
            await ctx.send("You have already started your journey.")
    
        



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

    #a command to add money to a user using the add_money function from helpers\db_manager.py
    @commands.hybrid_command(
        name="addmoney",
        description="This command will add money to a user.",
    )
    @checks.is_owner()
    async def addmoney(self, ctx: Context, user: discord.Member, amount: int):
        """
        This command will add money to a user.

        :param ctx: The context in which the command was called.
        :param user: The user that should be given money.
        :param amount: The amount of money that should be given.
        """
        await db_manager.add_money(user.id, amount)
        await ctx.send(f"You gave {user.mention} `{amount}` bucks.")
        
    #a command to equip an item using the equip_item function from helpers\db_manager.py, check if the item has isEquippable set to true, if there are mutiple items of the same type, remove the old one and equip the new one, if there are mutliples of the same item, equip the first one, if the item is already equipped, say that it is already equipped, check that only one of the weapon and armor item type is equipped at a time
    @commands.hybrid_command(
        name="equip",
        description="This command will equip an item.",
    )
    async def equip(self, ctx: Context, item_id: str):
        """
        This command will equip an item.

        :param ctx: The context in which the command was called.
        :param item: The item that should be equipped.
        """
        user_id = ctx.message.author.id
        item_name = await db_manager.get_basic_item_name(item_id)
        item_type = await db_manager.get_basic_item_type(item_id)
        item_equipped_id = await db_manager.id_of_item_equipped(user_id, item_id)
        print(item_equipped_id)
        print(item_type)
        if item_equipped_id == item_id:
            await ctx.send(f"`{item_name}` is already equipped.")
            return
        if item_type == "Weapon":
            weapon_equipped = await db_manager.is_weapon_equipped(user_id)
            if weapon_equipped == True:
                await ctx.send(f"You already have a weapon equipped.")
                return
        elif item_type == "Armor":
            armor_equipped = await db_manager.is_armor_equipped(user_id)
            if armor_equipped == True:
                await ctx.send(f"You already have armor equipped.")
                return
        isEquippable = await db_manager.is_basic_item_equipable(item_id)
        if isEquippable == 1:
            await db_manager.equip_item(user_id, item_id)
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
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
                    await ctx.send(f"You equipped `{item_name}`. It gave you +`{effect_amount}` health.")
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's health
                    await db_manager.remove_health_boost(user_id, effect_amount)
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
                    
            #if the item has no effect
            else:
                await ctx.send(f"You equipped `{item_name}`")
        else:
            await ctx.send(f"that is not equippable.")
            
    #a command to unequip an item using the unequip_item function from helpers\db_manager.py, check if the item is equipped, if it is, unequip it, if it isn't, say that it isn't equipped
    @commands.hybrid_command(
        name="unequip",
        description="This command will unequip an item.",
    )
    async def unequip(self, ctx: Context, item_id: str):
        """
        This command will unequip an item.

        :param ctx: The context in which the command was called.
        :param item: The item that should be unequipped.
        """
        user_id = ctx.message.author.id
        item_name = await db_manager.get_basic_item_name(item_id)
        item_equipped_id = await db_manager.id_of_item_equipped(user_id, item_id)
        if item_equipped_id == item_id:
            #remove the item effect
            item_effect = await db_manager.get_basic_item_effect(item_id)
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
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's health
                    await db_manager.add_health_boost(user_id, effect_amount)
            #if the effect is damage
            elif effect == "damage":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's damage
                    await db_manager.remove_damage_boost(user_id, effect_amount)
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's damage
                    await db_manager.add_damage_boost(user_id, effect_amount)
            #if the effect is luck
            elif effect == "luck":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's luck
                    await db_manager.remove_luck(user_id, effect_amount)
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's luck
                    await db_manager.add_luck(user_id, effect_amount)
                    
            #if the effect is crit chance
            elif effect == "crit_chance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's crit chance
                    await db_manager.remove_crit_chance(user_id, effect_amount)
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's crit chance
                    await db_manager.add_crit_chance(user_id, effect_amount)
                
            #if the effect is fire resistance
            elif effect == "fire_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's fire resistance
                    await db_manager.remove_fire_resistance(user_id, effect_amount)
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's fire resistance
                    await db_manager.add_fire_resistance(user_id, effect_amount)
            
            #if the effect is poison resistance
            elif effect == "poison_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's poison resistance
                    await db_manager.remove_poison_resistance(user_id, effect_amount)
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's poison resistance
                    await db_manager.add_poison_resistance(user_id, effect_amount)
                    
            #if the effect is frost resistance
            elif effect == "frost_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's frost resistance
                    await db_manager.remove_frost_resistance(user_id, effect_amount)
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's frost resistance
                    await db_manager.add_frost_resistance(user_id, effect_amount)
                    
            #if the effect is paralysis resistance
            elif effect == "paralysis_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's paralysis resistance
                    await db_manager.remove_paralysis_resistance(user_id, effect_amount)
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's paralysis resistance
                    await db_manager.add_paralysis_resistance(user_id, effect_amount)
            await db_manager.unequip_item(user_id, item_id)
            await ctx.send(f"You unequipped `{item_name}`")
        else:
            await ctx.send(f"`{item_name}` is not equipped.")
            
    #a command to use an item using the use_item function from helpers\db_manager.py, check if the item is usable, if it is, use it, if it isn't, say that it isn't usable
    @commands.hybrid_command(
        name="use",
        description="This command will use an item.",
    )
    async def use(self, ctx: Context, item_id: str):
        """
        This command will use an item.

        :param ctx: The context in which the command was called.
        :param item: The item that should be used.
        """
        use.useItem(ctx, item_id)
            
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
            await ctx.send("You are not in the database yet, please use the start command to start your adventure!")
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

    @commands.hybrid_command(
        name="create_channels",
        description="Create The channels for Random Encounters",
    )
    async def create_channels(self, ctx: Context):
        await randomEncounter.generate_channels(ctx)
        await randomEncounter.loop_random_encounters(ctx)
        
    @commands.hybrid_command(
        name="delete_channels",
        description="Delete The channels for Random Encounters",
    )
    async def delete_channels(self, ctx: Context):
        await randomEncounter.delete_channels(ctx)
        
        
    #command to start a user's adventure, gives them a starter weapon and armor
    @commands.hybrid_command(
        name="start",
        description="Start your adventure!",
    )
    async def start(self, ctx: Context):
        #run the start function from helper/start.py
        await start.start(ctx)
        
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
        await ctx.send("Your twitch account has been disconnected from your discord account!")


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Basic(bot))
