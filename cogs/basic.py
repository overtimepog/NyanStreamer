""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import asyncio
import datetime
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
from typing import List, Tuple


global i
i = 0
cash = "<:cash:1077573941515792384>"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
    # Add more rarities and colors as needed
}
# Here we name the cog and create a new class for the cog.
class Basic(commands.Cog, name="basic"):
    def __init__(self, bot):
        self.bot = bot

    #command to add a new streamer and their server and their ID to the database streamer table, using the add_streamer function from helpers\db_manager.py
    #registering a streamer will also add them to the database user table
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
#ANCHOR - Inventory
    @commands.hybrid_command(
        name="inventory",
        description="This command will view your inventory.",
    )
    async def inventory(self, ctx: Context):
        # Get user inventory items from the database
        inventory_items = await db_manager.view_inventory(ctx.author.id)
        if inventory_items == []:
            await ctx.send("You have no items in your inventory.")
            return

        # Calculate number of pages based on number of items
        num_pages = (len(inventory_items) // 5) + (1 if len(inventory_items) % 5 > 0 else 0)

        current_page = 0

        # Create a function to generate embeds from a list of items
        async def create_embeds(item_list):
            num_pages = (len(item_list) // 5) + (1 if len(item_list) % 5 > 0 else 0)
            embeds = []

            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                inventory_embed = discord.Embed(
                    title="Inventory",
                    description=f"{ctx.author.name}'s Inventory \n Commands: \n /equip ID: equips an item based on its ID \n /unequip ID: will unequip an item based on its ID. \n /sell ID amount: will sell that amount of an item from your inventory",
                )
                inventory_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                for item in item_list[start_idx:end_idx]:
                    item_id = item[1]
                    item_name = item[2]
                    item_price = item[3]
                    item_emoji = item[4]
                    item_rarity = item[5]
                    item_amount = item[6]
                    item_type = item[7]
                    item_damage = item[8]
                    is_equipped = item[9]
                    item_element = item[10]
                    item_crit_chance = item[11]
                    item_projectile = item[12]
                    if item_type == "Chest":
                        item_description = await db_manager.get_chest_description(item_id)
                    else:
                        item_description = await db_manager.get_basic_item_description(item_id)

                    inventory_embed.add_field(name=f"{item_emoji}{item_name} - x{item_amount}", value=f'**{item_description}** \n Type: `{item_type}` \n ID | `{item_id}` \n Equipped: {"Yes" if is_equipped else "No"}', inline=False)

                embeds.append(inventory_embed)

            return embeds

        # Create a list of embeds with 5 items per embed
        embeds = await create_embeds(inventory_items)
        class Select(discord.ui.Select):
                def __init__(self):
                    options=[
                        discord.SelectOption(label="All"),
                        discord.SelectOption(label="Weapon"),
                        discord.SelectOption(label="Tool"),
                        discord.SelectOption(label="Armor"),
                        discord.SelectOption(label="Consumable"),
                        discord.SelectOption(label="Material"),
                        discord.SelectOption(label="Badge"),
                        discord.SelectOption(label="Pet"),
                    ]
                    super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

                async def callback(self, interaction: discord.Interaction):
                    selected_item_type = self.values[0]

                    if selected_item_type == "All":
                        filtered_items = await db_manager.view_inventory(interaction.user.id)
                    else:
                        filtered_items = [item for item in await db_manager.view_inventory(interaction.user.id) if item[7] == selected_item_type]

                    filtered_embeds = await create_embeds(filtered_items)
                    new_view = InventoryButton(current_page=0, embeds=filtered_embeds)
                    try:
                        await interaction.response.edit_message(embed=filtered_embeds[0], view=new_view)
                    #catch IndexError 
                    except(IndexError):
                        await interaction.response.defer()
                    

        class InventoryButton(discord.ui.View):
                def __init__(self, current_page, embeds, **kwargs):
                    super().__init__(**kwargs)
                    self.current_page = current_page
                    self.embeds = embeds
                    self.add_item(Select())

                @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
                async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = 0
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
                async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page > 0:
                        self.current_page -= 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
                async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page < len(self.embeds) - 1:
                        self.current_page += 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
                async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = len(self.embeds) - 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

        view = InventoryButton(current_page=0, embeds=embeds)
        await ctx.send(embed=embeds[0], view=view)


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
        #print(streamer_prefix)
        #get the streamer prefix of the user
        user_streamer_prefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        #print(user_streamer_prefix)
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
        # Get all the quests from the database
        quests = await db_manager.get_quests_on_board()
        if quests == []:
            await ctx.send("There are no quests on the board.")
            return

        # Calculate number of pages based on number of quests
        num_pages = (len(quests) // 5) + (1 if len(quests) % 5 > 0 else 0)

        current_page = 0

        # Create a function to generate embeds from a list of quests
        async def create_embeds(quest_list):
            num_pages = (len(quest_list) // 5) + (1 if len(quest_list) % 5 > 0 else 0)
            embeds = []

            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                quest_embed = discord.Embed(
                    title="Quest Board",
                    description=f"Quests available for {ctx.author.name}. Use /questinfo <quest_id> to get more details.",
                )
                quest_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                for quest in quest_list[start_idx:end_idx]:
                    quest_id = quest[0]
                    quest_name = quest[1]
                    quest_xp = quest[3]
                    quest_reward = quest[4]
                    quest_reward_amount = quest[5]
                    quest_type = quest[7]
                    quest = quest[8]

                    # Format the quest type and quest
                    if quest_type == "collect":
                        quest_type = "Collect"
                        quest_parts = quest.split(" ")
                        item_id = quest_parts[1]
                        item_name = await db_manager.get_basic_item_name(item_id)
                        item_emoji = await db_manager.get_basic_item_emote(item_id)
                        quest = f"**{quest_parts[0]}** {item_emoji}{item_name}"
                    
                    elif quest_type == "kill":
                            quest_type = "Kill"
                            quest_parts = quest.split(" ")
                            enemy_id = quest_parts[1]
                            enemy_name = await db_manager.get_enemy_name(enemy_id)
                            enemy_emoji = await db_manager.get_enemy_emoji(enemy_id)
                            #clear the () and , from the enemy emoji
                            enemy_emoji = str(enemy_emoji)
                            enemy_emoji = enemy_emoji.replace("(", "")
                            enemy_emoji = enemy_emoji.replace(")", "")
                            enemy_emoji = enemy_emoji.replace(",", "")
                            #remove the ' on each side of the emoji
                            enemy_emoji = enemy_emoji.replace("'", "")
                            quest = f"**{quest_parts[0]}** {enemy_emoji}{enemy_name}"

                    # Replace "Money" with cash emoji
                    if quest_reward == "Money":
                        quest_reward = f"{cash} {quest_reward_amount}"
                    else:
                        # If the reward is an item, get the item name from the database
                        item_name = await db_manager.get_basic_item_name(quest_reward)
                        item_emoji = await db_manager.get_basic_item_emote(quest_reward)
                        quest_reward = f"{item_emoji}{item_name} x{quest_reward_amount}"

                    quest_embed.add_field(name=f"**{quest_name}**", value=f"ID | `{quest_id}` \n **Quest**: {quest_type} {quest} \n **XP**: {quest_xp} \n **Reward**: {quest_reward} \n", inline=False)

                embeds.append(quest_embed)

            return embeds


        # Create a list of embeds with 5 quests per embed
        embeds = await create_embeds(quests)

        class QuestBoardButton(discord.ui.View):
            def __init__(self, current_page, embeds, **kwargs):
                super().__init__(**kwargs)
                self.current_page = current_page
                self.embeds = embeds

            @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
            async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = 0
                await interaction.response.defer()
                await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
            async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page > 0:
                    self.current_page -= 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
            async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page < len(self.embeds) - 1:
                    self.current_page += 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
            async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = len(self.embeds) - 1
                await interaction.response.defer()
                await interaction.message.edit(embed=self.embeds[self.current_page])

        view = QuestBoardButton(current_page=0, embeds=embeds)
        await ctx.send(embed=embeds[0], view=view)

        #when the user clicks the check mark, add the quest to the users quest list, remove the quest from the quest board, check if the user already has the quest, and if they do, tell them they already have it, and if they dont, add it to their quest list
    @commands.hybrid_command(
    name="questinfo",
    description="Get detailed information about a specific quest.",
    )
    async def questinfo(self, ctx: Context, quest_id: str):
        # Get the quest from the database
        quest = await db_manager.get_quest_from_id(quest_id)
        if quest is None:
            await ctx.send("That quest does not exist.")
            return

        quest_id, quest_name, quest_description, quest_xp, quest_reward, quest_reward_amount, quest_level_req, quest_type, quest = quest

        # Create an embed with detailed information about the quest
        quest_embed = discord.Embed(title=f"**{quest_name}**")
        quest_embed.add_field(name="ID", value=quest_id)
        quest_embed.add_field(name="Description", value=quest_description)
        quest_embed.add_field(name="XP", value=quest_xp)
        quest_embed.add_field(name="Reward", value=f"{quest_reward_amount} {quest_reward}")
        quest_embed.add_field(name="Level Requirement", value=quest_level_req)
        quest_embed.add_field(name="Quest Type", value=quest_type)

        await ctx.send(embed=quest_embed)
    
    @commands.hybrid_command(
        name="acceptquest",
        description="Accept a quest from the quest board.",
    )
    async def acceptquest(self, ctx: Context, quest: str):
        # Get the quest id from the database
        quest = await db_manager.get_quest_from_id(quest_id)
        if quest is None:
            await ctx.send("That quest does not exist.")
            return

        quest_id = str(quest_id)

        # Get the user id
        user_id = ctx.message.author.id
        user_id = str(user_id)

        # Check if the user already has the quest
        user_has_quest = await db_manager.check_user_has_quest(user_id, quest_id)

        # Check if the user has any quest 
        user_has_any_quest = await db_manager.check_user_has_any_quest(user_id)

        isCompleted = await db_manager.check_quest_completed(user_id, quest_id)

        # Check if the user meets the level requirements
        user_level = await db_manager.get_level(user_id)
        level_req = await db_manager.get_quest_level_required(quest_id)

        # Convert them to integers
        user_level = int(user_level[0])
        level_req = int(level_req)

        if user_level < level_req:
            await ctx.send("You do not meet the level requirements for this quest!")
        elif isCompleted == True:
            await ctx.send("You already completed this quest!")
        elif user_has_quest == True:
            await ctx.send("You already have this quest!")
        elif user_has_any_quest == True:
            await ctx.send("You already have a quest! Abandon or complete your current quest to get a new one!")
        else:
            # If the user doesn't have the quest, add it to their quest list
            await db_manager.give_user_quest(user_id, quest_id)
            await db_manager.create_quest_progress(user_id, quest_id)
            await ctx.send("Quest added to your quest list!")
            # Remove the quest from the quest board
            # await db_manager.remove_quest_from_board(quest_id)

        
    #abandon quest hybrid command 
    @commands.hybrid_command(
        name="abandonquest",
        description="Abandon your current quest",
    )
    async def abandonquest(self, ctx: Context):
        await db_manager.remove_quest_from_user(ctx.author.id)
        await ctx.send("You have Abandoned your current quest, if you want to get a new one please check the quest board")
        
    
    #ANCHOR - shop command that shows the shop
    @commands.hybrid_command(
        name="shop",
        description="This command will show the shop.",
    )
    
    async def shop(self, ctx: Context):
        #get the shop items from the database
        shopitems = await db_manager.display_shop_items()

        # Calculate number of pages based on number of items
        num_pages = (len(shopitems) // 5) + (1 if len(shopitems) % 5 > 0 else 0)

        current_page = 0

        # Create a function to generate embeds from a list of items
        async def create_embeds(item_list):
            num_pages = (len(item_list) // 5) + (1 if len(item_list) % 5 > 0 else 0)
            embeds = []

            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                shop_embed = discord.Embed(
                    title="Shop",
                    description="This is the shop, you can buy items here with `/buy itemid #` EX. `/buy iron_sword 1`. \n"
                )
                shop_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                for item in item_list[start_idx:end_idx]:
                    item_id = item[0]
                    item_name = item[1]
                    item_price = item[2]
                    item_emoji = item[3]
                    item_rarity = item[4]
                    item_type = item[5]
                    item_damage = item[6]
                    is_usable = item[7]
                    is_equippable = item[8]
                    item_amount = item[9]
                    item_description = await db_manager.get_basic_item_description(item_id)
                    item_amount = await db_manager.get_shop_item_amount(item_id)
                    if await db_manager.check_chest(item_id):
                        item_name = await db_manager.get_chest_name(item_id)
                        item_emoji = await db_manager.get_chest_icon(item_id)
                        item_description = await db_manager.get_chest_description(item_id)
                        item_amount = await db_manager.get_shop_item_amount(item_id)
                        shop_embed.add_field(name=f"{item_emoji}{item_name} - {cash}{item_price}", value=f'**{item_description}** \n Type: `Chests` \n ID:`{item_id}`', inline=False)
                    else:
                        shop_embed.add_field(name=f"{item_emoji}{item_name} - {cash}{item_price}", value=f'**{item_description}** \n Type: `{item[5]}` \n ID:`{item_id}`', inline=False)
                embeds.append(shop_embed)

            return embeds

        # Create a list of embeds with 5 items per embed
        embeds = await create_embeds(shopitems)

        class Select(discord.ui.Select):
            def __init__(self):
                options=[
                    discord.SelectOption(label="All"),
                    discord.SelectOption(label="Weapon"),
                    discord.SelectOption(label="Tool"),
                    discord.SelectOption(label="Armor"),
                    discord.SelectOption(label="Consumable"),
                    discord.SelectOption(label="Material"),
                    discord.SelectOption(label="Badge"),
                ]
                super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                selected_item_type = self.values[0]

                if selected_item_type == "All":
                    filtered_items = shopitems
                else:
                    filtered_items = [item for item in shopitems if item[5] == selected_item_type]

                filtered_embeds = await create_embeds(filtered_items)
                new_view = ShopButton(current_page=0, embeds=filtered_embeds)
                await interaction.response.edit_message(embed=filtered_embeds[0], view=new_view)
                
        class ShopButton(discord.ui.View):
            def __init__(self, current_page, embeds, **kwargs):
                super().__init__(**kwargs)
                self.current_page = current_page
                self.embeds = embeds
                self.add_item(Select())

            @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
            async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = 0
                await interaction.response.defer()
                await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
            async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page > 0:
                    self.current_page -= 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])
                    
            @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
            async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page < len(self.embeds) - 1:
                    self.current_page += 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
            async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = len(self.embeds) - 1
                await interaction.response.defer()
                await interaction.message.edit(embed=self.embeds[self.current_page])

                
                
        view = ShopButton(current_page=0, embeds=embeds)
        await ctx.send(embed=embeds[0], view=view)
                
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
                                    await ctx.send(f"You already have this Weapon!")
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
                                    await ctx.send(f"You already have this Armor!")
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
                            #remove the item from the shop
                            #await db_manager.remove_shop_item_amount(item, amount)
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
    async def profile(self, ctx: Context, user: discord.User):
        """
        This command will view your profile.

        :param ctx: The context in which the command was called.
        """
        user_id = user.id
        user_profile = await db_manager.profile(user_id)
        #print(user_profile)
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
        #print all this info
        print(f"User ID: {user_id}")
        print(f"User Money: {user_money}")
        print(f"User Health: {user_health}")
        print(f"Is Streamer: {isStreamer}")
        print(f"User XP: {user_xp}")
        print(f"User Level: {user_level}")
        print(f"User Quest: {user_quest}")
        print(f"User Twitch ID: {user_twitch_id}")
        print(f"User Twitch Name: {user_twitch_name}")
        #get the xp needed for the next level
        xp_needed = await db_manager.xp_needed(user_id)
        #convert the xp needed to a string
        xp_needed = str(xp_needed)
        user_items = await db_manager.view_inventory(user_id)
        embed = discord.Embed(title="Profile", description=f"{user.mention}'s Profile.")
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
            badge = f"{badge_emote}{badge_name} \n"
            Userbadges.append(badge)
        
        #get each badge and add it to the badges feild
        Userbadges = ''.join(Userbadges)
        if Userbadges:
            embed.add_field(name="Badges", value=f"{Userbadges}", inline=False)
        
        inventory_items = await db_manager.view_inventory(user.id)
        
        pet_items = [item for item in inventory_items if item[7] == "Pet"]

        # Find the equipped pet
        equipped_pet = next((pet for pet in pet_items if pet[9] == 1), None)
    
        if equipped_pet is not None:
            pet_id = equipped_pet[1]
            pet_name = equipped_pet[2]
            pet_emoji = equipped_pet[4]
            pet_rarity = equipped_pet[5]
            pet_amount = equipped_pet[6]
            pet_description = await db_manager.get_basic_item_description(pet_id)
    
            embed.add_field(name=f"Pet", value=f'{pet_emoji}{pet_name}', inline=False)
        
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
        embed.set_thumbnail(url=user.avatar.url)
        if isStreamer == 1:
            isStreamer = "Yes"
        elif isStreamer == 0:
            isStreamer = "No"
        if user_twitch_id == None or user_twitch_id == "" or user_twitch_id == "None":
            user_twitch_id = "Not Connected"
        embed.set_footer(text=f"User ID: {user_id} | Twitch: {user_twitch_id} | Streamer: {isStreamer}")
        
        async def display_inventory(ctx, user):
            # Get user inventory items from the database
            inventory_items = await db_manager.view_inventory(user.id)
            if inventory_items == []:
                await ctx.send(f"{user.name} has no items in their inventory")
                return

            # Calculate number of pages based on number of items
            num_pages = (len(inventory_items) // 5) + (1 if len(inventory_items) % 5 > 0 else 0)

            current_page = 0

            # Create a function to generate embeds from a list of items
            async def create_embeds(item_list):
                num_pages = (len(item_list) // 5) + (1 if len(item_list) % 5 > 0 else 0)
                embeds = []

                for i in range(num_pages):
                    start_idx = i * 5
                    end_idx = start_idx + 5
                    inventory_embed = discord.Embed(
                        title="Inventory",
                        description=f"{user.name}'s Inventory \n",
                    )
                    inventory_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                    for item in item_list[start_idx:end_idx]:
                        item_id = item[1]
                        item_name = item[2]
                        item_price = item[3]
                        item_emoji = item[4]
                        item_rarity = item[5]
                        item_amount = item[6]
                        item_type = item[7]
                        item_damage = item[8]
                        is_equipped = item[9]
                        item_element = item[10]
                        item_crit_chance = item[11]
                        item_projectile = item[12]
                        item_description = await db_manager.get_basic_item_description(item_id)

                        inventory_embed.add_field(name=f"{item_emoji}{item_name} - x{item_amount}", value=f'**{item_description}** \n Type: `{item_type}` \n ID | `{item_id}` \n Equipped: {"Yes" if is_equipped else "No"}', inline=False)

                    embeds.append(inventory_embed)

                return embeds

            # Create a list of embeds with 5 items per embed
            embeds = await create_embeds(inventory_items)
            class Select(discord.ui.Select):
                    def __init__(self):
                        options=[
                            discord.SelectOption(label="All"),
                            discord.SelectOption(label="Weapon"),
                            discord.SelectOption(label="Tool"),
                            discord.SelectOption(label="Armor"),
                            discord.SelectOption(label="Consumable"),
                            discord.SelectOption(label="Material"),
                            discord.SelectOption(label="Badge"),
                            discord.SelectOption(label="Pet"),
                        ]
                        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

                    async def callback(self, interaction: discord.Interaction):
                        selected_item_type = self.values[0]

                        if selected_item_type == "All":
                            filtered_items = await db_manager.view_inventory(interaction.user.id)
                        else:
                            filtered_items = [item for item in await db_manager.view_inventory(interaction.user.id) if item[7] == selected_item_type]

                        filtered_embeds = await create_embeds(filtered_items)
                        new_view = InventoryButton(current_page=0, embeds=filtered_embeds)
                        try:
                            await interaction.response.edit_message(embed=filtered_embeds[0], view=new_view)
                    #catch IndexError 
                        except(IndexError):
                            await interaction.response.defer()

            class InventoryButton(discord.ui.View):
                    def __init__(self, current_page, embeds, **kwargs):
                        super().__init__(**kwargs)
                        self.current_page = current_page
                        self.embeds = embeds
                        self.add_item(Select())

                    @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
                    async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                        self.current_page = 0
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                    @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
                    async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                        if self.current_page > 0:
                            self.current_page -= 1
                            await interaction.response.defer()
                            await interaction.message.edit(embed=self.embeds[self.current_page])

                    @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
                    async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                        if self.current_page < len(self.embeds) - 1:
                            self.current_page += 1
                            await interaction.response.defer()
                            await interaction.message.edit(embed=self.embeds[self.current_page])

                    @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
                    async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                        self.current_page = len(self.embeds) - 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

            view = InventoryButton(current_page=0, embeds=embeds)
            await ctx.send(embed=embeds[0], view=view)
             
        async def display_pets(ctx, user):
            # Get user inventory items from the database
            inventory_items = await db_manager.view_inventory(user.id)
            if inventory_items == []:
                await ctx.send(f"{user.name} has no items in their inventory")
                return

            # Filter out items that are not pets
            pet_items = [item for item in inventory_items if item[7] == "Pet"]

            # Calculate number of pages based on number of pets
            num_pages = len(pet_items)

            current_page = 0
            

            rarity_colors = {
                "Common": 0x808080,  # Grey
                "Uncommon": 0x319236,  # Green
                "Rare": 0x4c51f7,  # Blue
                "Epic": 0x9d4dbb,  # Purple
                "Legendary": 0xf3af19,  # Gold
                # Add more rarities and colors as needed
            }

            # Create a function to generate embeds from a list of pets
            async def create_embeds(pet_list):
                embeds = []
                for i, pet in enumerate(pet_list):
                    pet_rarity = pet[5]
                    pet_color = rarity_colors.get(pet_rarity, 0x000000)

                for i, pet in enumerate(pet_list):
                    pet_embed = discord.Embed(
                        title=f"{user.name}'s {pet[2]}",
                        color=pet_color
                    )
                    pet_rarity = pet[5]
                    pet_embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{pet[4].split(':')[2].replace('>', '')}.gif?size=240&quality=lossless")
                    pet_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                    pet_id = pet[1]
                    pet_name = pet[2]
                    pet_emoji = pet[4]
                    pet_rarity = pet[5]
                    pet_amount = pet[6]
                    is_equipped = pet[9]
                    pet_description = await db_manager.get_basic_item_description(pet_id)

                    pet_embed.add_field(name=f"{pet_name} - x{pet_amount} \n", value=f'**{pet_description}** \n ID | `{pet_id}` \n Equipped: {"Yes" if is_equipped else "No"}', inline=False)

                    embeds.append(pet_embed)

                return embeds

            # Create a list of embeds with 1 pet per embed
            embeds = await create_embeds(pet_items)

            class PetButton(discord.ui.View):
                def __init__(self, current_page, embeds, **kwargs):
                    super().__init__(**kwargs)
                    self.current_page = current_page
                    self.embeds = embeds

                @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
                async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = 0
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
                async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page > 0:
                        self.current_page -= 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
                async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page < len(self.embeds) - 1:
                        self.current_page += 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
                async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = len(self.embeds) - 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

            view = PetButton(current_page=0, embeds=embeds)
            try:
                await ctx.send(embed=embeds[0], view=view)
            except(IndexError):
                await ctx.send(f"{user.name} has no pets")

        class ProfileView(discord.ui.View):
            def __init__(self, ctx):
                super().__init__()
                self.ctx = ctx
                self.user = user

            @discord.ui.button(label="Inventory", custom_id="profile_inv")
            async def inv_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await display_inventory(self.ctx, self.user)
                await interaction.response.defer()

            @discord.ui.button(label="Pets", custom_id="profile_pets")
            async def pets_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                # Handle the "Pets" button click here.
                await display_pets(self.ctx, self.user)
                await interaction.response.defer()

        view = ProfileView(ctx)
        await ctx.send(embed=embed, view=view)
        
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
            await db_manager.add_item_to_inventory(user_id, "pickaxe", 1)
            #equip the iron sword
            await db_manager.equip_item(user_id, "iron_sword")
            await ctx.send(f"You have started your Journey and your Iron Sword has been Equipped, Welcome {ctx.message.author.name} to **Dank Streamer**.")
        else:
            await ctx.send("You have already started your journey.")
        



#a command to give a user money using the add_money function from helpers\db_manager.py
    @commands.hybrid_command(
        name="pay",
        description="This command will give a user some of your money.",
    )
    async def pay(self, ctx: Context, user: discord.Member, amount: int):
        """
        This command will pay a user money.

        :param ctx: The context in which the command was called.
        :param user: The user that should be given money.
        :param amount: The amount of money that should be given.
        """
        user_id = ctx.message.author.id
        user_money = await db_manager.get_money(user_id)
        user_money = user_money[0][0]
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
        #print(item_equipped_id)
        #print(item_type)
        if item_equipped_id == item:
            await ctx.send(f"`{item_name}` is already equipped.")
            return
        if item_type == "Weapon":
            weapon_equipped = await db_manager.is_weapon_equipped(user_id)
            if weapon_equipped == True:
                await ctx.send(f"You already have a weapon equipped.")
                return 
            
        if item_type == "Pet":
            weapon_equipped = await db_manager.is_pet_equipped(user_id)
            if weapon_equipped == True:
                await ctx.send(f"You can only have 1 pet equipped at a time.")
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
            #get the item effect
            item_effect = await db_manager.get_basic_item_effect(item)
            if item_effect == None or item_effect == "None":
                message = f"You equipped `{item_name}`."
                await db_manager.equip_item(user_id, item)
                await ctx.send(message)
                return
            #print(item_effect)
            #split the effect by spaces
            item_effect = item_effect.split()
            #get the effect, the effect type, and the effect amount
            effect = item_effect[0]
            #print(effect)
            effect_add_or_minus = item_effect[1]
            #print(effect_add_or_minus)
            effect_amount = item_effect[2]
            #print(effect_amount)
            #if the effect is health
            if effect == "health":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's health
                    await db_manager.add_health_boost(user_id, effect_amount)
                    await db_manager.add_health(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` health."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's health
                    await db_manager.remove_health_boost(user_id, effect_amount)
                    await db_manager.remove_health(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` health."
                    
            #if the effect is damage
            elif effect == "damage":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's damage
                    await db_manager.add_damage_boost(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` damage."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's damage
                    await db_manager.remove_damage_boost(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` damage."
                    
            #if the effect is luck
            elif effect == "luck":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's luck
                    await db_manager.add_luck(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` luck."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's luck
                    await db_manager.remove_luck(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` luck."
                    
            #if the effect is crit chance
            elif effect == "crit_chance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's crit chance
                    await db_manager.add_crit_chance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` crit chance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's crit chance
                    await db_manager.remove_crit_chance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` crit chance."
                    
            #if the effect is dodge chance
            elif effect == "dodge_chance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's dodge chance
                    await db_manager.add_dodge_chance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` dodge chance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's dodge chance
                    await db_manager.remove_dodge_chance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` dodge chance."
                    
            #if the effect is fire resistance
            elif effect == "fire_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's fire resistance
                    await db_manager.add_fire_resistance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` fire resistance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's fire resistance
                    await db_manager.remove_fire_resistance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` fire resistance."
                    
            #if the effect is paralsys resistance
            elif effect == "paralysis_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's paralsys resistance
                    await db_manager.add_paralysis_resistance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` paralsys resistance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's paralsys resistance
                    await db_manager.remove_paralysis_resistance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` paralsys resistance."
                    
            #if the effect is poison resistance
            elif effect == "poison_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's poison resistance
                    await db_manager.add_poison_resistance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` poison resistance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's poison resistance
                    await db_manager.remove_poison_resistance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` poison resistance."
                    
            #if the effect is frost resistance
            elif effect == "frost_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #add the effect amount to the user's frost resistance
                    await db_manager.add_frost_resistance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` frost resistance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #remove the effect amount from the user's frost resistance
                    await db_manager.remove_frost_resistance(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` frost resistance."
            await db_manager.equip_item(user_id, item)
            await ctx.send(message)
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
            message = f"You unequipped `{item_name}`."
            #if the effect is health
            if effect == "health":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's health
                    await db_manager.remove_health_boost(user_id, effect_amount)
                    await db_manager.remove_health(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` health."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's health
                    await db_manager.add_health_boost(user_id, effect_amount)
                    await db_manager.add_health(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` health."
            #if the effect is damage
            elif effect == "damage":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's damage
                    await db_manager.remove_damage_boost(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` damage."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's damage
                    await db_manager.add_damage_boost(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` damage."
            #if the effect is luck
            elif effect == "luck":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's luck
                    await db_manager.remove_luck(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` luck."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's luck
                    await db_manager.add_luck(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` luck."
                    
            #if the effect is crit chance
            elif effect == "crit_chance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's crit chance
                    await db_manager.remove_crit_chance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` crit chance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's crit chance
                    await db_manager.add_crit_chance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` crit chance."
                
            #if the effect is dodge chance
            elif effect == "dodge_chance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's dodge chance
                    await db_manager.remove_dodge_chance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` dodge chance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's dodge chance
                    await db_manager.add_dodge_chance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` dodge chance."
                
            #if the effect is fire resistance
            elif effect == "fire_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's fire resistance
                    await db_manager.remove_fire_resistance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` fire resistance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's fire resistance
                    await db_manager.add_fire_resistance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` fire resistance."
            
            #if the effect is poison resistance
            elif effect == "poison_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's poison resistance
                    await db_manager.remove_poison_resistance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` poison resistance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's poison resistance
                    await db_manager.add_poison_resistance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` poison resistance."
                    
            #if the effect is frost resistance
            elif effect == "frost_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's frost resistance
                    await db_manager.remove_frost_resistance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` frost resistance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's frost resistance
                    await db_manager.add_frost_resistance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` frost resistance."
                    
            #if the effect is paralysis resistance
            elif effect == "paralysis_resistance":
                #if the effect is add
                if effect_add_or_minus == "+":
                    #remove the effect amount from the user's paralysis resistance
                    await db_manager.remove_paralysis_resistance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` paralysis resistance."
                #if the effect is minus
                elif effect_add_or_minus == "-":
                    #add the effect amount to the user's paralysis resistance
                    await db_manager.add_paralysis_resistance(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` paralysis resistance."
            await db_manager.unequip_item(user_id, item)
            await ctx.send(message)
        else:
            await ctx.send(f"`{item_name}` is not equipped.")
            
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
        await ctx.send("Check your DMs :)")
        await ctx.author.send(embed=embed, view=MyView(f"https://dankstreamer.lol/webhook?discord_id={ctx.author.id}")) # Send a message with our View class that contains the button
        
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
    async def fight(self, ctx: Context, target: discord.Member):
        #check if the user is in a battle
        #check if the user is in a battle
        user_exists = await db_manager.check_user(target.id)
        if user_exists == None:
            await ctx.send("This user does not exist!, tell them to do /start to start playing!")
            return
        #check if the user is dead
        user_is_alive = await db_manager.is_alive(ctx.author.id)
        if user_is_alive == False:
            await ctx.send("You are dead! wait to respawn! or use an item to revive!")
            return
        #check if the user is dead
        user_is_alive = await db_manager.is_alive(target.id)
        if user_is_alive == False:
            await ctx.send("This user is dead! wait till they respawn! or they use an item to revive!")
            return
        #attack the user
        await battle.userattack(ctx, target)
        
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

    #ANCHOR use command
    #a cooldown of 2 minutes
    @commands.cooldown(1, 120, commands.BucketType.user)
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
        #check if the item is in the inventory
        isItemThere = await db_manager.is_item_in_inventory(ctx.author.id, item)
        if isItemThere == False or isItemThere == None or isItemThere == 0:
            await ctx.send("You don't have this item!")
            await self.use.reset_cooldown(ctx)
            return
        user_id = ctx.message.author.id
        isChest = await db_manager.check_chest(item)
        if isChest == 1:
            item_name = await db_manager.get_chest_name(item)
            isUsable = 1
        else: 
            item_name = await db_manager.get_basic_item_name(item)
            isUsable = await db_manager.is_basic_item_usable(item)
        if isUsable == 1:
            #remove item from inventory
            await db_manager.remove_item_from_inventory(user_id, item, 1)
            #if the item's name is "Potion", add 10 health to the user
            #get the items effect
            item_effect = await db_manager.get_basic_item_effect(item)
            #if the item effect is "None":
            if item_effect == "None":
                item_effect = "None"
                item_effect_type = "None"
            elif isChest == 1:
                item_effect = "None"
                item_effect_type = "None"
            else:
                #split the item effect by space
                item_effect = item_effect.split(" ")
                #get the item effect type
                item_effect_type = item_effect[0]
                #get the item effect amount
                item_effect_amount = item_effect[2]
            #if the item effect type is "health"
            if item_effect_type == "health":
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
            chest_name = await db_manager.get_chest_name(item)
            itemID = item
            try:
                item = item.split("_")
            except:
                pass
            luck = await db_manager.get_luck(user_id)
            #if item[0] is chest
            if item[1] == "chest" or isChest == 1 or item == "chest":

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
                #print(itemID)
                chest_contents = await db_manager.get_chest_contents(itemID)
                def choose_item_based_on_chance(items_with_chances: List[Tuple]):
                    total = sum(w for i, w in items_with_chances)
                    r = random.uniform(0, total)
                    upto = 0
                    for item, w in items_with_chances:
                        if upto + w >= r:
                            return item
                        upto += w
                    assert False, "Shouldn't get here"
                # apply the luck to the chest item chances, then normalize them to sum to 1
                chest_contents = [({'item_id': item['item_id'], 'item_amount': item['item_amount']}, item['drop_chance'] + luck / 100) for item in chest_contents]
                total_chance = sum(chance for item, chance in chest_contents)
                chest_contents = [({'item_id': item['item_id'], 'item_amount': item['item_amount']}, chance / total_chance) for item, chance in chest_contents]

                # Choose an item based on chest item chances
                chosen_item = choose_item_based_on_chance(chest_contents)

                if chosen_item is not None:
                    await db_manager.add_item_to_inventory(ctx.author.id, chosen_item[0], chosen_item[2])
                    item_name = await db_manager.get_basic_item_name(chosen_item[0])
                    item_emoji = await db_manager.get_basic_item_emote(chosen_item[0])
                    # tell the user what they got
                    await ctx.send(random.choice(outcomePhrases) + f"{item_emoji} **{item_name}** - {chosen_item[2]}")
                    return 
                else:
                    #they found nothing
                    await ctx.send(f"It seems {chest_name} ended up being empty!")
                    return
        else:
            await ctx.send(f"`{item_name}` is not usable.")
            
            
    #explore command
    @commands.hybrid_command(
            name="explore",
            description="Explore a structure in the current channel.",
            usage="explore <structure>",
    )
    #command cooldown of 5 minutes
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def explore(self, ctx: Context, structure: str):
        if await db_manager.check_user(ctx.author.id) == 0:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.explore.reset_cooldown(ctx)
            return
    
        msg = ctx.message

        await db_manager.add_explorer_log(ctx.guild.id, ctx.author.id)
        structure_outcomes = await db_manager.get_structure_outcomes(structure)
        luck = await db_manager.get_luck(ctx.author.id)

        outcomes = []
        for outcome in structure_outcomes:
            quote = outcome[1]
            state = outcome[2]
            outcome_chance = outcome[3] * 100  # Multiply by 100 because your outcome_chance is in the range of 0.01 to 1
            outcome_type = outcome[4]
            outcome_thing = outcome[5]
            outcome_amount = outcome[6]
            outcome_money = outcome[7]
            outcome_xp = outcome[8]

            outcomes.append([quote, state, outcome_chance, outcome_type, outcome_thing, outcome_amount, outcome_money, outcome_xp])

        outcomes.sort(key=lambda x: x[2], reverse=True)

        roll = random.randint(1, 100) + luck
        if roll > 100:
            roll = 100
        elif roll < 1:
            roll = 1

        # Filter outcomes that the roll is equal or less than the chance.
        valid_outcomes = [item for item in outcomes if roll <= item[2]]

        if not valid_outcomes:  # If no valid outcomes, take the one with the highest chance
            item = outcomes[0]
        else:
            item = random.choice(valid_outcomes)

        outcome_quote = item[0]
        outcome_state = item[1]
        outcome_chance = item[2]
        outcome_type = item[3]
        outcome_thing = item[4]
        outcome_amount = item[5]
        outcome_money = item[6]
        outcome_xp = item[7]

        outcome_thing = str(outcome_thing)
        outcome_quote = str(outcome_quote).strip()
        if outcome_type == "item_gain":
            #if outcome things first word is chest, then add a to the end of the outcome_quote
            if outcome_thing.split("_")[0] == "chest":
                outcome_icon = await db_manager.get_chest_icon(outcome_thing)
                outcome_name = await db_manager.get_chest_name(outcome_thing)
            else:
                outcome_name = await db_manager.get_basic_item_name(outcome_thing)
                outcome_icon = await db_manager.get_basic_item_emote(outcome_thing)
            #send a message saying the outcome, and the item gained
            await ctx.send(f"{outcome_quote} + {outcome_amount} {outcome_icon} **{outcome_name}** ...And + ⭐{outcome_xp} XP!")
            #remove the health from the users health
            await db_manager.add_xp(msg.author.id, outcome_xp)
            #check if the user leveled up
            canLevelUp = await db_manager.can_level_up(msg.author.id)
            if canLevelUp == True:
                level = await db_manager.get_level(msg.author.id)
                #remove the () and , from the level
                level = str(level)
                level = level.replace("(", "")
                level = level.replace(")", "")
                level = level.replace(",", "")
                #if the user leveled up, send a message saying they leveled up
                await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
                await db_manager.add_level(msg.author.id, 1)
                
            userquest = await db_manager.get_user_quest(msg.author.id)
            if userquest != 0:
                #check if the users quest objective is to get an item and if the item is the item they got
                quest_objective = await db_manager.get_quest_objective_from_id(userquest)
                #seperate it by space and get the second thing
                quest_objective = quest_objective.split(" ")
                quest_objective = quest_objective[1]
                if quest_objective == outcome_thing:
                    #add one to the users quest progress
                    await db_manager.update_quest_progress(msg.author.id, userquest, outcome_amount)
                    #check the users quest progress
                    progress = await db_manager.get_quest_progress(msg.author.id, userquest)
                    total = await db_manager.get_quest_total_from_id(userquest)
                    #if the progress is less than the total, complete the quest and give the user the reward
                    if progress >= total:
                        #get quest reward type
                        quest_reward_type = await db_manager.get_quest_reward_type_from_id(userquest)
                        #if the quest reward type is item, give the user the item, and if its Money, give the user the money
                        if quest_reward_type == "item":
                            #get quest reward
                            quest_reward = await db_manager.get_quest_reward_from_id(userquest)
                            #get quest reward amount
                            quest_reward_amount = await db_manager.get_quest_reward_amount_from_id(userquest)
                            #add the item to the users inventory
                            await db_manager.add_item_to_inventory(msg.author.id, quest_reward, quest_reward_amount)
                            await ctx.send(f"Congrats {msg.author.mention}, you completed the quest **{await db_manager.get_quest_name_from_quest_id(userquest)}** and got x{quest_reward_amount} {await db_manager.get_basic_item_emote(quest_reward)} **{await db_manager.get_basic_item_name(quest_reward)}**!")
                        elif quest_reward_type == "Money":
                            #get quest reward amount
                            quest_reward_amount = await db_manager.get_quest_reward_amount_from_id(userquest)
                            #add the money to the users money
                            await db_manager.add_money(msg.author.id, quest_reward_amount)
                            await ctx.send(f"Congrats {msg.author.mention}, you completed the quest **{await db_manager.get_quest_name_from_quest_id(userquest)}** and got {cash}{quest_reward_amount} Money!")
                    await db_manager.mark_quest_completed(msg.author.id, userquest)
                    
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
            await ctx.send(f"{outcome_quote} + {outcome_amount} {outcome_icon} **{outcome_name}** ...And + ⭐{outcome_xp} XP")
            #remove the health from the users health
            await db_manager.add_xp(msg.author.id, outcome_xp)
            #check if the user leveled up
            canLevelUp = await db_manager.can_level_up(msg.author.id)
            if canLevelUp == True:
                #if the user leveled up, send a message saying they leveled up
                level = await db_manager.get_level(msg.author.id)
                #remove the () and , from the level
                level = str(level)
                level = level.replace("(", "")
                level = level.replace(")", "")
                level = level.replace(",", "")
                #if the user leveled up, send a message saying they leveled up
                await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
                await db_manager.add_level(msg.author.id, 1)
            #remove the item from the users inventory
            await db_manager.remove_item_from_inventory(msg.author.id, outcome_thing, outcome_amount)
        #if the outcome type is health_loss
        elif outcome_type == "health_loss":
            #send a message saying the outcome, and the health lost
            await ctx.send(f"{outcome_quote} - {outcome_amount} health! ...And + ⭐{outcome_xp} XP")
            #remove the health from the users health
            await db_manager.add_xp(msg.author.id, outcome_xp)
            #check if the user leveled up
            canLevelUp = await db_manager.can_level_up(msg.author.id)
            if canLevelUp == True:
                #if the user leveled up, send a message saying they leveled up
                level = await db_manager.get_level(msg.author.id)
                #remove the () and , from the level
                level = str(level)
                level = level.replace("(", "")
                level = level.replace(")", "")
                level = level.replace(",", "")
                #if the user leveled up, send a message saying they leveled up
                await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
                await db_manager.add_level(msg.author.id, 1)
            await db_manager.remove_health(msg.author.id, outcome_amount)
        #if the outcome type is health_gain
        elif outcome_type == "health_gain":
            #send a message saying the outcome, and the health gained
            await ctx.send(f"{outcome_quote} + {outcome_amount} health! ...And + ⭐{outcome_xp} XP")
            #remove the health from the users health
            await db_manager.add_xp(msg.author.id, outcome_xp)
            #check if the user leveled up
            canLevelUp = await db_manager.can_level_up(msg.author.id)
            if canLevelUp == True:
                #if the user leveled up, send a message saying they leveled up
                level = await db_manager.get_level(msg.author.id)
                #remove the () and , from the level
                level = str(level)
                level = level.replace("(", "")
                level = level.replace(")", "")
                level = level.replace(",", "")
                #if the user leveled up, send a message saying they leveled up
                await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
                await db_manager.add_level(msg.author.id, 1)
            #add the health to the users health
            await db_manager.add_health(msg.author.id, outcome_amount)
        #if the outcome type is money_gain
        elif outcome_type == "money_gain":
            #send a message saying the outcome, and the money gained
            await ctx.send(f"{outcome_quote} + {cash}{outcome_amount} ...And + ⭐{outcome_xp} XP")
                        #remove the health from the users health
            await db_manager.add_xp(msg.author.id, outcome_xp)
            #check if the user leveled up
            canLevelUp = await db_manager.can_level_up(msg.author.id)
            if canLevelUp == True:
                #if the user leveled up, send a message saying they leveled up
                level = await db_manager.get_level(msg.author.id)
                #remove the () and , from the level
                level = str(level)
                level = level.replace("(", "")
                level = level.replace(")", "")
                level = level.replace(",", "")
                #if the user leveled up, send a message saying they leveled up
                await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
                await db_manager.add_level(msg.author.id, 1)
            #add the money to the users money
            await db_manager.add_money(msg.author.id, outcome_amount)
        #if the outcome type is money_loss
        elif outcome_type == "money_loss":
            #send a message saying the outcome, and the money lost
            await ctx.send(f"{outcome_quote} - {cash}{outcome_amount} ...And + ⭐{outcome_xp} XP")
                        #remove the health from the users health
            await db_manager.add_xp(msg.author.id, outcome_xp)
            #check if the user leveled up
            canLevelUp = await db_manager.can_level_up(msg.author.id)
            if canLevelUp == True:
                #if the user leveled up, send a message saying they leveled up
                level = await db_manager.get_level(msg.author.id)
                #remove the () and , from the level
                level = str(level)
                level = level.replace("(", "")
                level = level.replace(")", "")
                level = level.replace(",", "")
                #if the user leveled up, send a message saying they leveled up
                await ctx.send(f"Congrats {msg.author.mention}, you leveled up! You are now level {level}!")
                await db_manager.add_level(msg.author.id, 1)
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
    async def craft(self, ctx: Context, recipe: str):
        """Craft an item"""
        # Get the user's inventory
        inventory = await db_manager.view_inventory(ctx.author.id)
        # If the user has no items
        if not inventory:
            # Send a message saying the user has no items
            await ctx.send("You have no items in your inventory!")
            return

        # Get the item info
        item_info = await db_manager.view_basic_item(recipe)
        #print(item_info)
        # If the item is not found
        if not item_info:
            # Send a message saying the item is not found
            await ctx.send("Item not found!")
            return

        # Get the item name, emote, and recipe
        item_name = item_info[0][1]
        item_emote = item_info[0][3]
        item_recipe = await db_manager.get_item_recipe(recipe)
        has_recipe = await db_manager.check_item_recipe(recipe)

        # If the item does not have a recipe
        if not has_recipe:
            await ctx.send(f"{item_emote} **{item_name}** does not have a recipe!")
            return

        # Check if the user has all the required items before crafting
        for recipe_item, recipe_amount in item_recipe:
            # Check if the user has the item and enough quantity of it
            if not await db_manager.check_user_has_item(ctx.author.id, recipe_item, recipe_amount):
                # Send a message saying the user does not have the item or enough quantity of it
                await ctx.send(f"You do not have enough {recipe_item}!")
                return

        # Remove required items from the user's inventory and give them the crafted item
        for recipe_item, recipe_amount in item_recipe:
            await db_manager.remove_item_from_inventory(ctx.author.id, recipe_item, recipe_amount)
        await db_manager.add_item_to_inventory(ctx.author.id, item_name, item_emote)
        await ctx.send(f"{item_emote} **{item_name}** has been crafted!")

            
            
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
        if monsterSpawned == 1:
            #start the battle
            monsterHealth = await db_manager.get_enemy_health(monsterID)
            await battle.attack(ctx, userID, userName, monsterID, monsterName)
        #if the monster is not spawned
        else:
            #send a message saying the monster is not spawned
            await ctx.send(f"**{monsterName}** is not spawned, wait for the current Monster to be defeated!")
            return
    
    
#spawn command
    @commands.hybrid_command()
    @checks.is_owner()
    async def spawn(self, ctx: Context, enemy: str):
        """Spawn an enemy"""
        #start the battle
        await battle.spawn_monster(ctx, enemy)
        
#mob command to view the current mob spawned
    @commands.hybrid_command()
    async def mob(self, ctx: Context):
        """View the current mob spawned"""
        #get the current mob spawned
        currentSpawn = await db_manager.get_current_spawn(ctx.guild.id)
        #if there is no mob spawned
        if currentSpawn == None or [] or [ ]:
            #send a message saying there is no mob spawned
            await ctx.send("There is no mob spawned!")
            return
        #if there is a mob spawned
        else:
            await battle.send_spawned_embed(ctx)
            #get the mob emote
            return
        
#recipe book command, to view all the recipes
    @commands.hybrid_command(
        name="recipebook",
        description="This command will view all the recipes.",
    )
    async def recipebook(self, ctx: Context):
        # Get all the recipes from the database
        recipes = await db_manager.get_all_recipes()

        # If there are no recipes, send a message saying there are no recipes
        if not recipes:
            await ctx.send("There are no recipes!")
            return

        # Calculate number of pages based on number of recipes
        num_pages = (len(recipes) // 5) + (1 if len(recipes) % 5 > 0 else 0)
        current_page = 0

        # Create a function to generate embeds from a list of recipes
        async def create_embeds(recipe_list):
            recipes_dict = {}
            for recipe in recipe_list:
                recipe_id = recipe[0]
                item_id = recipe[1]
                item_quantity = recipe[2]
                recipe_emote = await db_manager.get_basic_item_emote(recipe_id)
                item_emote = await db_manager.get_basic_item_emote(item_id)
                item_name = await db_manager.get_basic_item_name(item_id)
                recipe_name = await db_manager.get_basic_item_name(recipe_id)
                if recipe_id not in recipes_dict:
                    recipes_dict[recipe_id] = {'recipe_emote': recipe_emote, 'recipe_name': recipe_name, 'items': []}
                recipes_dict[recipe_id]['items'].append({'name': item_name, 'emote': item_emote, 'quantity': item_quantity})

            num_pages = (len(recipes_dict) // 5) + (1 if len(recipes_dict) % 5 > 0 else 0)
            embeds = []

            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                recipe_embed = discord.Embed(
                    title="Recipe Book",
                    description="All the recipes in the game!",
                    color=0x000000,
                )
                recipe_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                for recipe_id, recipe_data in list(recipes_dict.items())[start_idx:end_idx]:
                    recipe_emote = recipe_data['recipe_emote']
                    recipe_name = recipe_data['recipe_name']
                    recipe_items = recipe_data['items']
                    recipe_items_string = "\n".join([f"{item['quantity']}x {item['emote']}{item['name']}" for item in recipe_items])
                    recipe_embed.add_field(name=f"{recipe_emote}{recipe_name} (`{recipe_id}`)", value=recipe_items_string, inline=False)

                embeds.append(recipe_embed)

            return embeds


        embeds = await create_embeds(recipes)
        class Select(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="All"),
                    discord.SelectOption(label="Weapon"),
                    discord.SelectOption(label="Tool"),
                    discord.SelectOption(label="Armor"),
                    discord.SelectOption(label="Consumable"),
                    discord.SelectOption(label="Material"),
                    discord.SelectOption(label="Badge"),
                ]
                super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                selected_item_type = self.values[0]

                if selected_item_type == "All":
                    filtered_recipes = await db_manager.get_all_recipes()
                else:
                    filtered_recipes = []
                    all_recipes = await db_manager.get_all_recipes()

                    for recipe in all_recipes:
                        item_type = await db_manager.get_basic_item_type(recipe[0])
                        if item_type == selected_item_type or selected_item_type == "All":
                            filtered_recipes.append(recipe)


                filtered_embeds = await create_embeds(filtered_recipes)
                new_view = RecipebookButton(current_page=0, embeds=filtered_embeds)
                await interaction.response.edit_message(embed=filtered_embeds[0], view=new_view)
            
        class RecipebookButton(discord.ui.View):
            def __init__(self, current_page, embeds, **kwargs):
                super().__init__(**kwargs)
                self.current_page = current_page
                self.embeds = embeds
                self.add_item(Select())
            @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
            async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = 0
                await interaction.response.defer()
                await interaction.message.edit(embed=self.embeds[self.current_page])
            @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
            async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page > 0:
                    self.current_page -= 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])
            @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
            async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page < len(self.embeds) - 1:
                    self.current_page += 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])
            @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
            async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = len(self.embeds) - 1
                await interaction.response.defer()
                await interaction.message.edit(embed=self.embeds[self.current_page])

        view = RecipebookButton(current_page=0, embeds=embeds)
        await ctx.send(embed=embeds[0], view=view)

    @commands.hybrid_command(
            name="beastiary",
            description="This command will view all the enemies.",
        )
    async def beastiary(self, ctx: Context):
            # Get all the enemies from the database
            enemies = await db_manager.get_all_enemies()

            # Get all the drops from the database
            drops = await db_manager.get_all_enemy_drops()

            # If there are no enemies, send a message saying there are no enemies
            if not enemies:
                await ctx.send("There are no enemies!")
                return

            # Transform data into dictionaries
            enemies_dict = {enemy[0]: enemy for enemy in enemies}
            drops_dict = {}
            for drop in drops:
                enemy_id = drop[0]
                if enemy_id not in drops_dict:
                    drops_dict[enemy_id] = []
                drops_dict[enemy_id].append(drop)

            # Create a function to generate embeds from a list of enemies
            async def create_embeds(enemy_dict, drop_dict):
                num_pages = (len(enemy_dict) // 5) + (1 if len(enemy_dict) % 5 > 0 else 0)
                embeds = []
                enemy_ids = list(enemy_dict.keys())

                for i in range(num_pages):
                    start_idx = i * 5
                    end_idx = start_idx + 5

                    beastiary_embed = discord.Embed(
                        title="Beastiary",
                        description="All the enemies in the game!",
                        color=0x000000,
                    )
                    beastiary_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                    for enemy_id in enemy_ids[start_idx:end_idx]:
                        enemy_data = enemy_dict[enemy_id]
                        enemy_emote = enemy_data[4]  # Assuming enemy emote is at index 4
                        enemy_name = enemy_data[1]  # Assuming enemy name is at index 1

                        # Generate drops info
                        drop_infos = drop_dict.get(enemy_id, [])
                        if drop_infos:
                            unique_drops = set([drop[1] for drop in drop_infos])
                            drop_info_list = []
                            for unique_drop in unique_drops:
                                item_emote = await db_manager.get_basic_item_emote(unique_drop)
                                item_name = await db_manager.get_basic_item_name(unique_drop)
                                drop_info_list.append(f"\t{item_emote} {item_name}")
                            drop_info = "\n".join(drop_info_list)
                        else:
                            drop_info = "No Drops"

                        beastiary_embed.add_field(name=f"\n{enemy_name}{enemy_emote}(`{enemy_id}`)", value=f"\n{drop_info}\n", inline=False)

                    embeds.append(beastiary_embed)

                return embeds

            embeds = await create_embeds(enemies_dict, drops_dict)

            class BeastiaryButton(discord.ui.View):
                def __init__(self, current_page, embeds, **kwargs):
                    super().__init__(**kwargs)
                    self.current_page = current_page
                    self.embeds = embeds

                @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
                async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = 0
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
                async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page > 0:
                        self.current_page -= 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
                async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page < len(self.embeds) - 1:
                        self.current_page += 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
                async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = len(self.embeds) - 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

            view = BeastiaryButton(current_page=0, embeds=embeds)
            await ctx.send(embed=embeds[0], view=view)


#petview command
    @commands.hybrid_command(
        name="petview",
        description="This command will view all pets in the game.",
    )
    async def petview(self, ctx: Context):
        # Get all pets from the database
        pets = await db_manager.get_all_pets()
        if pets == []:
            await ctx.send("There are no pets in the game.")
            return

        # Calculate number of pages based on number of items
        num_pages = (len(pets) // 5) + (1 if len(pets) % 5 > 0 else 0)

        # Create a function to generate embeds from a list of pets
        async def create_embeds(pet_list):
            num_pages = (len(pet_list) // 5) + (1 if len(pet_list) % 5 > 0 else 0)
            embeds = []

            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                pet_embed = discord.Embed(
                    title="Pets",
                    description=f"All available pets in the game, you can find them in Pet Chests!",
                )
                pet_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                for pet in pet_list[start_idx:end_idx]:
                    pet_id = pet[0] #id
                    pet_name = pet[1] #name
                    pet_price = pet[2] #price
                    pet_emoji = pet[3] #emoji
                    pet_rarity = pet[4] #rarity
                    pet_type = pet[5] #emoji
                    pet_effect = pet[17]

                    pet_embed.add_field(name=f"{pet_emoji}{pet_name} (`{pet_id}`)", value=f'**Effect: {pet_effect}** \n Price: `{pet_price}` \n Rarity: `{pet_rarity}` \n', inline=False)

                embeds.append(pet_embed)

            return embeds

        # Create a list of embeds with 5 pets per embed
        embeds = await create_embeds(pets)

        class PetviewButton(discord.ui.View):
                def __init__(self, current_page, embeds, **kwargs):
                    super().__init__(**kwargs)
                    self.current_page = current_page
                    self.embeds = embeds

                @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
                async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = 0
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
                async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page > 0:
                        self.current_page -= 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
                async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page < len(self.embeds) - 1:
                        self.current_page += 1
                        await interaction.response.defer()
                        await interaction.message.edit(embed=self.embeds[self.current_page])

                @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
                async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    self.current_page = len(self.embeds) - 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

        view = PetviewButton(current_page=0, embeds=embeds)
        await ctx.send(embed=embeds[0], view=view)
    

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Basic(bot))