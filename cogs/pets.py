import asyncio
import datetime
from io import BytesIO
import json
import random
import re
import requests
from discord import Webhook, SyncWebhook
import aiohttp
import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord.ext.commands import Context, has_permissions, Bot
from discord.ext import tasks

from helpers import battle, checks, db_manager, hunt, mine
from typing import List, Tuple
from discord.ext.commands.errors import CommandInvokeError
from petpetgif import petpet

cash = "⚙"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
}

class PetSelect(discord.ui.Select):
    def __init__(self, pets: list, bot, user):
        self.bot = bot
        self.pets = pets
        self.user = user
        self.selected_pet = None
        super().__init__(placeholder='Select your pet...', min_values=1, max_values=1)

    async def prepare_options(self):
        options = []
        self.pets = await db_manager.get_users_pets(self.user.id)
        for pet in self.pets:
            pet_emoji = await db_manager.get_basic_item_emote(pet[0])
            petitemname = await db_manager.get_basic_item_name(pet[0])
            rarity = await db_manager.get_basic_item_rarity(pet[0])
            options.append(discord.SelectOption(label=pet[2], value=pet[0], emoji=pet_emoji, description=f"{rarity} Level {pet[3]} {petitemname}"))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.selected_pet = await db_manager.get_pet_attributes(interaction.user.id, self.values[0])  # Update instance attribute
        embed = await create_pet_embed(self.selected_pet, interaction.user)
        rarity = await db_manager.get_basic_item_rarity(self.selected_pet[0])
        rarity_multiplier = {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 4, "Legendary": 5}
        # Cost calculations
        hunger_cost = (100 - self.selected_pet[5]) * rarity_multiplier[rarity]
        cleanliness_cost = (100 - self.selected_pet[6]) * rarity_multiplier[rarity]
        happiness_cost = (100 - self.selected_pet[7]) * rarity_multiplier[rarity]

        self.view.clear_items()

        user_balance = await db_manager.get_money(interaction.user.id)
        user_balance = user_balance[0]
        user_balance = str(user_balance)
        #remove the ( and ) and , from the balance
        user_balance = user_balance.replace("(", "")
        user_balance = user_balance.replace(")", "")
        user_balance = user_balance.replace(",", "")
        user_balance = int(user_balance)

        feed_button = FeedButton(self.selected_pet, self.view, self, hunger_cost, user_balance, self.bot)
        feed_button.disabled = self.selected_pet[5] >= 100 or user_balance < hunger_cost
        self.view.add_item(feed_button)

        clean_button = CleanButton(self.selected_pet, self.view, self, cleanliness_cost, user_balance, self.bot)
        clean_button.disabled = self.selected_pet[6] >= 100 or user_balance < cleanliness_cost
        self.view.add_item(clean_button)

        play_button = PlayButton(self.selected_pet, self.view, self, happiness_cost, user_balance, self.bot)
        play_button.disabled = self.selected_pet[7] >= 100 or user_balance < happiness_cost
        self.view.add_item(play_button)

        self.view.add_item(PetButton(self.selected_pet))
        self.view.add_item(NameButton(self.selected_pet, self.bot))
        self.view.add_item(self)
        
        await interaction.response.edit_message(embed=embed, view=self.view)
        await self.prepare_options()

class FeedButton(discord.ui.Button):
    def __init__(self, pet, petview, select, cost, user_balance, bot):
        self.pet = pet
        self.petview = petview
        self.select = select
        self.cost = cost
        self.bot = bot
        can_afford = pet[5] <= 100 and user_balance >= cost
        super().__init__(style=discord.ButtonStyle.danger if not can_afford else discord.ButtonStyle.green, label=f"{cash}{cost} Feed", emoji="🍔")

    async def callback(self, interaction: discord.Interaction):
        await db_manager.remove_money(interaction.user.id, self.cost)
        await db_manager.add_pet_hunger(interaction.user.id, self.pet[0], 25)
        pet_attributes = await db_manager.get_pet_attributes(interaction.user.id, self.pet[0])
        embed = await create_pet_embed(pet_attributes, interaction.user)
        rarity = await db_manager.get_basic_item_rarity(self.pet[0])
        rarity_multiplier = {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 4, "Legendary": 5}
        # Cost calculations
        hunger_cost = (100 - pet_attributes[5]) * rarity_multiplier[rarity]
        cleanliness_cost = (100 - pet_attributes[6]) * rarity_multiplier[rarity]
        happiness_cost = (100 - pet_attributes[7]) * rarity_multiplier[rarity]
        self.petview.clear_items()

        user_balance = await db_manager.get_money(interaction.user.id)
        user_balance = user_balance[0]
        user_balance = str(user_balance)
        #remove the ( and ) and , from the balance
        user_balance = user_balance.replace("(", "")
        user_balance = user_balance.replace(")", "")
        user_balance = user_balance.replace(",", "")
        user_balance = int(user_balance)

        feed_button = FeedButton(self.pet, self.petview, self.select, hunger_cost, user_balance, self.bot)
        feed_button.disabled = pet_attributes[5] >= 100 or user_balance < hunger_cost
        self.petview.add_item(feed_button)

        clean_button = CleanButton(self.pet, self.petview, self.select, cleanliness_cost, user_balance, self.bot)
        clean_button.disabled = pet_attributes[6] >= 100 or user_balance < cleanliness_cost
        self.petview.add_item(clean_button)

        play_button = PlayButton(self.pet, self.petview, self.select, happiness_cost, user_balance, self.bot)
        play_button.disabled = pet_attributes[7] >= 100 or user_balance < happiness_cost
        self.petview.add_item(play_button)

        self.petview.add_item(PetButton(self.pet))
        self.petview.add_item(NameButton(self.pet, self.bot))
        self.petview.add_item(self.select)
        
        await interaction.response.edit_message(embed=embed, view=self.petview)

class CleanButton(discord.ui.Button):
    def __init__(self, pet, petview, select, cost, user_balance, bot):
        self.pet = pet
        self.petview = petview
        self.select = select
        self.cost = cost
        self.bot = bot
        can_afford = pet[6] <= 100 and user_balance >= cost
        super().__init__(style=discord.ButtonStyle.danger if not can_afford else discord.ButtonStyle.green, label=f"{cash}{cost} Clean", emoji="🛀")


    async def callback(self, interaction: discord.Interaction):
        await db_manager.remove_money(interaction.user.id, self.cost)
        await db_manager.add_pet_cleanliness(interaction.user.id, self.pet[0], 25)
        pet_attributes = await db_manager.get_pet_attributes(interaction.user.id, self.pet[0])
        embed = await create_pet_embed(pet_attributes, interaction.user)
        rarity = await db_manager.get_basic_item_rarity(self.pet[0])
        rarity_multiplier = {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 4, "Legendary": 5}
        # Cost calculations
        hunger_cost = (100 - pet_attributes[5]) * rarity_multiplier[rarity]
        cleanliness_cost = (100 - pet_attributes[6]) * rarity_multiplier[rarity]
        happiness_cost = (100 - pet_attributes[7]) * rarity_multiplier[rarity]
        self.petview.clear_items()

        user_balance = await db_manager.get_money(interaction.user.id)
        user_balance = user_balance[0]
        user_balance = str(user_balance)
        #remove the ( and ) and , from the balance
        user_balance = user_balance.replace("(", "")
        user_balance = user_balance.replace(")", "")
        user_balance = user_balance.replace(",", "")
        user_balance = int(user_balance)

        feed_button = FeedButton(self.pet, self.petview, self.select, hunger_cost, user_balance, self.bot)
        feed_button.disabled = pet_attributes[5] >= 100 or user_balance < hunger_cost
        self.petview.add_item(feed_button)

        clean_button = CleanButton(self.pet, self.petview, self.select, cleanliness_cost, user_balance, self.bot)
        clean_button.disabled = pet_attributes[6] >= 100 or user_balance < cleanliness_cost
        self.petview.add_item(clean_button)

        play_button = PlayButton(self.pet, self.petview, self.select, happiness_cost, user_balance, self.bot)
        play_button.disabled = pet_attributes[7] >= 100 or user_balance < happiness_cost
        self.petview.add_item(play_button)

        self.petview.add_item(PetButton(self.pet))
        self.petview.add_item(NameButton(self.pet, self.bot))
        self.petview.add_item(self.select)
        
        await interaction.response.edit_message(embed=embed, view=self.petview)

class PlayButton(discord.ui.Button):
    def __init__(self, pet, petview, select, cost, user_balance, bot):
        self.pet = pet
        self.petview = petview  
        self.select = select
        self.cost = cost
        self.bot = bot
        can_afford = pet[7] <= 100 and user_balance >= cost
        super().__init__(style=discord.ButtonStyle.danger if not can_afford else discord.ButtonStyle.green, label=f"{cash}{cost} Play", emoji="⚽")

    async def callback(self, interaction: discord.Interaction):
        await db_manager.remove_money(interaction.user.id, self.cost)
        await db_manager.add_pet_happiness(interaction.user.id, self.pet[0], 25)
        pet_attributes = await db_manager.get_pet_attributes(interaction.user.id, self.pet[0])
        embed = await create_pet_embed(pet_attributes, interaction.user)
        rarity = await db_manager.get_basic_item_rarity(self.pet[0])
        rarity_multiplier = {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 4, "Legendary": 5}
        # Cost calculations
        hunger_cost = (100 - pet_attributes[5]) * rarity_multiplier[rarity]
        cleanliness_cost = (100 - pet_attributes[6]) * rarity_multiplier[rarity]
        happiness_cost = (100 - pet_attributes[7]) * rarity_multiplier[rarity]
        self.petview.clear_items()

        user_balance = await db_manager.get_money(interaction.user.id)
        user_balance = user_balance[0]
        user_balance = str(user_balance)
        #remove the ( and ) and , from the balance
        user_balance = user_balance.replace("(", "")
        user_balance = user_balance.replace(")", "")
        user_balance = user_balance.replace(",", "")
        user_balance = int(user_balance)

        feed_button = FeedButton(self.pet, self.petview, self.select, hunger_cost, user_balance, self.bot)
        feed_button.disabled = pet_attributes[5] >= 100 or user_balance < hunger_cost
        self.petview.add_item(feed_button)

        clean_button = CleanButton(self.pet, self.petview, self.select, cleanliness_cost, user_balance, self.bot)
        clean_button.disabled = pet_attributes[6] >= 100 or user_balance < cleanliness_cost
        self.petview.add_item(clean_button)

        play_button = PlayButton(self.pet, self.petview, self.select, happiness_cost, user_balance, self.bot)
        play_button.disabled = pet_attributes[7] >= 100 or user_balance < happiness_cost
        self.petview.add_item(play_button)

        self.petview.add_item(PetButton(self.pet))
        self.petview.add_item(NameButton(self.pet, self.bot))
        self.petview.add_item(self.select)
        
        await interaction.response.edit_message(embed=embed, view=self.petview)

class PetButton(discord.ui.Button):
    def __init__(self, pet: list):
        self.pet = pet
        super().__init__(style=discord.ButtonStyle.gray, label='Pet', emoji='🖐️', row=1)

    async def callback(self, interaction: discord.Interaction):
        # Add your pet functionality here
        # Send a message to the user indicating they pet their pet
        pet_emoji = await db_manager.get_basic_item_emote(self.pet[0])
        if pet_emoji is not None:
                pet_emoji = pet_emoji.split(':')[2].replace('>', '')
                pet_emoji = f"https://cdn.discordapp.com/emojis/{pet_emoji}.gif?size=240&quality=lossless"

                # Use aiohttp to download the image
                async with aiohttp.ClientSession() as session:
                    async with session.get(pet_emoji) as resp:
                        image = await resp.read()

                source = BytesIO(image)  # file-like container to hold the emoji in memory
                dest = BytesIO()  # container to store the petpet gif in memory
                petpet.make(source, dest)
                dest.seek(0)  # set the file pointer back to the beginning so it doesn't upload a blank file.
                await interaction.response.send_message(file=discord.File(dest, filename="petpet.gif"))

class NameButton(discord.ui.Button):
    def __init__(self, pet: list, bot):
        self.pet = pet
        self.bot = bot
        super().__init__(style=discord.ButtonStyle.gray, label='Name', emoji='🔤', row=1)

    async def callback(self, interaction: discord.Interaction):
        # Add your pet functionality here
        #check if the user has the nametag item
        hasone = await db_manager.check_user_has_item(interaction.user.id, "nametag")
        if hasone == True:
            #remove the nametag from the user
            await db_manager.remove_item_from_inventory(interaction.user.id, "nametag", 1)
            #send a message to the user asking them what they want to name their pet
            await interaction.response.send_message("What would you like to name your pet?")
            #wait for the user to respond
            def check(m):
                return m.author == interaction.user
            while True:
                msg = await self.bot.wait_for('message', check=check)
                if len(msg.content) > 25:
                    #send a message to the user saying the name is too long
                    message = await interaction.original_response()
                    await message.edit(content="Your pet's name is too long! Please try again with a shorter name.")
                    await db_manager.add_item_to_inventory(interaction.user.id, "nametag", 1)
                    await msg.delete()
                else:
                    break
            #set the name of the pet to the message content
            await db_manager.set_pet_name(interaction.user.id, self.pet[0], msg.content)
            #save the pet's name to a variable
            pet_name = msg.content
            #now delete the message the user sent
            await msg.delete()

            for option in self.view.select.options:
                if option.value == self.pet[0]:
                    option.label = pet_name
                    break

            pet_emoji = await db_manager.get_basic_item_emote(self.pet[0])
            item_name = await db_manager.get_basic_item_name(self.pet[0])
            rarity = await db_manager.get_basic_item_rarity(self.pet[0])
            pet_emoji = pet_emoji.split(':')[2].replace('>', '')
            pet_emoji = f"https://cdn.discordapp.com/emojis/{pet_emoji}.gif?size=240&quality=lossless"
            #send a message to the user saying their pet has been named in a embed
            embed = discord.Embed(
                title=f"Your {item_name} has been named!",
                description=f"Your {item_name} has been named **{pet_name}**!",
                color= rarity_colors[rarity]
            )
            embed.set_thumbnail(url=pet_emoji)
            embed.set_footer(text=f"Owner: {interaction.user.name}", icon_url=interaction.user.avatar.url)
            message = await interaction.original_response()
            await message.edit(content="Nice Name :)", embed=embed)
            # Update the pet's name in the select menu
        else:
            #send a message to the user saying they don't have a nametag
            icon = await db_manager.get_basic_item_emote("nametag")
            embed = discord.Embed(
                title=f"You don't have a Name Tag!",
                description=f"You don't have a Name Tag to name your pet with! You can buy one from the shop.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
        



class PetSelectView(discord.ui.View):
    def __init__(self, pets: list, user: discord.User, bot):
        super().__init__()
        self.user = user
        self.value = None
        self.select = PetSelect(pets, bot, user)
        self.add_item(self.select)


    async def prepare(self):
        await self.select.prepare_options()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.user.id == interaction.user.id

def calculate_time_till_empty(current_value, decrease_rate, loop_interval):
    """Calculate the time until the attribute reaches zero."""
    if current_value <= 0:
        return "Empty"
    else:
        remaining_loops = current_value // decrease_rate
        remaining_time = remaining_loops * loop_interval  # in minutes

        hours, remainder = divmod(remaining_time, 60)
        minutes, seconds = divmod(remainder, 1)

        if hours > 0:
            return f"{int(hours)}hr"
        elif minutes > 0:
            return f"{int(minutes)}m"
        else:
            return f"{int(seconds)}s"

def generate_progress_bar(value, max_value):
    TOTAL_PARTS = 10
    filled_parts = round((value / max_value) * TOTAL_PARTS)
    bar = '▰' * filled_parts + '▱' * (TOTAL_PARTS - filled_parts)

    return bar

async def create_pet_embed(pet, user):
    rarity = await db_manager.get_basic_item_rarity(pet[0])
    icon = await db_manager.get_basic_item_emote(pet[0])
    pet_description = await db_manager.get_basic_item_description(pet[0])
    embed = discord.Embed(
        title=f"{pet[2]}'s Statistics",
        description=f"{pet_description}",
        color=rarity_colors[rarity]
    )
    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{icon.split(':')[2].replace('>', '')}.gif?size=240&quality=lossless")
    embed.add_field(name="Level", value=pet[3], inline=True)
    embed.add_field(name="XP", value=pet[4], inline=True)
    effect = await db_manager.get_basic_item_effect(pet[0])
    if effect == "None":
        pass
    else:
        #if the effect has a _ in it, it will replace it with a space
        effect = effect.replace("_", " ")
        #now make the first letter of each word uppercase
        effect = effect.title()
        embed.add_field(name="Effect", value=effect, inline=False)
    embed.add_field(name=f"Hunger `{pet[5]}/100` Time till empty: `{calculate_time_till_empty(pet[5], 5, 30)}`", value="```" + generate_progress_bar(pet[5], 100) + f"```", inline=False)
    embed.add_field(name=f"Cleanliness `{pet[6]}/100` Time till empty: `{calculate_time_till_empty(pet[6], 5, 120)}`", value="```" + generate_progress_bar(pet[6], 100) + f"```", inline=False)
    embed.add_field(name=f"Happiness `{pet[7]}/100` Time till empty: `{calculate_time_till_empty(pet[7], 5, 60)}`", value="```" + generate_progress_bar(pet[7], 100) + f"```", inline=False)
    await db_manager.get_money(pet[1])
    #get the name of a user by their id
    user_balance = await db_manager.get_money(user.id)
    user_balance = user_balance[0]
    user_balance = str(user_balance)
    #remove the ( and ) and , from the balance
    user_balance = user_balance.replace("(", "")
    user_balance = user_balance.replace(")", "")
    user_balance = user_balance.replace(",", "")
    user_balance = int(user_balance)
    embed.set_footer(text=f"Owner: {user.name} | Balance: {cash}{user_balance}", icon_url=user.avatar.url)
    return embed

class Pets(commands.Cog, name="pets"):
    def __init__(self, bot):
        self.bot = bot
        self.update_pet_hunger.start()
        self.update_pet_happiness.start()
        self.update_pet_cleanliness.start()

    @commands.hybrid_command()
    async def pet(self, ctx: Context):
        """Display your pet's stats."""
        pets = await db_manager.get_users_pets(ctx.author.id)
        if not pets:
            await ctx.send('You do not own any pets.')
            return

        view = PetSelectView(pets, ctx.author, self.bot)
        await view.prepare()
        message = await ctx.send('Select a Pet :)', view=view)
        view.message = message

    @tasks.loop(minutes=30)
    async def update_pet_hunger(self):
        """Update pets' hunger periodically."""
        all_pets = await db_manager.get_all_users_pets()
        for pet in all_pets:
            new_hunger = max(0, pet[5] - 5)  # pet[5] seems to be the current hunger value
            await db_manager.set_pet_hunger(pet[1], pet[0], new_hunger)
            updated = await db_manager.get_pet_attributes(pet[1], pet[0])
            print(f'Updated hunger for {pet[1]}' + f'\'s pet {pet[2]}, It is now {updated[5]}')


    @update_pet_hunger.before_loop
    async def before_update_hunger(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1)
    async def update_pet_happiness(self):
        """Update pets' happiness periodically."""
        all_pets = await db_manager.get_all_users_pets()
        for pet in all_pets:
            new_happiness = max(0, pet[7] - 5)  # pet[7] seems to be the current happiness value
            await db_manager.set_pet_happiness(pet[1], pet[0], new_happiness)
            updated = await db_manager.get_pet_attributes(pet[1], pet[0])
            print(f'Updated happiness for {pet[1]}' + f'\'s pet {pet[2]}, It is now {updated[7]}')


    @update_pet_happiness.before_loop
    async def before_update_happiness(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=2)
    async def update_pet_cleanliness(self):
        """Update pets' cleanliness periodically."""
        all_pets = await db_manager.get_all_users_pets()
        for pet in all_pets:
            new_cleanliness = max(0, pet[6] - 5)  # pet[6] seems to be the current cleanliness value
            await db_manager.set_pet_cleanliness(pet[1], pet[0], new_cleanliness)
            updated = await db_manager.get_pet_attributes(pet[1], pet[0])
            print(f'Updated cleanliness for {pet[1]}' + f'\'s pet {pet[2]}, It is now {updated[6]}')


    @update_pet_cleanliness.before_loop
    async def before_update_cleanliness(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Pets(bot))
