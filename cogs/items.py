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

import aiohttp
import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord.ext.commands import Context, has_permissions

from helpers import battle, buy, checks, db_manager


# Here we name the cog and create a new class for the cog.
class Items(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    #command to add a new streamer and their server and their ID to the database streamer table, using the add_streamer function from helpers\db_manager.py
    #registering a streamer will also add them to the database user table
    @commands.hybrid_command(
        name="register",
        description="This command will add a new streamer to the database.",
    )
    async def register(self, ctx: Context, streamer_channel: str, emoteprefix: str):
        """
        This command will add a new streamer to the database.

        :param ctx: The context in which the command was called.
        :param streamer_channel: The streamer's twitch channel.
        :param streamer_server: The streamer's server.
        :param streamer_id: The streamer's ID.
        """

        twitch_id = await db_manager.get_twitch_id(streamer_channel)
        broadcaster_cast_type = await db_manager.get_broadcaster_type(streamer_channel)
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
                await db_manager.add_streamer(streamer_channel, user_id, emoteprefix, twitch_id, broadcaster_cast_type)
                await ctx.send("You are now a streamer.")
                return
            await db_manager.add_streamer(streamer_channel, user_id, emoteprefix, twitch_id, broadcaster_cast_type)
            await db_manager.add_user(user_id, True)
            await ctx.send("Streamer added to the database.")
            return
        elif broadcaster_cast_type == "affiliate":
            #if the user already exists in the database, update their streamer status to true
            if await db_manager.check_user(user_id):
                await db_manager.update_is_streamer(user_id)
                await db_manager.add_streamer(streamer_channel, user_id, emoteprefix, twitch_id, broadcaster_cast_type)
                await ctx.send("You are now a streamer.")
                return
            await db_manager.add_streamer(streamer_channel, user_id, emoteprefix, twitch_id, broadcaster_cast_type)
            await db_manager.add_user(user_id, True)
            await ctx.send("Streamer added to the database.")
            return
        elif broadcaster_cast_type == "":
            await db_manager.add_user(user_id, False)
            await ctx.send("Streamer is not a Partner or Affiliate, added to database as user.")
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
        await db_manager.remove_user(user_id)
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
        """
        This command will view your inventory.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        #check if the user exists in the database
        users = await db_manager.view_users()
        for i in users:
            user_id_if_exists = i[0]
            user_id_if_exists = int(user_id_if_exists)
            if user_id == user_id_if_exists:
                inventory = await db_manager.view_inventory(user_id)
                embed = discord.Embed(title="Inventory", description="Your inventory.", color=0x00ff00)
                for i in inventory:
                    item_id = i[1]
                    isitem_equipped = await db_manager.check_item_equipped(user_id, item_id)
                    item_name = i[2]
                    item_emoji = i[4]
                    item_amount = i[6]
                    item_rarity = i[5]
                    if isitem_equipped == 1:
                        embed.add_field(name=f"`ID:{item_id}` {item_name}{item_emoji}", value=f"rarity: {item_rarity} (equipped)", inline=False)
                    else:
                        embed.add_field(name=f"`ID:{item_id}` {item_name}{item_emoji} x{item_amount}", value=f"rarity: {item_rarity}", inline=False)
                await ctx.send(embed=embed)
                return
        await ctx.send(f"You do not exist in the database.")

    #command to create a new item in the database item table, using the add_item function from helpers\db_manager.py
    @commands.hybrid_command(
        name="createitem",
        description="This command will create a new item in the database.",
    )
    @checks.is_streamer()
    async def create_item(self, ctx: Context, item_name: str, item_emote: discord.PartialEmoji):
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
        item_sub_type = preset['item_sub_type']
        item_effect = preset['item_effect']
        isUsable = preset['isUsable']
        isEquippable = preset['isEquippable']
        if item_type == "Common":
            #pic a random crit chance from the first 5 crit chances
            item_crit_chance = random.choice(critChances[:5])
        elif item_type == "Uncommon":
            #pic a random crit chance from the first 10 crit chances but not the first 5
            item_crit_chance = random.choice(critChances[5:10])
        elif item_type == "Rare":
            #pick a random crit chance after 10 but not after 15
            item_crit_chance = random.choice(critChances[10:15])
        elif item_type == "Epic":
            #pic a random crit chance from the first 20 crit chances but not the first 15
            item_crit_chance = random.choice(critChances[15:20])
        elif item_type == "Legendary":
            #pic a random crit chance from the first 20 crit chances but not the first 15
            item_crit_chance = random.choice(critChances[20:25])
        #add the item to the database
        #send an embed to the streamer with the item info
        if item_type == "Weapon":
            embed = discord.Embed(title=f"Item Created", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}\nItem Damage: {item_damage}", color=0x00ff00)
        elif item_type == "Armor":
            embed = discord.Embed(title=f"Item Created", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}\nItem Defence: {item_damage}", color=0x00ff00)
        elif item_type == "Consumable":
            embed = discord.Embed(title=f"Item Created", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}\nItem Effect: {item_effect}", color=0x00ff00)
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
                await db_manager.add_item(streamerPrefix, item_name, item_price, item_rarity, emojiString, twitchID, item_type, item_damage, item_sub_type, item_crit_chance, item_effect, isUsable, isEquippable)
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
                item_type = preset['item_type']
                item_damage = preset['item_damage']
                #send an embed to the streamer with the item info
                embed = discord.Embed(title=f"Item Preset", description=f"Item: {item_name}\nItem Price: {item_price}\nItem Rarity: {item_rarity}\nItem Type: {item_type}\nItem Damage: {item_damage}", color=0x00ff00)
                #set the embed thumbnail to the emoji url
                embed.set_thumbnail(url=item_emote_url)
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

        #await db_manager.add_item(streamerPrefix, item_name, item_rarity, emojiString, twitchID, item_type, item_damage)

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
#STUB - shop command
    @commands.hybrid_command(
        name="shop",
        description="This command will display the shop.",
    )
    async def shop(self, ctx: Context):
        """
        This command will display the shop.

        :param ctx: The context in which the command was called.
        """
        shop = await db_manager.display_shop_items()
        embed = discord.Embed(title="Shop", description="All of the items in the shop.", color=0x00ff00)
        weaponembed = discord.Embed(title="Weapons", description="All of the weapons in the shop.", color=0x00ff00)
        armorembed = discord.Embed(title="Armor", description="All of the armor in the shop.", color=0x00ff00)
        heals = discord.Embed(title="Heals", description="All of the healing items in the shop.", color=0x00ff00)
        misc = discord.Embed(title="Misc", description="All of the misc items in the shop.", color=0x00ff00)
        #create a separate embed for each item type
        for i in shop:
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

            #grab the int out of the coroutine=
            if item_type == "Weapon" or item_type == "Projectile":
                #for each item in the item 
                #create an embed for this item type
                weaponembed.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Rarity**: `{item_rarity}` ", inline=True)
            if item_type == "Armor" or item_type == "Shield" or item_type == "Cosmetic":
                #create an embed for this item type
                armorembed.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Defence**: `{item_damage}` \n **Rarity**: `{item_rarity}` ", inline=True)
            #if its a consumable, and the item effect has the word heal in it, then display the heal amount
            #check if the word heal is in the item effect
            if item_type == "Consumable" and ("heal" in item_effect or "revive" in item_effect):
                #create an embed for this item type
                heals.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Heal**: `{item_damage}` \n **Rarity**: `{item_rarity}` ", inline=True)
            #if its a consumable, and the item effect has the word damage in it, then display the damage amount
            else:
                if item_damage == 0:
                    #create an embed for this item type whitch is misc
                    misc.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Rarity**: `{item_rarity}` ", inline=True)
        #await ctx.send(embed=embed)

        #create buttons to switch between the different embeds
        #create a list of all the embeds
        #make sure the emebds exist before adding them to the list
        embeds = []
        #add the embeds to the list
        if weaponembed.fields:
            embeds.append(weaponembed)
        if armorembed.fields:
            embeds.append(armorembed)
        if heals.fields:
            embeds.append(heals)
        if misc.fields:
            embeds.append(misc)


        #send the first embed, and add reactions to it to switch between the different embeds
        message = await ctx.send(embed=embeds[0])
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")






        #create a function to check if the reaction is the one we want
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]
        
        #switch between the different embeds
        i = 0
        reaction = None
        while True:
            if str(reaction) == "⬅️":
                if i > 0:
                    i -= 1
                    await message.edit(embed=embeds[i])
            elif str(reaction) == "➡️":
                if i < len(embeds)-1:
                    i += 1
                    await message.edit(embed=embeds[i])
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction, user)                
            except asyncio.TimeoutError:
                break

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
                    item_sub_type = await db_manager.get_basic_item_sub_type(item_id)
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
                            await db_manager.add_item_to_inventory(user_id, item_id, item_name, item_price, item_emoji, item_rarity, amount, item_type, item_damage, False, item_sub_type, item_crit_chance)
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
        embed.set_thumbnail(url=ctx.message.author.avatar.url)
        if isStreamer == 1:
            isStreamer = "Yes"
        elif isStreamer == 0:
            isStreamer = "No"
        embed.set_footer(text=f"User ID: {user_id} | Streamer: {isStreamer}")

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
        user_id = ctx.message.author.id
        item_name = await db_manager.get_basic_item_name(item_id)
        item_damage = await db_manager.get_basic_item_damage(item_id)
        isUsable = await db_manager.is_basic_item_usable(item_id)
        #get the items effect
        item_effect = await db_manager.get_basic_item_effect(item_id)
        #get streamer item effect
        #check if the item is a streamer item
        isStreamerItem = await db_manager.check_streamer_item(item_id)
        isStreamerItemUsable = await db_manager.get_streamer_item_usable(item_id)
        if isStreamerItem == 1:
            if isStreamerItemUsable == True or isStreamerItemUsable == 1:
                streamer_item_effect = await db_manager.get_streamer_item_effect(item_id)
                if "heal" in streamer_item_effect:
                    #get the amount to heal the user by
                    heal_amount = int(streamer_item_effect[5:])
                    #heal the user
                    await db_manager.add_health(user_id, heal_amount)
                    #remove the item from the users inventory
                    await db_manager.remove_item_from_inventory(user_id, item_id)
                    await ctx.send(f"You used `{item_name}` and healed `{heal_amount}` health.")
                    return
            else:
                await ctx.send(f"`{item_name}` is not usable.")
                return
            
        if isUsable == 1:
            #remove item from inventory
            #before removing the item, check if the users health is full, if it is, don't remove the item
            user_health = await db_manager.get_health(user_id)
            user_max_health = 100
            if user_health == user_max_health:
                await ctx.send(f"You are already at full health.")
                return
            print(item_effect)
            #if item effect has the word heal in it then heal the user
            if "heal" in item_effect:
                #get the amount to heal the user by
                heal_amount = int(item_effect[5:])
                #heal the user
                await db_manager.add_health(user_id, heal_amount)
                #remove the item from the users inventory
                await db_manager.remove_item_from_inventory(user_id, item_id)
                #send a message
                await ctx.send(f"You used `{item_name}` and healed {heal_amount} health.")
            elif "revive" in item_effect:
                #revive the user
                await db_manager.set_alive(user_id)
                #heal the user to full health
                await db_manager.set_health(user_id, 100)
                #remove the item from the users inventory
                await db_manager.remove_item_from_inventory(user_id, item_id)
                #send a message
                await ctx.send(f"You used `{item_name}` and revived.")
        else:
            await ctx.send(f"`{item_name}` is not usable.")
            
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
                item_sub_type = await db_manager.get_basic_item_sub_type(item_id)
                print(item_sub_type)
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
                #create an embed
                embed = discord.Embed(
                    title=f"{item_name}",
                    description=f"{item_description}",
                    color=discord.Color.from_rgb(255, 255, 255),
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
                if item_sub_type == "None" or item_sub_type == "none" or item_sub_type == 0:
                    pass
                else:
                    embed.add_field(name="Sub-Type", value=f"{item_sub_type}")
                embed.set_footer(text="Item ID: " + item_id)
                #send the embed
                if hasRecipe == 1 or hasRecipe == True:
                    edited_embed.add_field(name="Type", value=f"{item_type}")
                    if item_sub_type == "None" or item_sub_type == "none" or item_sub_type == 0:
                        pass
                    else:
                        edited_embed.add_field(name="Sub-Type", value=f"{item_sub_type}")
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
                embed = discord.Embed(
                    title=f"{item_name}",
                    description=f"An item from {streamer_name}, very rare. :)",
                    color=discord.Color.from_rgb(255, 255, 255),
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
                if item_sub_type == "None" or item_sub_type == "none" or item_sub_type == 0:
                    pass
                else:
                    embed.add_field(name="Sub-Type", value=f"{item_sub_type}")
                

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
                item_sub_type = await db_manager.get_basic_item_sub_type(item_id)
                print(item_sub_type)
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
                #create an embed
                embed = discord.Embed(
                    title=f"{item_name}",
                    description=f"{item_description}",
                    color=discord.Color.from_rgb(255, 255, 255),
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
                if item_sub_type == "None" or item_sub_type == "none" or item_sub_type == 0:
                    pass
                else:
                    embed.add_field(name="Sub-Type", value=f"{item_sub_type}")
                embed.set_footer(text="Item ID: " + item_id)
                #send the embed
                if hasRecipe == 1 or hasRecipe == True:
                    edited_embed.add_field(name="Type", value=f"{item_type}")
                    if item_sub_type == "None" or item_sub_type == "none" or item_sub_type == 0:
                        pass
                    else:
                        edited_embed.add_field(name="Sub-Type", value=f"{item_sub_type}")
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
                #create an embed
                embed = discord.Embed(
                    title=f"{item_name}",
                    description=f"An item from {streamer_name}, very rare. :)",
                    color=discord.Color.from_rgb(255, 255, 255),
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
                if item_sub_type == "None" or item_sub_type == "none" or item_sub_type == 0:
                    pass
                else:
                    embed.add_field(name="Sub-Type", value=f"{item_sub_type}")
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



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Items(bot))
