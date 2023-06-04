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

cash = "<:cash:1077573941515792384>"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
}

class PetSelect(discord.ui.Select):
    def __init__(self, pets: list, bot):
        self.bot = bot
        self.pets = pets
        self.selected_pet = None
        super().__init__(placeholder='Select your pet...', min_values=1, max_values=1)

    async def prepare_options(self):
        options = []
        for pet in self.pets:
            pet_emoji = await db_manager.get_basic_item_emote(pet[0])
            petitemname = await db_manager.get_basic_item_name(pet[0])
            options.append(discord.SelectOption(label=pet[2], value=pet[0], emoji=pet_emoji, description=f"Level {pet[3]} {petitemname}"))
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.selected_pet = await db_manager.get_pet_attributes(interaction.user.id, self.values[0])  # Update instance attribute
        embed = await create_pet_embed(self.selected_pet)
        await interaction.response.edit_message(embed=embed)
        await self.prepare_options()

class PetButton(discord.ui.Button):
    def __init__(self, cost: int, attribute: str):
        super().__init__(style=discord.ButtonStyle.primary, label=f'Pet ({cost} {cash})', custom_id=f'{attribute}_pet_button', emoji="🥰")
        self.cost = cost
        self.attribute = attribute

    async def callback(self, interaction: discord.Interaction):
        # Create and send the pet pet gif
        pet_emoji = interaction.message.embeds[0].thumbnail.url

class PetRefillButtons(discord.ui.View):
    def __init__(self, pet: list):
        super().__init__()
        self.feed_cost = 10
        self.clean_cost = 15
        self.play_cost = 5
        self.pet = pet

        self.add_item(discord.ui.Button(label=f'Feed ({self.feed_cost} coins)', style=discord.ButtonStyle.blurple, custom_id="feed_button"))
        self.add_item(discord.ui.Button(label=f'Clean ({self.clean_cost} coins)', style=discord.ButtonStyle.blurple, custom_id="clean_button"))
        self.add_item(discord.ui.Button(label=f'Play ({self.play_cost} coins)', style=discord.ButtonStyle.blurple, custom_id="play_button"))
        self.add_item(discord.ui.Button(label='Pet', style=discord.ButtonStyle.grey, custom_id="pet_button"))
        
    @discord.ui.button(custom_id="feed_button")
    async def feed_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has enough money to feed pet, deduct the cost and refill hunger stat
        # If not enough money, send error message
        pass

    @discord.ui.button(custom_id="clean_button")
    async def clean_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has enough money to clean pet, deduct the cost and refill cleanliness stat
        # If not enough money, send error message
        pass

    @discord.ui.button(custom_id="play_button")
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has enough money to play with pet, deduct the cost and refill happiness stat
        # If not enough money, send error message
        pass

    @discord.ui.button(custom_id="pet_button")
    async def pet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Send a message to the user indicating they pet their pet
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
                await interaction.response.send_message(f"You Pet {self.pet[2]}", file=discord.File(dest, filename="petpet.gif"))



class PetSelectView(discord.ui.View):
    def __init__(self, pets: list, user: discord.User, bot):
        super().__init__()
        self.user = user
        self.value = None
        self.select = PetSelect(pets, bot)
        self.buttons = PetRefillButtons(self.select.selected_pet)
        self.add_item(self.select)
        self.buttons = PetRefillButtons(self.select.selected_pet)  # this is a View, not an Item
        for item in self.buttons.children:  # add each button separately
            self.add_item(item)
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

async def create_pet_embed(pet):
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
