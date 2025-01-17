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
import time
from discord.ui import Select, View, Button

from helpers import battle, checks, db_manager, hunt, mine, search, bank, beg
from typing import List, Tuple
from discord.ext.commands.errors import CommandInvokeError
from num2words import num2words
import logging
from discord import User

global i
i = 0
cash = "⌬"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
    # Add more rarities and colors as needed
}

async def open_chest(self, ctx, chest_id: str, user_luck: int):
        chest_data = await db_manager.get_chest_data_by_id(chest_id)
        if not chest_data:
            await ctx.send("Invalid chest ID.")
            return

        chest_contents = chest_data["chest_contents"]
        items_awarded = {}

        for item in chest_contents:
            if random.randint(1, 100) <= (item["drop_chance"] * 100 + user_luck):
                if item["item_id"] in items_awarded:
                    items_awarded[item["item_id"]] += item["item_amount"]
                else:
                    items_awarded[item["item_id"]] = item["item_amount"]

        description = "You opened the chest and received:\n"
        for item_id, amount in items_awarded.items():
            item_data = await db_manager.get_basic_item_data(item_id)
            item_emoji = item_data["item_emoji"]
            item_name = item_data["item_name"]
            description += f"{amount} {item_emoji} {item_name}\n"
            await db_manager.add_item_to_inventory(ctx.author.id, item_id, amount)

        embed = discord.Embed(
            title="Chest Opened",
            description=description,
            color=0xFFD700
        )
        await ctx.send(embed=embed)

class PetSelect(discord.ui.Select):
    def __init__(self, pets: list, bot, user, item):
        self.bot = bot
        self.pets = pets
        self.user = user
        self.item = item
        self.selected_pet = None
        super().__init__(placeholder='Select your pet...', min_values=1, max_values=1)

    async def prepare_options(self):
        options = []
        self.pets = await db_manager.get_users_pets(self.user.id)
        for pet in self.pets:
            pet_emoji = await db_manager.get_basic_item_emoji(pet[0])
            petitemname = await db_manager.get_basic_item_name(pet[0])
            rarity = await db_manager.get_basic_item_rarity(pet[0])
            options.append(discord.SelectOption(label=pet[2], value=pet[0], emoji=pet_emoji, description=f"{rarity} Level {pet[3]} {petitemname}"))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.selected_pet = await db_manager.get_pet_attributes(interaction.user.id, self.values[0])
        # Retrieve the selected pet from the dropdown menu
        selected_pet = self.selected_pet
        if selected_pet is not None:
            #get the items effect
            pet_id = selected_pet[0]
            pet_name = selected_pet[2]
            item_effect = await db_manager.get_basic_item_effect(self.item)
            item_name = await db_manager.get_basic_item_name(self.item)
            item_emoji = await db_manager.get_basic_item_emoji(self.item)
            #if the item effect is "None":
            if item_effect == "None":
                print("Shouldn't get here")
                return

            #split the item effect by space
            item_effect = item_effect.split(" ")
            #get the item effect type
            item_effect_type = item_effect[0]
            #get the item effect amount
            item_effect_amount = item_effect[2]
            try:
                item_effect_time = item_effect[3]
            except:
                item_effect_time = 0

            #if the time is 0, it is a permanent effect
            if item_effect_time == 0:
                #get the effect
                effecttype = item_effect_type
                #if the item_effect is pet_xp
                if effecttype == "pet_xp":
                    #add the effect amount to the pet's xp
                    await db_manager.add_pet_xp(pet_id, item_effect_amount)
                    #check if pet can level up
                    canLevelup = await db_manager.pet_can_level_up(pet_id)
                    if canLevelup == True:
                        #level up the pet
                        await db_manager.add_pet_level(pet_id, interaction.user.id, 1)
                        #get the pet's new level
                        pet_level = await db_manager.get_pet_level(pet_id)
                        #if the pet is level 10, it will evolve
                        if pet_level == 10:
                            #tell the user they can evolve their pet
                            await interaction.response.send_message(f"You used **{item_emoji}{item_name}** on **{pet_name}** and gave them **{item_effect_amount} XP** They Leveled up :), **{pet_name}** is now level **{pet_level}**! You can now evolve your pet with `s.evolve {pet_id} or /evolve`")
                            return
                        else:
                            await interaction.response.send_message(f"You used **{item_emoji}{item_name}** on **{pet_name}** and gave them **{item_effect_amount} XP** They Leveled up :), **{pet_name}** is now level **{pet_level}**!")
                            return
                    else:
                        await interaction.response.send_message(f"You used **{item_emoji}{item_name}** on **{pet_name}** and gave them **{item_effect_amount} XP**!")
                        return

            #if the time is not 0, it is a temporary effect
            #get the effect
            effect = await db_manager.get_basic_item_effect(self.item)
            pet_items = await db_manager.get_pet_items(pet_id, self.user.id)
            #check if the pet already has the item
            for i in pet_items:
                if self.item in i:
                    await interaction.response.send_message(f"{pet_name} already has this item, Please wait for its Durration to run out", ephemeral=True)
                    return
            await db_manager.add_pet_item(self.user.id, pet_id, self.item)
            await db_manager.add_timed_item(self.user.id, self.item, effect)
            embed = discord.Embed(
                title=f"You used {item_name}",
                description=f"You used `{item_name}` on `{pet_name}` and gave them the effect `{item_effect_type}` for `{item_effect_time}`!",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message('No pet was selected.', ephemeral=True)
            return


class PetSelectView(discord.ui.View):
        def __init__(self, pets: list, user: discord.User, bot, item):
            super().__init__()
            self.user = user
            self.value = None
            self.select = PetSelect(pets, bot, user, item)
            self.add_item(self.select)


        async def prepare(self):
            await self.select.prepare_options()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return self.user.id == interaction.user.id



class LeaderboardDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Highest Level", value="highest_level"),
            discord.SelectOption(label="Most Money", value="most_money"),
        ]
        super().__init__(placeholder="Choose a leaderboard category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        leaderboard = await db_manager.get_leaderboard(interaction.client, category, limit=50)  # Adjust the limit as needed

        if not leaderboard:
            await interaction.response.send_message(f"No entries found for the '{category}' leaderboard.", ephemeral=True)
            return

        # Calculate next reset time (Friday at 5 PM EST)
        now = datetime.datetime.now(pytz.timezone('US/Eastern'))
        next_friday = now + datetime.timedelta((4 - now.weekday()) % 7)
        next_reset = next_friday.replace(hour=17, minute=0, second=0, microsecond=0)
        next_reset_unix = int(time.mktime(next_reset.timetuple()))

        per_page = 10  # Number of entries per page
        pages = [leaderboard[i:i + per_page] for i in range(0, len(leaderboard), per_page)]

        self.view.update_leaderboard(pages, per_page, category, next_reset_unix)
        embed = self.view.create_embed(pages[0])
        await interaction.response.edit_message(embed=embed, view=self.view)

class LeaderboardView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.pages = []
        self.per_page = 10
        self.current_page = 0
        self.category = "highest_level"
        self.next_reset_unix = int(time.mktime(datetime.datetime.now().timetuple()))
        self.add_item(LeaderboardDropdown())
        self.add_item(PreviousButton())
        self.add_item(NextButton())
        self.add_item(CloseButton())

    def create_embed(self, entries):
        embed = discord.Embed(title=f"{self.category.replace('_', ' ').title()} Leaderboard | Next reset: <t:{self.next_reset_unix}:R>")
        medals = ["🏆", "🥈", "🥉"]
        for entry in entries:
            rank = entry['rank']
            username = entry['username']
            value = entry['value']
            name = f"{medals[rank-1]}{rank}: {username.title()}" if rank <= 3 else f"{rank}: {username.title()}"
            if self.category == "highest_level":
                stats = f"Level: {value}"
            elif self.category == "most_money":
                stats = f"Money: {value}"
            embed.add_field(
                name=name,
                value=stats,
                inline=False
            )
        embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.pages)}")
        return embed

    def update_leaderboard(self, pages, per_page, category, next_reset_unix):
        self.pages = pages
        self.per_page = per_page
        self.category = category
        self.next_reset_unix = next_reset_unix
        self.current_page = 0

class PreviousButton(Button):
    def __init__(self):
        super().__init__(label="≪", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.current_page > 0:
            view.current_page -= 1
            embed = view.create_embed(view.pages[view.current_page])
            await interaction.response.edit_message(embed=embed, view=view)

class NextButton(Button):
    def __init__(self):
        super().__init__(label="≫", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.current_page < len(view.pages) - 1:
            view.current_page += 1
            embed = view.create_embed(view.pages[view.current_page])
            await interaction.response.edit_message(embed=embed, view=view)

class CloseButton(Button):
    def __init__(self):
        super().__init__(label="Close", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()


class Basic(commands.Cog, name="basic"):
    def __init__(self, bot):
        self.bot = bot
        self.shop_reset.start()
        self.revive_users.start()
        self.update_leaderboard.start()
        self.bot.loop.create_task(self.start_weekly_leaderboard_reset())

    @tasks.loop(hours=8)
    async def shop_reset(self):
        print("-----------------------------")
        print("Resetting Shop...")
        await db_manager.clear_shop()
        await db_manager.add_shop_items()
        print("Done Resetting Shop...")
        print("-----------------------------")
        
    #task to update the leaderboard every 20min
    @tasks.loop(minutes=20)
    async def update_leaderboard(self):
        print("-----------------------------")
        print("Updating Leaderboard...")
        await db_manager.update_leaderboard()
        print("Done Updating Leaderboard...")
        print("-----------------------------")
    
    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=168)  # Loop every week (168 hours)
    async def weekly_leaderboard_reset(self):
        print("-----------------------------")
        print("Resetting Leaderboard and Distributing Prizes...")
        categories = ["highest_level", "most_money"]

        for category in categories:
            leaderboard = await db_manager.get_leaderboard(self.bot, category, limit=3)
            if leaderboard:
                for entry in leaderboard:
                    user_id = entry['user_id']
                    rank = entry['rank']

                    if user_id == 0:
                        continue

                    if rank == 1:
                        prize = "gold_trophy"
                    elif rank == 2:
                        prize = "silver_trophy"
                    elif rank == 3:
                        prize = "bronze_trophy"

                    await db_manager.add_item_to_inventory(user_id, prize, 1)
                    user = await self.bot.fetch_user(user_id)
                    await user.send(f"Congratulations! You placed {rank} in the {category.replace('_', ' ')} leaderboard and received a {prize}!")

        await db_manager.delete_leaderboard()
        await db_manager.update_leaderboard()
        print("Done Resetting Leaderboard and Distributing Prizes...")
        print("-----------------------------")

    @weekly_leaderboard_reset.before_loop
    async def before_weekly_leaderboard_reset(self):
        await self.bot.wait_until_ready()

    async def start_weekly_leaderboard_reset(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.now(pytz.timezone('US/Eastern'))
        next_friday = now + datetime.timedelta((4 - now.weekday()) % 7)
        next_reset = next_friday.replace(hour=17, minute=0, second=0, microsecond=0)
        if now > next_reset:
            next_reset += datetime.timedelta(weeks=1)
        delay = (next_reset - now).total_seconds()

        await asyncio.sleep(delay)
        self.weekly_leaderboard_reset.start()

    @shop_reset.before_loop
    async def before_shop_reset(self):
        await self.bot.wait_until_ready()

    #task to check and revive users every minute
    @tasks.loop(minutes=1)
    async def revive_users(self):
        await db_manager.revive_users()

    @revive_users.before_loop
    async def before_revive_users(self):
        await self.bot.wait_until_ready()

    @commands.hybrid_command(name="leaderboard", description="Show the leaderboard for a specified category.", aliases=["lb"])
    async def leaderboard(self, ctx: commands.Context):
        """
        Display the leaderboard for a chosen category.

        :param ctx: The context of the command.
        """
        view = LeaderboardView()
        await ctx.send("Select a leaderboard category:", view=view)

    #rank
    #command to view the user's rank, using the get_user_rank function from helpers\db_manager.py
    @commands.hybrid_command(
        name="rank",
        description="This command will show your rank.",
        aliases=["r", "ranks"],
    )
    async def rank(self, ctx: Context, user: discord.User = None):
        if user is None:
            user = ctx.author
            user_id = ctx.author.id

        print(f"Fetching ranks for user_id: {user_id}")
        most_money_rank, highest_level_rank = await db_manager.get_user_ranks(user_id)

        if most_money_rank is not None or highest_level_rank is not None:
            embed = discord.Embed(title=f"Ranks for {user.name}", color=discord.Color.blue())
            embed.add_field(name="Most Money Rank", value=most_money_rank if most_money_rank is not None else "Not ranked", inline=True)
            embed.add_field(name="Highest Level Rank", value=highest_level_rank if highest_level_rank is not None else "Not ranked", inline=True)

            await ctx.send(embed=embed)
            print(f"Ranks sent for user_id: {user_id}")
        else:
            await ctx.send(f"User with ID {user_id} not found in the leaderboards.")
            print(f"No ranks found for user_id: {user_id}")



    #command to add a new streamer and their server and their ID to the database streamer table, using the add_streamer function from helpers\db_manager.py
    #registering a streamer will also add them to the database user table
    #command to veiw all streamers in the database streamer table, using the view_streamers function from helpers\db_manager.py

    #command to view inventory of a user, using the view_inventory function from helpers\db_manager.py
    #ANCHOR - Inventory
    @commands.hybrid_command(
        name="inventory",
        description="This command will view your inventory.",
        aliases=["inv"],
    )
    async def inventory(self, ctx: Context):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser in [None, False, [], "None", 0]:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return

        # Get user inventory items from the database
        inventory_items = await db_manager.view_inventory(ctx.author.id)
        if not inventory_items:
            await ctx.send("You have no items in your inventory.")
            return

        # Calculate number of pages based on number of items
        num_pages = (len(inventory_items) // 5) + (1 if len(inventory_items) % 5 > 0 else 0)

        current_page = 0

        # Create a function to generate embeds from a list of items
        async def create_embeds(item_list, ctx: Context):
            num_pages = (len(item_list) // 5) + (1 if len(item_list) % 5 > 0 else 0)
            embeds = []

            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                inventory_embed = discord.Embed(
                    title="Inventory",
                    description=f"{ctx.author.name}'s Inventory \n Commands: \n s.equip ID: equips an item based on its ID \n s.unequip ID: will unequip an item based on its ID. \n s.sell ID amount: will sell that amount of an item from your inventory",
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
                    #check for all the ammo of the type in the users inventory
                    
                    if item_type == "Weapon":
                        ammo_id = await db_manager.get_ammo_id(item_id)
                        ammo_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, ammo_id)
                        ammo_name = await db_manager.get_basic_item_name(ammo_id)
                        ammo_emoji = await db_manager.get_basic_item_emoji(ammo_id)

                        inventory_embed.add_field(
                            name=f"{item_emoji}{item_name} - x{item_amount}",
                            value=(
                                f'**{item_description}** \n Price: `{int(item_price):,}` \n Type: `{item_type}` \n '
                                f'ID: `{item_id}` \n Damage: `{item_damage}` \n '
                                f'Crit Chance: `{item_crit_chance}` \n '
                                f'Ammo: {ammo_emoji}`{ammo_name}` \n Ammo in Inventory: x`{ammo_amount}`'
                            ),
                            inline=False
                        )

                    if item_type == "Chest":
                        item_description = await db_manager.get_chest_description(item_id)
                    else:
                        item_description = await db_manager.get_basic_item_description(item_id)
                    isequippable = await db_manager.is_basic_item_equipable(item_id)
                    if isequippable:
                        inventory_embed.add_field(
                            name=f"{item_emoji}{item_name} - x{item_amount}",
                            value=f'**{item_description}** \n Price: `{int(item_price):,}` \n Type: `{item_type}` \n ID | `{item_id}` \n Equipped: {"Yes" if is_equipped else "No"}',
                            inline=False
                        )
                        
                        
                    elif item_type == "Pet":
                        pet_name = await db_manager.get_pet_name(ctx.author.id, item_id)
                        if pet_name != item_name:
                            inventory_embed.add_field(
                                name=f"{item_emoji}{pet_name} (`{item_name}`) - x{item_amount}",
                                value=f'**{item_description}** \n Price: `{int(item_price):,}` \n Type: `{item_type}` \n ID | `{item_id}`',
                                inline=False
                            )
                        else:
                            inventory_embed.add_field(
                                name=f"{item_emoji}{item_name} - x{item_amount}",
                                value=f'**{item_description}** \n Price: `{int(item_price):,}` \n Type: `{item_type}` \n ID | `{item_id}`',
                                inline=False
                            )
                    else:
                        inventory_embed.add_field(
                            name=f"{item_emoji}{item_name} - x{item_amount}",
                            value=f'**{item_description}** \n Price: `{int(item_price):,}` \n Type: `{item_type}` \n ID | `{item_id}`',
                            inline=False
                        )

                embeds.append(inventory_embed)

            return embeds


        # Create a list of embeds with 5 items per embed
        embeds = await create_embeds(inventory_items)

        class Select(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="All"),
                    discord.SelectOption(label="Collectable"),
                    discord.SelectOption(label="Sellable"),
                    discord.SelectOption(label="Consumable"),
                    discord.SelectOption(label="Material"),
                    discord.SelectOption(label="Tool"),
                    discord.SelectOption(label="Weapon"),
                    discord.SelectOption(label="Armor"),
                    discord.SelectOption(label="Badge"),
                    discord.SelectOption(label="Pet"),
                    discord.SelectOption(label="Misc"),
                ]
                super().__init__(placeholder="Select an option", max_values=11, min_values=1, options=options)

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
                except IndexError:
                    await interaction.response.defer()

        class InventoryButton(discord.ui.View):
            def __init__(self, current_page, embeds, **kwargs):
                super().__init__(**kwargs)
                self.current_page = current_page
                self.embeds = embeds
                self.add_item(Select())

            @discord.ui.button(label="⋘", style=discord.ButtonStyle.green, row=1)
            async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = 0
                await interaction.response.defer()
                await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label="≪", style=discord.ButtonStyle.green, row=1)
            async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page > 0:
                    self.current_page -= 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label="≫", style=discord.ButtonStyle.green, row=1)
            async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.current_page < len(self.embeds) - 1:
                    self.current_page += 1
                    await interaction.response.defer()
                    await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label="⋙", style=discord.ButtonStyle.green, row=1)
            async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = len(self.embeds) - 1
                await interaction.response.defer()
                await interaction.message.edit(embed=self.embeds[self.current_page])

            @discord.ui.button(label="Close", style=discord.ButtonStyle.red, row=1)
            async def close_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.message.delete()

        view = InventoryButton(current_page=0, embeds=embeds)
        await ctx.send(embed=embeds[0], view=view)


    #command to create a new item in the database item table, using the create_streamer_item function from helpers\db_manager.py
    #`streamer_prefix` varchar(20) NOT NULL,
    #`item_id` varchar(20) NOT NULL,
    #`item_name` varchar NOT NULL,
    #`item_emoji` varchar(255) NOT NULL,
    #`item_rarity` varchar(255) NOT NULL,


    #@commands.hybrid_group(
    #    name="quest",
    #    description="Quest Commands",
    #)
    #async def quest(self, ctx):
    #    if ctx.invoked_subcommand is None:
    #        await ctx.send('Invalid quest command passed...')
#
#
    #@quest.command(
    #    name="board",
    #    description="This command will show the quest board.",
    #)
    #async def questboard(self, ctx: Context):
    #    # Get all the quests from the database
    #    quests = await db_manager.get_quests_on_board()
    #    if quests == []:
    #        await ctx.send("There are no quests on the board.")
    #        return
#
    #    # Calculate number of pages based on number of quests
    #    num_pages = (len(quests) // 5) + (1 if len(quests) % 5 > 0 else 0)
#
    #    current_page = 0
#
    #    # Create a function to generate embeds from a list of quests
    #    async def create_embeds(quest_list):
    #        num_pages = (len(quest_list) // 5) + (1 if len(quest_list) % 5 > 0 else 0)
    #        embeds = []
#
    #        for i in range(num_pages):
    #            start_idx = i * 5
    #            end_idx = start_idx + 5
    #            quest_embed = discord.Embed(
    #                title="Quest Board",
    #                description=f"Quests available for {ctx.author.name}. Use /questinfo <quest_id> to get more details.",
    #            )
    #            quest_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
#
    #            for quest in quest_list[start_idx:end_idx]:
    #                quest_id = quest[0]
    #                quest_name = quest[1]
    #                quest_xp = quest[3]
    #                quest_reward = quest[4]
    #                quest_reward_amount = quest[5]
    #                quest_type = quest[7]
    #                quest = quest[8]
#
    #                # Format the quest type and quest
    #                if quest_type == "collect":
    #                    quest_type = "Collect"
    #                    quest_parts = quest.split(" ")
    #                    item_id = quest_parts[1]
    #                    item_name = await db_manager.get_basic_item_name(item_id)
    #                    item_emoji = await db_manager.get_basic_item_emoji(item_id)
    #                    quest = f"**{quest_parts[0]}** {item_emoji}{item_name}"
    #
    #                elif quest_type == "kill":
    #                        quest_type = "Kill"
    #                        quest_parts = quest.split(" ")
    #                        enemy_id = quest_parts[1]
    #                        enemy_name = await db_manager.get_enemy_name(enemy_id)
    #                        enemy_emoji = await db_manager.get_enemy_emoji(enemy_id)
    #                        #clear the () and , from the enemy emoji
    #                        enemy_emoji = str(enemy_emoji)
    #                        enemy_emoji = enemy_emoji.replace("(", "")
    #                        enemy_emoji = enemy_emoji.replace(")", "")
    #                        enemy_emoji = enemy_emoji.replace(",", "")
    #                        #remove the ' on each side of the emoji
    #                        enemy_emoji = enemy_emoji.replace("'", "")
    #                        quest = f"**{quest_parts[0]}** {enemy_emoji}{enemy_name}"
#
    #                # Replace "Money" with cash emoji
    #                if quest_reward == "Money":
    #                    quest_reward = f"{cash} {quest_reward_amount}"
    #                else:
    #                    # If the reward is an item, get the item name from the database
    #                    item_name = await db_manager.get_basic_item_name(quest_reward)
    #                    item_emoji = await db_manager.get_basic_item_emoji(quest_reward)
    #                    quest_reward = f"{item_emoji}{item_name} x{quest_reward_amount}"
#
    #                quest_embed.add_field(name=f"**{quest_name}**", value=f"ID | `{quest_id}` \n **Quest**: {quest_type} {quest} \n **XP**: {quest_xp} \n **Reward**: {quest_reward} \n", inline=False)
#
    #            embeds.append(quest_embed)
#
    #        return embeds
#
#
    #    # Create a list of embeds with 5 quests per embed
    #    embeds = await create_embeds(quests)
#
    #    class QuestBoardButton(discord.ui.View):
    #        def __init__(self, current_page, embeds, **kwargs):
    #            super().__init__(**kwargs)
    #            self.current_page = current_page
    #            self.embeds = embeds
#
    #        @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
    #        async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
    #            self.current_page = 0
    #            await interaction.response.defer()
    #            await interaction.message.edit(embed=self.embeds[self.current_page])
#
    #        @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
    #        async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
    #            if self.current_page > 0:
    #                self.current_page -= 1
    #                await interaction.response.defer()
    #                await interaction.message.edit(embed=self.embeds[self.current_page])
#
    #        @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
    #        async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
    #            if self.current_page < len(self.embeds) - 1:
    #                self.current_page += 1
    #                await interaction.response.defer()
    #                await interaction.message.edit(embed=self.embeds[self.current_page])
#
    #        @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
    #        async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
    #            self.current_page = len(self.embeds) - 1
    #            await interaction.response.defer()
    #            await interaction.message.edit(embed=self.embeds[self.current_page])
#
    #    view = QuestBoardButton(current_page=0, embeds=embeds)
    #    await ctx.send(embed=embeds[0], view=view)
#
    #    #when the user clicks the check mark, add the quest to the users quest list, remove the quest from the quest board, check if the user already has the quest, and if they do, tell them they already have it, and if they dont, add it to their quest list
    #@quest.command(
    #name="info",
    #description="Get detailed information about a specific quest.",
    #)
    #async def questinfo(self, ctx: Context, quest_id: str):
    #    # Get the quest from the database
    #    quest = await db_manager.get_quest_from_id(quest_id)
    #    if quest is None:
    #        await ctx.send("That quest does not exist.")
    #        return
#
    #    quest_id, quest_name, quest_description, quest_xp, quest_reward, quest_reward_amount, quest_level_req, quest_type, quest = quest
#
    #    # Create an embed with detailed information about the quest
    #    quest_embed = discord.Embed(title=f"**{quest_name}**")
    #    quest_embed.add_field(name="ID", value=quest_id)
    #    quest_embed.add_field(name="Description", value=quest_description)
    #    quest_embed.add_field(name="XP", value=quest_xp)
    #    quest_embed.add_field(name="Reward", value=f"{quest_reward_amount} {quest_reward}")
    #    quest_embed.add_field(name="Level Requirement", value=quest_level_req)
    #    quest_embed.add_field(name="Quest Type", value=quest_type)
#
    #    await ctx.send(embed=quest_embed)
    #
    #@quest.command(
    #    name="accept",
    #    description="Accept a quest from the quest board.",
    #)
    #async def acceptquest(self, ctx: Context, quest: str):
    #    # Get the quest id from the database
    #    quest = await db_manager.get_quest_from_id(quest)
    #    if quest is None:
    #        await ctx.send("That quest does not exist.")
    #        return
#
    #    quest_id = str(quest)
#
    #    # Get the user id
    #    user_id = ctx.message.author.id
    #    user_id = str(user_id)
#
    #    # Check if the user already has the quest
    #    user_has_quest = await db_manager.check_user_has_quest(user_id, quest_id)
#
    #    # Check if the user has any quest
    #    user_has_any_quest = await db_manager.check_user_has_any_quest(user_id)
#
    #    isCompleted = await db_manager.check_quest_completed(user_id, quest_id)
#
    #    # Check if the user meets the level requirements
    #    user_level = await db_manager.get_level(user_id)
    #    level_req = await db_manager.get_quest_level_required(quest_id)
#
    #    # Convert them to integers
    #    user_level = int(user_level[0])
    #    level_req = int(level_req)
#
    #    if user_level < level_req:
    #        await ctx.send("You do not meet the level requirements for this quest!")
    #    elif isCompleted == True:
    #        await ctx.send("You already completed this quest!")
    #    elif user_has_quest == True:
    #        await ctx.send("You already have this quest!")
    #    elif user_has_any_quest == True:
    #        await ctx.send("You already have a quest! Abandon or complete your current quest to get a new one!")
    #    else:
    #        # If the user doesn't have the quest, add it to their quest list
    #        await db_manager.give_user_quest(user_id, quest_id)
    #        await db_manager.create_quest_progress(user_id, quest_id)
    #        await ctx.send("Quest added to your quest list!")
    #        # Remove the quest from the quest board
    #        # await db_manager.remove_quest_from_board(quest_id)
#
    #
    ##abandon quest hybrid command
    #@quest.command(
    #    name="abandon",
    #    description="Abandon your current quest",
    #)
    #async def abandonquest(self, ctx: Context):
    #    await db_manager.remove_quest_from_user(ctx.author.id)
    #    await ctx.send("You have Abandoned your current quest, if you want to get a new one please check the quest board")



    #ANCHOR - shop command that shows the shop
    @commands.hybrid_command(
        name="shop",
        description="view the shop.",
    )
    async def shop(self, ctx: Context):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return
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
                # Get the reset time
                resetTime = self.shop_reset.next_iteration
                if resetTime is None:
                    #print("Error: next_iteration returned None")
                    shop_embed = discord.Embed(
                    title="Shop",
                    description=f"Commands: \n **Buy**: `/buy iron_sword 1`. \n \n **Shop Restock Time**: `8hr` \n \n"
                    )
                else:
                    resetTime = str(resetTime)
                    resetTime = resetTime[:19]

                    # Parse the reset time string into a datetime object
                    resetTime = datetime.datetime.strptime(resetTime, '%Y-%m-%d %H:%M:%S')

                    # Make the datetime object timezone-aware (UTC)
                    resetTime = resetTime.replace(tzinfo=pytz.UTC)

                    # Convert the datetime object to Eastern Standard Time
                    est = pytz.timezone('US/Eastern')
                    resetTime = resetTime.astimezone(est)

                    # Convert the datetime object to a Unix timestamp
                    resetTime_unix = int(resetTime.timestamp())

                    shop_embed = discord.Embed(
                        title="Shop",
                        description=f"Shop Resets: <t:{resetTime_unix}:t> (<t:{resetTime_unix}:R>) \n \n"
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
                        shop_embed.add_field(name=f"{item_emoji}{item_name} - {cash}{int(item_price):,}", value=f'**{item_description}** \n ID | `{item_id}`', inline=False)
                    else:
                        #get the item effect
                        shop_embed.add_field(name=f"{item_emoji}{item_name} - {cash}{int(item_price):,}", value=f'**{item_description}** \n ID | `{item_id}`', inline=False)
                embeds.append(shop_embed)

            return embeds

        # Create a list of embeds with 5 items per embed
        embeds = await create_embeds(shopitems)

        class Select(discord.ui.Select):
            def __init__(self):
                options=[
                    discord.SelectOption(label="All"),
                    discord.SelectOption(label="Collectable"),
                    discord.SelectOption(label="Sellable"),
                    discord.SelectOption(label="Consumable"),
                    discord.SelectOption(label="Material"),
                    discord.SelectOption(label="Tool"),
                    discord.SelectOption(label="Weapon"),
                    discord.SelectOption(label="Armor"),
                    discord.SelectOption(label="Badge"),
                    discord.SelectOption(label="Pet"),
                    discord.SelectOption(label="Misc"),
                ]
                super().__init__(placeholder="Select an option", max_values=11, min_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                selected_item_type = self.values[0]

                if selected_item_type == "All":
                    filtered_items = shopitems
                else:
                    filtered_items = [item for item in shopitems if item[5] == selected_item_type]

                filtered_embeds = await create_embeds(filtered_items)
                new_view = ShopButton(current_page=0, embeds=filtered_embeds)
                try:
                    await interaction.response.edit_message(embed=filtered_embeds[0], view=new_view)
                #catch IndexError
                except(IndexError):
                    await interaction.response.defer()

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
    #add options for items to buy

    async def buy(self, ctx: Context, item: str, amount: int):
        shopitems = await db_manager.display_shop_items()
        """
        This command will buy an item from the shop.

        :param ctx: The context in which the command was called.
        :param item_id: The ID of the item that should be bought.
        :param amount: The amount of the item that should be bought.
        """
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return
        user_id = ctx.message.author.id
        user_profile = await db_manager.profile(user_id)
        user_money = int(user_profile[2])
        user_health = user_profile[3]
        isStreamer = user_profile[4]
        # Get the user's xp and level
        user_xp = user_profile[12]
        user_level = user_profile[13]
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
                    if item_type == "Pet":
                        #check if the the item_id is already in the users inventory
                        user_inventory = await db_manager.view_inventory(user_id)
                        for i in user_inventory:
                            if item in i:
                                await ctx.send(f"You already have this Pet!")
                                return
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
                    message = await ctx.send(f"Are you sure you want to buy `{amount}` of `{item_name}` for **{cash}{total_price:,}**")
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
                            await ctx.send(f"You bought `{amount}` of `{item_name}` for **{cash}{total_price:,}**")
                        return
                else:
                    item_name = await db_manager.get_basic_item_name(item)
                    await ctx.send(f"You don't have enough bucks to buy `{amount}` of `{item_name}`.")
                    return
        await ctx.send(f"Item doesn't exist in the shop.")

    @buy.autocomplete("item")
    async def buy_autocomplete(self, ctx: Context, argument):
        shopitems = await db_manager.display_shop_items()
        choices = []
        for item in shopitems:
            if argument.lower() in item[1].lower():
                if item[5] == 'Pet':
                    rarity = await db_manager.get_basic_item_rarity(item[0])
                    item_name = f"{rarity} {item[1]} ({cash}{int(item[2]):,})"
                else:
                    item_name = f"{item[1]} ({cash}{int(item[2]):,})"
                choices.append(app_commands.Choice(name=item_name, value=item[0]))
        return choices[:25]
    #sell command for selling items, multiple of the same item can be sold, and the user can sell multiple items at once, then removes them from the users inventory, and adds the price to the users money
    @commands.hybrid_command(
        name="sell",
        description="This command will sell an item from your inventory.",
    )
    async def sell(self, ctx: Context, item: str, amount: int):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return

        """
        This command will sell an item from your inventory.

        :param ctx: The context in which the command was called.
        :param item_id: The ID of the item that should be sold.
        :param amount: The amount of the item that should be sold.
        """
        user_id = ctx.message.author.id
        user_profile = await db_manager.profile(user_id)
        user_money = int(user_profile[2])
        user_health = user_profile[3]
        isStreamer = user_profile[4]
        # Get the user's xp and level
        user_xp = user_profile[12]
        user_level = user_profile[13]
        # Check if the item exists in the user's inventory
        user_inventory = await db_manager.view_inventory(user_id)
        for i in user_inventory:
            if item == i[1]:
                # Check if it's equipped
                if i[9]:
                    await ctx.send(f"You can't sell an equipped item!, unequip it first with `/unequip {item}`")
                    return
                if i[7] == 'Collectable':
                    await ctx.send(f"You can't sell a collectable!")
                    return
                # Check if the user has enough of the item
                item_amount = int(i[6])
                if item_amount >= amount:
                    item_price = int(i[3])
                    total_price = item_price * amount
                    # Remove the item from the user's inventory
                    await db_manager.remove_item_from_inventory(user_id, item, amount)
                    item_emoji = i[4]
                    # Add the price to the user's money
                    await db_manager.add_money(user_id, total_price)
                    await ctx.send(f"You sold {amount} **{item_emoji}{i[2]}** for **{total_price:,}**")
                    return
                else:
                    await ctx.send(f"You don't have enough **{item_emoji}{i[2]}** to sell `{amount}`.")
                    return
        await ctx.send(f"Item doesn't exist in your inventory.")

    @sell.autocomplete("item")
    async def sell_autocomplete(self, ctx: discord.Interaction, argument):
        #print(argument)
        user_id = ctx.user.id
        user_inventory = await db_manager.view_inventory(user_id)
        #if the item type is a pet
        choices = []
        for item in user_inventory:
            if argument.lower() in item[2].lower():
                    pet_name = await db_manager.get_pet_name(item[0], item[1])
                    rarity = await db_manager.get_basic_item_rarity(item[1])
                    item_amount_in_inventory = await db_manager.get_item_amount_from_inventory(user_id, item[1])
                    if item[7] == "Pet":
                        item_name = f"{rarity} {pet_name if item[7] == 'Pet' else item[2]} ({cash}{int(item[3]):,}) (x{item_amount_in_inventory})"
                        choices.append(app_commands.Choice(name=item_name, value=item[1]))
                    elif item[5] == 'Collectable':
                        #not for sale
                        continue
                    else:
                        item_name = f"{item[2]} ({cash}{int(item[3]):,}) (x{item_amount_in_inventory})"
                        choices.append(app_commands.Choice(name=item_name, value=item[1]))
        return choices[:25]

    @commands.hybrid_command(
        name="sellall",
        description="This command will sell all items from your inventory.",
    )
    async def sellall(self, ctx: Context):
        checkuser = await db_manager.check_user(ctx.author.id)
        print(f"Check user result: {checkuser}")
        if checkuser in [None, False, [], "None", 0]:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return

        # Step 1: Retrieve the user's inventory
        user_id = ctx.author.id
        print(f"Retrieving inventory for user: {user_id}")
        user_inventory = await db_manager.view_inventory(user_id)
        print(f"User inventory: {user_inventory}")

        # Step 2: Filter out sellable items
        sellable_items = [
            item for item in user_inventory if item[7] == 'Sellable'  # item_type is at index 7
        ]
        print(f"Sellable items: {sellable_items}")

        if not sellable_items:
            embed = discord.Embed(
                title="Sell Items",
                description="You have no sellable items in your inventory.",
            )
            await ctx.send(embed=embed)
            return

        # Step 3: Calculate the total price for all sellable items
        total_price = 0
        for item in sellable_items:
            total_price += item[6] * int(item[3])  # item_amount is at index 6 and item_sell_price is at index 3
        print(f"Total price calculated: {total_price}")

        # Step 4: Remove the sold items from the user's inventory
        for item in sellable_items:
            await db_manager.remove_item_from_inventory(user_id, item[1], item[6])  # item_id is at index 0 and item_amount is at index 6
            print(f"Removed item from inventory: {item}")

        # Step 5: Add the calculated amount to the user's balance
        await db_manager.add_money(user_id, total_price)
        print(f"Added money to user balance: {total_price}")

        # Step 6: Send an embed message with the sale summary
        embed = discord.Embed(
            title="Items Sold!",
            description="You sold all your sellable items.",
        )

        for item in sellable_items:
            item_name = item[2]  # item_name is at index 2
            item_emoji = item[4]  # item_emoji is at index 4
            item_total_value = item[6] * int(item[3])  # item_amount is at index 6 and item_sell_price is at index 3
            embed.add_field(name=f"x{item[6]} {item_emoji}{item_name} - {cash}{item_total_value}", value=f"", inline=False)
            print(f"Added field to embed for item: {item}")
            
        money = await db_manager.get_money(user_id)    
        money = int(str(money).replace("(", "").replace(")", "").replace(",", ""))
        embed.add_field(name=f"**{cash}{total_price}**", value=f"You now have **{cash}{money}**", inline=False)
        await ctx.send(embed=embed)
        print(f"Embed sent with total price: {total_price}")
#view a users profile using the view_profile function from helpers\db_manager.py
    @commands.hybrid_command(
        name="profile",
        description="This command will view your profile.",
        aliases=["p", "prof", "pfp"],
    )
    async def profile(self, ctx: Context, user: discord.User = None):
        """
        This command will view your profile.
    
        :param ctx: The context in which the command was called.
        """
        if user is None:
            user = ctx.author
    
        user_id = user.id
        user_profile = await db_manager.profile(user_id)
        if user_profile is None:
            if user_id == ctx.author.id:
                await ctx.send("you arent a sigma yet, use /start", ephemeral=True)
            else:
                await ctx.send(f"{user.name} isnt a sigma yet, tell them to use /start", ephemeral=True)
            return
    
        user_id = user_profile[0]
        user_money = user_profile[2]
        user_health = user_profile[3]
        isStreamer = user_profile[4]
        # Get the user's xp and level
        user_xp = user_profile[12]
        user_level = user_profile[13]
        user_quest = user_profile[14]
        user_twitch_id = user_profile[15]
        user_twitch_name = user_profile[16]
        player_title = user_profile[27]
        job_id = user_profile[28]
        locked = user_profile[35]
    
        # Get the xp needed for the next level
        xp_needed = await db_manager.xp_needed(user_id)
        # Convert the xp needed to a string
        xp_needed = str(xp_needed)
        
        print(f"User ID: {user_id}")
        print(f"Users Wallet: {user_money}")
        print(f"User Health: {user_health}")
        print(f"Is Streamer: {isStreamer}")
        print(f"User XP: {user_xp}")
        print(f"XP Needed: {xp_needed}")
        print(f"User Level: {user_level}")
        print(f"User Quest: {user_quest}")
        print(f"User Twitch ID: {user_twitch_id}")
        print(f"User Twitch Name: {user_twitch_name}")
    
        user_items = await db_manager.view_inventory(user_id)
        embed = discord.Embed(title="Profile", description=f"{user.mention}'s Profile.")
        isalive = await db_manager.is_alive(user_id)
        if user_health <= 0:
            #check if the user is marked as dead
            isalive = await db_manager.is_alive(user_id)
            if isalive == True:
                #if they are, mark them as dead
                await db_manager.set_dead(user_id)
            revivetimestamp = await db_manager.get_revival_timestamp(user_id)
            embed.add_field(name="Health", value=f"0 (Dead) Revive: <t:{revivetimestamp}:R>", inline=True)
        elif isalive == False:
            revivetimestamp = await db_manager.get_revival_timestamp(user_id)
            embed.add_field(name="Health", value=f"0 (Dead) Revive: <t:{revivetimestamp}:R>", inline=True)
        else:
            embed.add_field(name="Health", value=f"{user_health}", inline=True)
        net_dict = await bank.get_user_net_worth(user)
        profile = await db_manager.profile(user_id)
        locked = profile[34] 
        if locked == True:
            embed.add_field(name="Wallet", value=f"{cash}{int(user_money):,}<:119_Padlock_Locked:1246917790451896393>", inline=True)
        else:
            embed.add_field(name="Wallet", value=f"{cash}{int(user_money):,}", inline=True)
        
        #bank
        bank_balance = await db_manager.get_bank_balance(user_id)
        embed.add_field(name="Bank", value=f"{cash}{int(bank_balance):,}", inline=True)
        #add xp and level
        embed.add_field(name="XP", value=f"{user_xp} / {xp_needed}", inline=True)
        embed.add_field(name="Level", value=f"{user_level}", inline=True)
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

        user_id = user.id if user else ctx.author.id
        print(f"Fetching ranks for user_id: {user_id}")
        most_money_rank, highest_level_rank = await db_manager.get_user_ranks(user_id)
        if most_money_rank is not None or highest_level_rank is not None:
            embed.add_field(name="Most Money Rank", value=most_money_rank if most_money_rank is not None else "Not ranked", inline=True)
            embed.add_field(name="Highest Level Rank", value=highest_level_rank if highest_level_rank is not None else "Not ranked", inline=True)

        inventory_items = await db_manager.view_inventory(user_id)

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

        if job_id is None or job_id == 0 or job_id == "None":
            embed.add_field(name="Current Job", value="`You currently have no job. see the board to get one.`", inline=False)
        else:
            job_name = await db_manager.get_job_name_from_id(job_id)
            job_description = await db_manager.get_job_description_from_id(job_id)
            job_icon = await db_manager.get_job_icon_from_id(job_id)
            embed.add_field(name="Job", value=f"{job_icon}**{job_name}**", inline=False)
        embed.set_thumbnail(url=user.avatar.url)
        if isStreamer == 1:
            isStreamer = "Yes"
        elif isStreamer == 0:
            isStreamer = "No"
        if user_twitch_id == None or user_twitch_id == "" or user_twitch_id == "None":
            user_twitch_id = "Not Connected"
        embed.set_footer(text=f"User ID: {user_id} | Twitch: {user_twitch_id} | Streamer: {isStreamer}")

        async def display_inventory(ctx: Context, user):
            # Get user inventory items from the database
            inventory_items = await db_manager.view_inventory(user.id)
            if inventory_items == []:
                await ctx.send(f"{user.name} has no items in their inventory", ephemeral=True)
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
                        item_projectile = json.loads(item[12])
                        item_description = await db_manager.get_basic_item_description(item_id)

                        isEquippable = await db_manager.is_basic_item_equipable(item_id)
                        if isEquippable == True:
                            inventory_embed.add_field(name=f"{item_emoji}{item_name} - x{item_amount}", value=f'**{item_description}** \n Type: `{item_type}` \n ID | `{item_id}` \n Equipped: {"Yes" if is_equipped else "No"}', inline=False)
                        else:
                            inventory_embed.add_field(name=f"{item_emoji}{item_name} - x{item_amount}", value=f'**{item_description}** \n Type: `{item_type}` \n ID | `{item_id}`', inline=False)

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
                        
                    #close button
                    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, row=1)
                    async def on_close(self, interaction: discord.Interaction, button: discord.ui.Button):
                        await interaction.response.defer()
                        await interaction.message.delete()
                        self.stop()

            view = InventoryButton(current_page=0, embeds=embeds)
            await ctx.send(embed=embeds[0], view=view, ephemeral=True)

        async def display_pets(ctx: Context, user):
            # Get user inventory items from the database
            inventory_items = await db_manager.view_inventory(user.id)
            if inventory_items == []:
                await ctx.send(f"{user.name} has no items in their inventory", ephemeral=True)
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
                    
                #close button
                @discord.ui.button(label="Close", style=discord.ButtonStyle.red, row=1)
                async def on_close(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.defer()
                    await interaction.message.delete()
                    self.stop()

            view = PetButton(current_page=0, embeds=embeds)
            try:
                await ctx.send(embed=embeds[0], view=view, ephemeral=True)
            except(IndexError):
                await ctx.send(content=f"{user.name} has no pets", ephemeral=True)

        async def display_stats(ctx: Context, user):
            # Get user stats from the database
            user_profile = await db_manager.profile(user.id)
            if user_profile is None:
                await ctx.send(f"{user.name} is not in the database yet.", ephemeral=True)
                return

            # Create an embed for the stats
            stats_embed = discord.Embed(title="Stats", description=f"{user.name}'s Stats")
            stats_embed.add_field(name="Luck", value=user_profile[26])
            stats_embed.add_field(name="Shifts Worked", value=user_profile[32])
            stats_embed.add_field(name="Bonus %", value=str(user_profile[35]) + "%")

            await ctx.send(embed=stats_embed)

        async def display_active_items(ctx: Context, user):
            # Get user active items from the database
            active_items = await db_manager.view_timed_items(user.id)
            est_min_datetime = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC).astimezone(pytz.timezone('US/Eastern'))
            # Convert the datetime object to a Unix timestamp
            est_min_unix = int(est_min_datetime.timestamp())
            item_info = defaultdict(lambda: {"count": 0, "latest_expire": est_min_unix})

            if active_items:
                for item in active_items:
                    # get the item name
                    item_name = await db_manager.get_basic_item_name(item[0])
                    # get the item emoji
                    item_emoji = await db_manager.get_basic_item_emoji(item[0])
                    # get the item expire time
                    expire_time = item[3]
                    expiration_datetime = datetime.datetime.strptime(expire_time, '%Y-%m-%d %H:%M:%S')
                    # Make the datetime object timezone-aware (UTC)
                    expiration_datetime = expiration_datetime.replace(tzinfo=pytz.UTC)

                    # Convert the datetime object to Eastern Standard Time
                    est = pytz.timezone('US/Eastern')
                    expiration_datetime = expiration_datetime.astimezone(est)

                    # Convert the datetime object to a Unix timestamp
                    expiration_unix = int(expiration_datetime.timestamp())

                    # Update item_info
                    item_key = f"{item_emoji}{item_name}"
                    item_info[item_key]["count"] += 1
                    item_info[item_key]["latest_expire"] = max(item_info[item_key]["latest_expire"], expiration_unix)

            # Display information
            # Initialize an empty string to hold all the item information
            active_items_str = ""

            # Loop through all the items and add their information to the string
            for item_key, info in item_info.items():
                active_items_str += f"**{item_key} x{info['count']}** - Latest expiration: <t:{info['latest_expire']}:R>\n"

            # Create a list of embeds with 5 items per embed
            embeds = []
            for i in range(0, len(active_items_str), 5):
                embed = discord.Embed()
                embed.add_field(name="Active Items", value=active_items_str[i:i+5], inline=False)
                embeds.append(embed)

            class ActiveItemsButton(discord.ui.View):
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
                    
                #close button
                @discord.ui.button(label="Close", style=discord.ButtonStyle.red, row=1)
                async def on_close(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.defer()
                    await interaction.message.delete()
                    self.stop()

            # If there are multiple pages, add the buttons
            if len(embeds) > 1:
                view = ActiveItemsButton(current_page=0, embeds=embeds)
                await ctx.send(embed=embeds[0], view=view, ephemeral=True)
            elif len(embeds) == 0:
                await ctx.send(content=f"{user.name} has no active items.", ephemeral=True)
            else:
                await ctx.send(embed=embeds[0], ephemeral=True)

        class ProfileView(discord.ui.View):
            def __init__(self, ctx):
                super().__init__()
                self.ctx = ctx
                self.user = user

            @discord.ui.button(label="Active Items", custom_id="profile_active_items")
            async def active_items_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await display_active_items(self.ctx, self.user)
                await interaction.response.defer()

            @discord.ui.button(label="Inventory", custom_id="profile_inv")
            async def inv_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await display_inventory(self.ctx, self.user)
                await interaction.response.defer()

            @discord.ui.button(label="Pets", custom_id="profile_pets")
            async def pets_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                # Handle the "Pets" button click here.
                await display_pets(self.ctx, self.user)
                await interaction.response.defer()

            @discord.ui.button(label="Stats", custom_id="profile_stats")
            async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await display_stats(self.ctx, self.user)
                await interaction.response.defer()
                
            #close button
            @discord.ui.button(label="Close", style=discord.ButtonStyle.red, row=1)
            async def on_close(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                await interaction.message.delete()
                self.stop()

        view = ProfileView(ctx)
        await ctx.send(embed=embed, view=view)

    #hybrid command to start the user on their journy, this will create a profile for the user using the profile function from helpers\db_manager.py and give them 200 bucks
    @commands.hybrid_command(
        name="start",
        description="This command will make you a sigma.",
    )
    async def start(self, ctx: Context):
        """
        This command will make you a sigma.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        #check if the user is in the database
        userExist = await db_manager.check_user(user_id)
        if userExist == None or userExist == []:
            await db_manager.get_user(user_id, ctx.author.name)
            #equip the iron sword
            await ctx.send(f"You are now a sigma")
        else:
            await ctx.send("You're already a sigma")

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

            elif effect == "bonus":
                if effect_add_or_minus == "+":
                    await db_manager.add_percent_bonus(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you +`{effect_amount}` bonus."
                elif effect_add_or_minus == "-":
                    await db_manager.remove_percent_bonus(user_id, effect_amount)
                    message = f"You equipped `{item_name}`. It gave you -`{effect_amount}` bonus."

            await db_manager.equip_item(user_id, item)
            await ctx.send(message)
        else:
            await ctx.send(f"that is not equippable.")

    @equip.autocomplete("item")
    async def equip_autocomplete(self, ctx: discord.Interaction, argument):
        user_id = ctx.user.id
        user_inventory = await db_manager.view_inventory(user_id)
        choices = []
        for item in user_inventory:
            if argument.lower() in item[2].lower():
                isEquippable = await db_manager.is_basic_item_equipable(item[1])
                if isEquippable == 1 or isEquippable == True:
                    choices.append(app_commands.Choice(name=f"{item[2]}", value=item[1]))
        return choices[:25]

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

            #bonus
            elif effect == "bonus":
                if effect_add_or_minus == "+":
                    await db_manager.remove_percent_bonus(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you -`{effect_amount}` bonus."
                elif effect_add_or_minus == "-":
                    await db_manager.add_percent_bonus(user_id, effect_amount)
                    message = f"You unequipped `{item_name}`. It gave you +`{effect_amount}` bonus."

            await db_manager.unequip_item(user_id, item)
            await ctx.send(message)
        else:
            await ctx.send(f"`{item_name}` is not equipped.")

    @unequip.autocomplete("item")
    async def unequip_autocomplete(self, ctx: discord.Interaction, argument):
        user_id = ctx.user.id
        user_items = await db_manager.view_inventory(user_id)
        choices = []
        for item in user_items:
            isEquipped = await db_manager.is_item_equipped(user_id, item[1])
            if isEquipped == 1 or isEquipped == True:
                choices.append(app_commands.Choice(name=item[2], value=item[1]))
        return choices[:25]
    #hybrid command to battle a monster
    
    @commands.cooldown(1, 8, commands.BucketType.user)
    @commands.hybrid_command(
        name="fight",
        description="Fight a user!",
    )
    async def fight(self, ctx: Context, target: discord.Member):
        #check if the user is in a battle
        #check if the user is in a battle
        user_exists = await db_manager.check_user(ctx.author.id)
        if user_exists == None:
            await ctx.send("you're not a sigma yet, please use the `/start`")
            return
        user_exists = await db_manager.check_user(target.id)
        if user_exists == None:
            await ctx.send("This user does not exist lol!, tell them to do /start to be a sigma!")
            return
        #check if the user is dead
        user_is_alive = await db_manager.is_alive(ctx.author.id)
        if user_is_alive == False:
            await ctx.send("You are dead! wait to respawn! or use an item to revive!")
            return
        #check if the user is dead
        user_is_alive = await    db_manager.is_alive(target.id)
        if user_is_alive == False:
            await ctx.send("This user is dead! wait till they respawn! or they use an item to revive!")
            return
        #attack the user
        await battle.userattack(ctx, target)

    #mine command
    #command cooldown of 20 seconds
    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.hybrid_command(
        name="search",
        description="Search for cool stuff",
    )
    async def search(self, ctx: Context):
        userExist = await db_manager.check_user(ctx.author.id)
        if userExist == None or userExist == []:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.search.reset_cooldown(ctx)
            return
        await search.search(ctx)
        await ctx.defer()

    @commands.cooldown(1, 40, commands.BucketType.user)
    @commands.hybrid_command(
        name="beg",
        description="beg for money",
    )
    async def beg(self, ctx: Context):
        userExist = await db_manager.check_user(ctx.author.id)
        if userExist == None or userExist == []:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.beg.reset_cooldown(ctx)
            return
        await beg.beg(ctx)

    #hunt command
    #command cooldown of 20 seconds
    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.hybrid_command(
        name="hunt",
        description="Hunt for animals",
    )
    async def hunt(self, ctx: Context):
        userExist = await db_manager.check_user(ctx.author.id)
        if userExist == None or userExist == []:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.hunt.reset_cooldown(ctx)
            return
        await hunt.hunt(ctx)
        await ctx.defer()

    #ANCHOR use command
    #a cooldown of 2 minutes
    # Function to handle using chest items
    async def use_chest(self, ctx: Context, item: str, user_id: int, luck: int):
        outcome_phrases = [
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

        def choose_items_based_on_chance(items_with_chances: List[Tuple], luck: int):
            chosen_items = []
            for item, chance in items_with_chances:
                adjusted_chance = chance + (luck / 100)
                if random.uniform(0, 100) <= adjusted_chance:
                    chosen_items.append(item)
            return chosen_items

        chest_contents = await db_manager.get_chest_contents(item)
        chest_contents = [
            (
                {'item_id': item[1], 'item_amount': item[2]},
                item[3]
            ) for item in chest_contents
        ]

        chosen_items = choose_items_based_on_chance(chest_contents, luck)

        embed = discord.Embed(title="Chest Opened!", color=discord.Color.green())

        if chosen_items:
            for chosen_item in chosen_items:
                await db_manager.add_item_to_inventory(ctx.author.id, chosen_item['item_id'], chosen_item['item_amount'])
                item_name = await db_manager.get_basic_item_name(chosen_item['item_id'])
                item_emoji = await db_manager.get_basic_item_emoji(chosen_item['item_id'])
                embed.add_field(name=item_name, value=f"{item_emoji} - {chosen_item['item_amount']}", inline=False)
            embed.description = random.choice(outcome_phrases)
        else:
            chest_name = await db_manager.get_chest_name(item)
            embed.description = f"It seems {chest_name} ended up being empty!"

        await ctx.send(embed=embed)

    # Function to handle using pet items
    async def use_pet_item(self, ctx: Context, item: str, user_id: int, item_emoji: str, item_name: str):
        pets = await db_manager.get_users_pets(ctx.author.id)
        if not pets:
            await ctx.send('You do not own any pets.')
            return
        view = PetSelectView(pets, ctx.author, self.bot, item)
        await view.prepare()
        message = await ctx.send(f'Which Pet do You want to use {item_emoji}{item_name} on?', view=view)
        view.message = message

    # Function to handle using timed items
    async def use_timed_item(self, ctx: Context, item: str, user_id: int, item_emoji: str, item_name: str):
        item_effect = await db_manager.get_basic_item_effect(item)
        await db_manager.add_timed_item(user_id, item, item_effect)

        item_effect_parts = item_effect.split(" ")
        item_effect_type = item_effect_parts[0]
        plus_or_minus = item_effect_parts[1]
        item_effect_amount = item_effect_parts[2]
        item_effect_time = item_effect_parts[3] if len(item_effect_parts) > 3 else "0"

        await self.process_and_send_item_quote(ctx, item, item_emoji, item_name, {
            "item_effect_type": item_effect_type,
            "plus_or_minus": plus_or_minus,
            "effect_amount": item_effect_amount,
            "item_effect_time": item_effect_time
        })

    async def process_and_send_item_quote(self, ctx: Context, item: str, item_emoji: str, item_name: str, additional_placeholders: dict):
        # Get the item's quotes
        item_quotes_data = await db_manager.get_item_quotes(item)
        item_quotes = [quote[1] for quote in item_quotes_data]
        # Pick a random quote
        prompt = random.choice(item_quotes)
        # Replace placeholders
        placeholders = {
            "{user}": ctx.author.mention,
            "{item}": f"{item_emoji}{item_name}"
        }
        placeholders.update(additional_placeholders)

        for placeholder, replacement in placeholders.items():
            if replacement is not None:
                prompt = prompt.replace(f"{{{placeholder}}}", replacement)

        # Send the message
        await ctx.send(prompt)

    # Function to handle using revive items
    async def use_revive_item(self, ctx: Context, item: str, user_id: int, item_emoji: str, item_name: str):
        if await db_manager.is_alive(user_id):
            await ctx.send("You are already alive!")
            await db_manager.add_item_to_inventory(user_id, item, 1)
        else:
            await db_manager.set_alive(user_id)
            await db_manager.add_health(user_id, 100)
            await db_manager.revive_users()
            await self.process_and_send_item_quote(ctx, item, item_emoji, item_name, {})

    # Use effect item
    async def use_effect_item(self, ctx: Context, item: str, user_id: int, item_emoji: str, item_name: str):
        item_effect = await db_manager.get_basic_item_effect(item)
        item_effect_parts = item_effect.split(" ")
        item_effect_type = item_effect_parts[0]
        plus_or_minus = item_effect_parts[1]
        item_effect_amount = item_effect_parts[2]

        if item_effect_type == "heal":
            if '-' in item_effect_amount:
                min_effect, max_effect = map(int, item_effect_amount.split('-'))
                effect_amount = random.randint(min_effect, max_effect)
            else:
                effect_amount = int(item_effect_amount)

            await db_manager.add_health(user_id, effect_amount)
            # Check the user's health, if it is greater than 100, set it to 100
            user_health = await db_manager.get_health(user_id)
            if user_health > 100:
                await db_manager.set_health(user_id, 100)

        # Process and send item quotes
        await self.process_and_send_item_quote(ctx, item, item_emoji, item_name, {
            "item_effect_type": item_effect_type,
            "plus_or_minus": plus_or_minus,
            "effect_amount": str(effect_amount)
        })



    # Main use command function
    @commands.hybrid_command(
        name="use",
        description="This command will use an item.",
    )
    async def use(self, ctx: Context, item: str):
        userExist = await db_manager.check_user(ctx.author.id)
        if not userExist:
            await ctx.send("You don't have an account! Use `/start` to start your adventure!")
            await self.use.reset_cooldown(ctx)
            return

        if not await db_manager.is_item_in_inventory(ctx.author.id, item):
            await ctx.send("You don't have this item!")
            await self.use.reset_cooldown(ctx)
            return

        user_id = ctx.author.id
        isChest = await db_manager.check_chest(item)
        item_name = await db_manager.get_chest_name(item) if isChest else await db_manager.get_basic_item_name(item)
        isUsable = 1 if isChest else await db_manager.is_basic_item_usable(item)

        if isUsable:
            await db_manager.remove_item_from_inventory(user_id, item, 1)
            item_emoji = await db_manager.get_basic_item_emoji(item)
            sub_type = await db_manager.get_basic_item_sub_type(item)

            if sub_type == "Pet Item":
                await self.use_pet_item(ctx, item, user_id, item_emoji, item_name)
                return

            isTimed = await db_manager.is_timed_item(item)
            if isTimed:
                await self.use_timed_item(ctx, item, user_id, item_emoji, item_name)
                return

            item_effect = await db_manager.get_basic_item_effect(item)
            if item_effect == "None" or isChest:
                item_effect_type = "None"
                item_effect_amount = None
            else:
                item_effect = item_effect.split(" ")
                item_effect_type = item_effect[0]
                item_effect_amount = item_effect[2]

            if item_effect_type == "revive":
                await self.use_revive_item(ctx, item, user_id, item_emoji, item_name)
                return

            if item == "chest" or item == "pet_chest":
                luck = await db_manager.get_luck(user_id)
                await self.use_chest(ctx, item, user_id, luck)
                return

            if item_effect_type == "None":
                await ctx.send(f"You used `{item_name}`!")
            else:
                self.use_effect_item(ctx, item, user_id, item_emoji, item_name)
        else:
            await ctx.send(f"`{item_name}` is not usable.")

    @use.autocomplete("item")
    async def use_autocomplete(self, ctx: discord.Interaction, argument):
        user_id = ctx.user.id
        user_inventory = await db_manager.view_inventory(user_id)
        choices = [
            app_commands.Choice(name=item[2], value=item[1])
            for item in user_inventory
            if argument.lower() in item[2].lower() and (
                await db_manager.is_basic_item_usable(item[1]) or await db_manager.check_chest(item[1])
            )
        ]
        return choices[:25]


    #explore command
    #@commands.hybrid_command(
    #        name="explore",
    #        description="Explore a structure in the current channel.",
    #        usage="explore",
    #)
    ##command cooldown of 2 minutes
    #@commands.cooldown(1, 120, commands.BucketType.user)
    #async def explore(self, ctx: commands.Context):
    #    async def handle_outcomes(ctx, random_outcomes, db_manager, embed):
    #        def choose_outcome_based_on_chance(outcomes_with_chances):
    #            total = sum(chance for _, chance in outcomes_with_chances)
    #            r = random.uniform(0, total)
    #            upto = 0
    #            for outcome, chance in outcomes_with_chances:
    #                if upto + chance >= r:
    #                    return outcome
    #                upto += chance
    #            assert False, "Shouldn't get here"
#
    #        user_luck = await db_manager.get_luck(ctx.author.id)
#
    #        random_outcomes = [
    #            (item, item["outcome_chance"] + user_luck / 100) for item in random_outcomes
    #        ]
#
    #        total_chance = sum(chance for _, chance in random_outcomes)
    #        random_outcomes = [
    #            (item, chance / total_chance) for item, chance in random_outcomes
    #        ]
#
    #        # Adjust the selection process to ensure different outcomes
    #        chosen_outcomes = []
    #        for _ in range(3):
    #            if len(random_outcomes) == 0:
    #                break  # no more outcomes to choose from
    #            chosen_outcome = choose_outcome_based_on_chance(random_outcomes)
    #            chosen_outcomes.append(chosen_outcome)
    #            random_outcomes.remove((chosen_outcome, chosen_outcome["outcome_chance"] / total_chance))  # remove the chosen outcome from the list
#
    #        # Process each chosen outcome
    #        for chosen_outcome in chosen_outcomes:
    #            outcome_dispatcher = {
    #                "item_gain": handle_item_gain,
    #                "health_gain": handle_health_gain,
    #                "money_gain": handle_money_gain,
    #                "xp_gain": handle_xp_gain,
    #            }
    #            # Call the corresponding function
    #            await outcome_dispatcher[chosen_outcome["outcome_type"]](chosen_outcome, ctx, db_manager, embed)
#
    #    async def handle_item_gain(chosen_outcome, ctx, db_manager, embed):
    #        item_id = chosen_outcome["outcome_output"]
    #        print(item_id)
    #        await db_manager.add_item_to_inventory(ctx.author.id, item_id, chosen_outcome["outcome_amount"])
    #        isChest = await db_manager.check_chest(item_id)
    #        if isChest == 1:
    #            item_name = await db_manager.get_chest_name(item_id)
    #            item_emoji = await db_manager.get_chest_icon(item_id)
    #        else:
    #            item_name = await db_manager.get_basic_item_name(item_id)
    #            item_emoji = await db_manager.get_basic_item_emoji(item_id)
    #        embed.add_field(name=":package: Item Gain", value=f"You have gained {chosen_outcome['outcome_amount']} of {item_emoji} {item_name}!", inline=False)
#
    #    async def handle_health_gain(chosen_outcome, ctx, db_manager, embed):
    #        await db_manager.add_health(ctx.author.id, chosen_outcome["outcome_amount"])
    #        embed.add_field(name=":green_heart: Health Gain", value=f"You have gained {chosen_outcome['outcome_amount']} health!", inline=False)
#
    #    async def handle_money_gain(chosen_outcome, ctx, db_manager, embed):
    #        await db_manager.add_money(ctx.author.id, chosen_outcome["outcome_amount"])
    #        embed.add_field(name=":moneybag: Money Gain", value=f"You have gained {cash}{chosen_outcome['outcome_amount']}!", inline=False)
#
    #    async def handle_xp_gain(chosen_outcome, ctx, db_manager, embed):
    #        await db_manager.add_xp(ctx.author.id, chosen_outcome["outcome_amount"])
    #        embed.add_field(name=":sparkles: XP Gain", value=f"You have gained {chosen_outcome['outcome_amount']} XP!", inline=False)
    #        # Check if the user can level up
    #        if await db_manager.can_level_up(ctx.author.id):
    #            #if the user can level up, level them up
    #            await db_manager.add_level(ctx.author.id, 1)
    #            #send a message to the channel saying the user has leveled up
    #            #get the users new level
    #            new_level = await db_manager.get_level(ctx.author.id)
    #        await ctx.send(ctx.author.name + " has leveled up! They are now level " + str(new_level) + "!")
#
    #    userExist = await db_manager.check_user(ctx.author.id)
    #    if userExist == None or userExist == []:
    #        await ctx.send("You don't have an account! Use `/start` to start your adventure!")
    #        await self.explore.reset_cooldown(ctx)
    #        return
#
    #    msg = ctx.message
#
    #    await db_manager.add_explorer_log(ctx.guild.id, ctx.author.id)
    #    all_structures = await db_manager.get_all_structures()
    #    structure = random.choice(all_structures)
    #    print(structure[0])
    #    outcomes = await db_manager.get_structure_outcomes(structure[0])
    #    structure_outcomes = []
    #    for outcome in outcomes:
    #        structure_outcomes.append({
    #            "structure_quote": outcome[1],
    #            "structure_state": outcome[2],
    #            "outcome_chance": outcome[3],
    #            "outcome_type": outcome[4],
    #            "outcome_output": outcome[5],
    #            "outcome_amount": outcome[6],
    #            "outcome_money": outcome[7],
    #            "outcome_xp": outcome[8]
    #        })
    #    luck = await db_manager.get_luck(ctx.author.id)
#
    #    outcomes = [outcome for outcome in structure_outcomes]
    #    outcomes.sort(key=lambda x: x["outcome_chance"], reverse=True)
#
    #    # Using set() to ensure unique outcomes
    #    # Get unique outcomes
    #    outcome_strs = {json.dumps(outcome) for outcome in structure_outcomes}
    #    unique_outcomes = [json.loads(outcome_str) for outcome_str in outcome_strs]
#
    #    # Selecting 3 unique random outcomes
    #    if len(unique_outcomes) < 3:
    #        random_outcomes = unique_outcomes
    #    else:
    #        random_outcomes = random.sample(unique_outcomes, 3)
#
    #    embed = discord.Embed(title=":compass: Exploration Results", description=f"> Explorer: **{ctx.author.name}**", color=discord.Color.blue())
    #    embed.set_image(url=structure[2])
    #    embed.set_footer(text="You can Explore again in 2 minutes.")
#
    #    await handle_outcomes(ctx, random_outcomes, db_manager, embed)
    #    await ctx.send(embed=embed)


    #craft command
    @commands.hybrid_command(
        name="craft",
        description="Craft an item",
    )
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
        for recipe_item_name, component, component_amount in item_recipe:
            hasone = await db_manager.check_user_has_item(ctx.author.id, component)
            item_ammount = await db_manager.get_item_amount_from_inventory(ctx.author.id, component)
            # Check if the user has the item and enough quantity of it
            if not hasone or item_ammount < component_amount:
                component_emoji = await db_manager.get_basic_item_emoji(component)
                component_name = await db_manager.get_basic_item_name(component)
                # Send a message saying the user does not have the item or enough quantity of it
                await ctx.send(f"You do not have enough {component_emoji} **{component_name}**!")
                return

        # Remove required items from the user's inventory and give them the crafted item
        for recipe_item_name, component, component_amount in item_recipe:
            await db_manager.remove_item_from_inventory(ctx.author.id, component, component_amount)
        await db_manager.add_item_to_inventory(ctx.author.id, recipe, 1)
        await ctx.send(f"{item_emote} **{item_name}** has been crafted!")

    @craft.autocomplete("recipe")
    async def craft_autocomplete(self, ctx: discord.Interaction, argument):
        # Get the user's ID
        user_id = ctx.user.id
        # Get the user's inventory
        user_inventory = await db_manager.view_inventory(user_id)
        # Initialize a dictionary to store the items that the user can craft
        possible_recipes = {}

        # Iterate through all the recipes in the database
        all_recipes = await db_manager.get_all_recipes()
        for recipe in all_recipes:
            print(recipe)
            # Get the required items and their amounts for the current recipe
            required_items = await db_manager.get_item_recipe(recipe[0])
            # Assume the user can craft the item until proven otherwise
            can_craft = True

            # Check if the user has enough of each required item
            for recipe_id, required_item_id, amount in required_items:
                hasone = await db_manager.check_user_has_item(user_id, required_item_id)
                item_amount = await db_manager.get_item_amount_from_inventory(user_id, required_item_id)
                # If the user does not have enough of the required item, they cannot craft the item
                if not hasone or item_amount < amount:
                    can_craft = False
                    break

            # If the user can craft the item, add it to the dictionary of possible recipes
            if can_craft:
                if recipe[0] not in possible_recipes:  # If the recipe is not yet in the dictionary, add it
                    item_name = await db_manager.get_basic_item_name(recipe[0])
                    recipe_components = [f"{await db_manager.get_basic_item_name(required_item_id)} x{amount}" for recipe_id, required_item_id, amount in required_items]
                    possible_recipes[recipe[0]] = [item_name, recipe_components]

        # Transform the dictionary to a list and filter it based on the argument
        matching_recipes = [(recipe, f"{name} ({', '.join(components)})") for recipe, (name, components) in possible_recipes.items() if argument.lower() in name.lower()]

        # Return the list of matching recipes
        return [app_commands.Choice(name=name, value=recipe) for recipe, name in matching_recipes[:25]]



#attack command
    #@commands.hybrid_command(
    #    name="attack",
    #    description="Attack an enemy",
    #    aliases=["atk"]
    #)
    #async def attack(self, ctx: Context, enemy: str):
    #    """Attack an enemy"""
    #    userID = ctx.author.id
    #    userName = ctx.author.name
    #    monsterID = enemy
    #    monsterName = await db_manager.get_enemy_name(enemy)
    #    #check if the monster is spawned
    #    monsterSpawned = await db_manager.check_current_spawn(monsterID, ctx.guild.id)
    #    #check if a user is alive
    #    isAlive = await db_manager.is_alive(userID)
    #    if isAlive == False:
    #        await ctx.send("You are dead! Use a revive potion <:RevivePotion:1077645427647725578> to revive!")
    #        return
    #    #if the monster is spawned
    #    if monsterSpawned == 1:
    #        #start the battle
    #        monsterHealth = await db_manager.get_enemy_health(monsterID)
    #        await battle.attack(ctx, userID, userName, monsterID, monsterName)
    #    #if the monster is not spawned
    #    else:
    #        #send a message saying the monster is not spawned
    #        await ctx.send(f"**{monsterName}** is not spawned, wait for the current Monster to be defeated!")
    #        return


#spawn command
##mob command to view the current mob spawned
#    @commands.hybrid_command()
#    async def mob(self, ctx: Context):
#        """View the current mob spawned"""
#        #get the current mob spawned
#        currentSpawn = await db_manager.get_current_spawn(ctx.guild.id)
#        #if there is no mob spawned
#        if currentSpawn == None or [] or [ ]:
#            #send a message saying there is no mob spawned
#            await ctx.send("There is no mob spawned!")
#            return
#        #if there is a mob spawned
#        else:
#            await battle.send_spawned_embed(ctx)
#            #get the mob emote
#            return

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
                recipe_emote = await db_manager.get_basic_item_emoji(recipe_id)
                item_emote = await db_manager.get_basic_item_emoji(item_id)
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
                    description="All the recipes in the game!"
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

    #@commands.hybrid_command(
    #        name="beastiary",
    #        description="This command will view all the enemies.",
    #    )
    #async def beastiary(self, ctx: Context):
    #        # Get all the enemies from the database
    #        enemies = await db_manager.get_all_enemies()
#
    #        # Get all the drops from the database
    #        drops = await db_manager.get_all_enemy_drops()
#
    #        # If there are no enemies, send a message saying there are no enemies
    #        if not enemies:
    #            await ctx.send("There are no enemies!")
    #            return
#
    #        # Transform data into dictionaries
    #        enemies_dict = {enemy[0]: enemy for enemy in enemies}
    #        drops_dict = {}
    #        for drop in drops:
    #            enemy_id = drop[0]
    #            if enemy_id not in drops_dict:
    #                drops_dict[enemy_id] = []
    #            drops_dict[enemy_id].append(drop)
#
    #        # Create a function to generate embeds from a list of enemies
    #        async def create_embeds(enemy_dict, drop_dict):
    #            num_pages = (len(enemy_dict) // 5) + (1 if len(enemy_dict) % 5 > 0 else 0)
    #            embeds = []
    #            enemy_ids = list(enemy_dict.keys())
#
    #            for i in range(num_pages):
    #                start_idx = i * 5
    #                end_idx = start_idx + 5
#
    #                beastiary_embed = discord.Embed(
    #                    title="Beastiary",
    #                    description="All the enemies in the game!",
    #                    color=0x000000,
    #                )
    #                beastiary_embed.set_footer(text=f"Page {i + 1}/{num_pages}")
#
    #                for enemy_id in enemy_ids[start_idx:end_idx]:
    #                    enemy_data = enemy_dict[enemy_id]
    #                    enemy_emote = enemy_data[4]  # Assuming enemy emote is at index 4
    #                    enemy_name = enemy_data[1]  # Assuming enemy name is at index 1
#
    #                    # Generate drops info
    #                    drop_infos = drop_dict.get(enemy_id, [])
    #                    if drop_infos:
    #                        unique_drops = set([drop[1] for drop in drop_infos])
    #                        drop_info_list = []
    #                        for unique_drop in unique_drops:
    #                            item_emote = await db_manager.get_basic_item_emoji(unique_drop)
    #                            item_name = await db_manager.get_basic_item_name(unique_drop)
    #                            drop_info_list.append(f"\t{item_emote} {item_name}")
    #                        drop_info = "\n".join(drop_info_list)
    #                    else:
    #                        drop_info = "No Drops"
#
    #                    beastiary_embed.add_field(name=f"\n{enemy_name}{enemy_emote}(`{enemy_id}`)", value=f"\n{drop_info}\n", inline=False)
#
    #                embeds.append(beastiary_embed)
#
    #            return embeds
#
    #        embeds = await create_embeds(enemies_dict, drops_dict)
#
    #        class BeastiaryButton(discord.ui.View):
    #            def __init__(self, current_page, embeds, **kwargs):
    #                super().__init__(**kwargs)
    #                self.current_page = current_page
    #                self.embeds = embeds
#
    #            @discord.ui.button(label="<<", style=discord.ButtonStyle.green, row=1)
    #            async def on_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
    #                self.current_page = 0
    #                await interaction.response.defer()
    #                await interaction.message.edit(embed=self.embeds[self.current_page])
#
    #            @discord.ui.button(label="<", style=discord.ButtonStyle.green, row=1)
    #            async def on_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
    #                if self.current_page > 0:
    #                    self.current_page -= 1
    #                    await interaction.response.defer()
    #                    await interaction.message.edit(embed=self.embeds[self.current_page])
#
    #            @discord.ui.button(label=">", style=discord.ButtonStyle.green, row=1)
    #            async def on_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
    #                if self.current_page < len(self.embeds) - 1:
    #                    self.current_page += 1
    #                    await interaction.response.defer()
    #                    await interaction.message.edit(embed=self.embeds[self.current_page])
#
    #            @discord.ui.button(label=">>", style=discord.ButtonStyle.green, row=1)
    #            async def on_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
    #                self.current_page = len(self.embeds) - 1
    #                await interaction.response.defer()
    #                await interaction.message.edit(embed=self.embeds[self.current_page])
#
    #        view = BeastiaryButton(current_page=0, embeds=embeds)
    #        await ctx.send(embed=embeds[0], view=view)

    #trade command
    @commands.hybrid_command(
        name="trade",
        description="This command will trade with another user.",
    )
    async def trade(self, ctx: Context, user: discord.Member, item: str, item_count: int = 1, requested_item=None, requested_item_count: int = 1):
        # Get the user's inventory
        user_inventory = await db_manager.view_inventory(ctx.author.id)
        if user_inventory == []:
            await ctx.send("You have no items to trade.")
            return

        # Get the other user's inventory
        other_user_inventory = await db_manager.view_inventory(user.id)
        if other_user_inventory == [] and requested_item is not None:
            await ctx.send(f"{user.name} has no items to trade.")
            return

        # Check if the user has the item
        if item not in [item[0] for item in user_inventory] or user_inventory[item] < item_count:
            await ctx.send(f"You do not have enough `{item}`.")
            return

        if requested_item:
            # Check if the other user has the requested item
            if requested_item not in [item[0] for item in other_user_inventory] or other_user_inventory[requested_item] < requested_item_count:
                await ctx.send(f"{user.name} does not have enough `{requested_item}`.")
                return

        # Get the item emoji
        #if the item is a chest, get the chest emoji
        if item == "chest" or "pet_chest":
            item_emoji = await db_manager.get_chest_icon(item)
        else:
            item_emoji = await db_manager.get_basic_item_emoji(item)

        # Get the requested item emoji
        if requested_item:
            if requested_item == "chest" or "pet_chest":
                requested_item_emoji = await db_manager.get_chest_icon(requested_item)
            else:
                requested_item_emoji = await db_manager.get_basic_item_emoji(requested_item)

        # Ask the other user if they accept the trade/gift
        if requested_item:
            confirm_msg = await ctx.send(f"{user.name}, {ctx.author.name} wants to trade their {item_emoji}{item} (x{item_count}) for your {requested_item_emoji}{requested_item} (x{requested_item_count}). React with 👍 or 👎.")
        else:
            confirm_msg = await ctx.send(f"{user.name}, {ctx.author.name} wants to give you {item_emoji}{item} (x{item_count}). React with 👍 or 👎.")

        # Add reactions to the confirmation message
        await confirm_msg.add_reaction('👍')  # thumbs up
        await confirm_msg.add_reaction('👎')  # thumbs down

        def check(reaction, react_user):
            return react_user == user and str(reaction.emoji) in ['👍', '👎']

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Trade request timed out.')
            return
        if str(reaction.emoji) == '👎':
            await ctx.send("Trade cancelled.")
            return

        # Perform the trade/gift
        await db_manager.remove_item(ctx.author.id, item, item_count)
        await db_manager.add_item_to_inventory(user.id, item, item_count)
        if requested_item:
            await db_manager.remove_item(user.id, requested_item, requested_item_count)
            await db_manager.add_item_to_inventory(ctx.author.id, requested_item, requested_item_count)

        if requested_item:
            await ctx.send(f"{ctx.author.name} has traded their {item_emoji}{item} (x{item_count}) for {user.name}'s {requested_item_emoji}{requested_item} (x{requested_item_count}).")
        else:
            await ctx.send(f"{ctx.author.name} has given {item_emoji}{item} (x{item_count}) to {user.name}.")


    @commands.hybrid_command(
        name="daily",
        description="Grants daily rewards to a user.",
        usage="daily",
    )
    async def daily(self, ctx: Context):
        user_id = ctx.author.id

        # Fetch user data
        user_data = await db_manager.profile(user_id)

        # Check if the user is eligible for daily rewards
        current_time = datetime.datetime.now()
        if user_data[31] is not None:
            last_daily = datetime.datetime.strptime(user_data[31].split('.')[0], "%Y-%m-%d %H:%M:%S")
            seconds_passed = (current_time - last_daily).total_seconds()

            # Calculate the streak
            if seconds_passed < 86400:  # 86400 seconds in a day
                reset_time_unix = int((current_time + datetime.timedelta(days=1)).timestamp())  # Unix timestamp for the next day
                embed = discord.Embed(
                    title="Daily Reward",
                    color=discord.Color.red()
                )
                embed.description = f"You already claimed your daily reward!\nCome back <t:{reset_time_unix}:R>"

                await ctx.send(embed=embed)
                return
            elif seconds_passed < 172800:  # 172800 seconds in two days
                streak = user_data[36] + 1
            else:
                streak = 0
        else:
            streak = 0

        # Grant daily reward
        # Get the bonus % of the user
        bonus = await db_manager.get_percent_bonus(user_id)
        bonus = int(bonus) / 100
        daily_reward = 500 + (streak * 100)  # Add bonus reward according to streak
        daily_reward = int(daily_reward + (daily_reward * bonus))  # Add bonus reward according to user's bonus %
        # Get the bonus % of the daily reward and add it to the daily reward
        new_balance = user_data[2] + daily_reward
        await db_manager.set_money(user_id, new_balance)

        # Update the last_daily and streak fields in the database
        await db_manager.update_daily(user_id)
        await db_manager.set_streak(user_id, streak)

        # Notify the user with an embed
        embed = discord.Embed(
            title="Daily Reward",
            description=f"Successfully granted your daily reward!\nYour new balance is **{new_balance:,}**",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Current streak: {streak} days")
        await ctx.send(embed=embed)
        
    #rob command
    @commands.hybrid_command(
        name="rob",
        description="Rob a user.",
        usage="rob <user>",
    )
    async def rob(self, ctx: Context, user: discord.Member):
        user_id = ctx.author.id
        target_id = user.id

        # Fetch user data
        user_data = await db_manager.profile(user_id)
        target_data = await db_manager.profile(target_id)
        
        # Check if the target is locked
        if target_data[34] == True:
            # Go into the attacker's inventory and see if they have a lockpick or skeleton_key
            inventory = await db_manager.view_inventory(user_id)
            has_lockpick = False
            has_skeleton_key = False

            # Look through the inventory to see if the user has a lockpick or skeleton_key
            for item in inventory:
                if item[1] == "lockpick":
                    has_lockpick = True
                elif item[1] == "skeleton_key":
                    has_skeleton_key = True
                    break  # Skeleton key found, no need to check further

            result_embed = discord.Embed(title="Robbing Results", color=discord.Color.red())

            if has_skeleton_key:
                # Proceed with the rob attempt using the skeleton key (unbreakable)
                result_embed.add_field(name="Lockpick", value="Used an unbreakable skeleton key", inline=False)
            elif has_lockpick:
                # Get the user's luck (assuming it's stored in user_data)
                user_luck = user_data.get('luck', 0)  # default to 0 if not found

                # Calculate the chance of the lockpick breaking
                import random
                base_break_chance = 50  # 50% base chance of breaking for 0 luck
                break_chance = max(base_break_chance - user_luck, 5)  # ensure at least 5% chance of breaking

                if random.randint(1, 100) <= break_chance:
                    # Lockpick breaks
                    result_embed.add_field(name="Lockpick", value="Your lockpick broke while trying to rob the target", inline=False)
                    # Remove the lockpick from the user's inventory
                    await db_manager.remove_item_from_inventory(user_id, "lockpick")
                    await ctx.send(embed=result_embed)
                    return  # Exit after lockpick breaks
                else:
                    # Lockpick did not break, proceed with the rob attempt
                    result_embed.add_field(name="Lockpick", value="Successfully unlocked the target's belongings with a lockpick", inline=False)

            else:
                result_embed.add_field(name="Error", value="You don't have a lockpick or skeleton key to use for the robbery", inline=False)
                await ctx.send(embed=result_embed)
                return

            # Calculate money steal amount
            base_money_stolen = 50  # Base money stolen
            luck_factor = user_luck / 100  # Luck factor based on user's luck
            max_money_stolen = int(base_money_stolen * (1 + luck_factor))  # Max money based on luck
            money_stolen = random.randint(base_money_stolen, max_money_stolen)  # Random amount influenced by luck
            money_stolen = min(money_stolen, target_data['balance'])  # Ensure not to steal more than target has

            new_user_balance = user_data['balance'] + money_stolen
            new_target_balance = target_data['balance'] - money_stolen
            await db_manager.set_money(user_id, new_user_balance)
            await db_manager.set_money(target_id, new_target_balance)

            result_embed.add_field(name="Money Stolen", value=f"{cash}{money_stolen}", inline=False)

            # Calculate item steal chance and number of items to steal
            base_steal_chance = 5  # 5% base chance to steal an item
            steal_chance = min(base_steal_chance + user_luck, 95)  # Cap at 95%
            max_items_to_steal = 1 + (user_luck // 20)  # More items with higher luck, e.g., 0-4 additional items

            target_inventory = await db_manager.view_inventory(target_id)
            items_stolen = []

            for _ in range(max_items_to_steal):
                if random.randint(1, 100) <= steal_chance:
                    if not target_inventory:
                        break  # No items left to steal
                    stolen_item = random.choice(target_inventory)
                    item_count_to_steal = min(random.randint(1, 3), stolen_item[2])  # Steal 1-3 items or as many as they have
                    await db_manager.remove_item_from_inventory(target_id, stolen_item[1], item_count_to_steal)
                    await db_manager.add_item_to_inventory(user_id, stolen_item[1], item_count_to_steal)
                    items_stolen.append({
                        'name': stolen_item[2],
                        'count': item_count_to_steal,
                        'emoji': stolen_item[4]  # Assuming the 4th field is the item emoji
                    })
                    target_inventory = [item for item in target_inventory if item[1] != stolen_item[1]]

            if items_stolen:
                stolen_items_str = ', '.join([f"{item['emoji']} {item['count']}x {item['name']}" for item in items_stolen])
                result_embed.add_field(name="Items Stolen", value=stolen_items_str, inline=False)
            else:
                result_embed.add_field(name="Items Stolen", value="No items stolen", inline=False)

            await ctx.send(embed=result_embed)
        else:
            result_embed = discord.Embed(title="Robbing Results", color=discord.Color.red())
            result_embed.add_field(name="Error", value="The target's belongings are not locked", inline=False)
            await ctx.send(embed=result_embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Basic(bot))