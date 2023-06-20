import asyncio
import json
import os
import random
from io import BytesIO
from typing import Any, Optional, Tuple, Union

import aiohttp
import aiosqlite
import discord
import requests
from discord.ext import commands
from discord.ext.commands import Bot, Context
from PIL import Image, ImageChops, ImageDraw, ImageFont

from helpers import db_manager, battle
from typing import List, Tuple

class SearchButton(discord.ui.Button['SearchButton']):
    def __init__(self, label: str, location: dict, user: discord.User):
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.location = location
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("These buttons are not for you!", ephemeral=True)
            return

        # Disable all the buttons once one has been clicked
        for item in self.view.children:
            item.disabled = True

        # Update the original message to reflect the disabled buttons
        await interaction.message.edit(view=self.view)

        comment_types = ["positive_comments", "negative_comments"] * 5 + ["death_comments"]
        comment_type = random.choice(comment_types)
        comment = random.choice(self.location[comment_type])

        print("Chosen Comment Type: " + comment_type + "\nChosen Comment: " + comment)
        embed = discord.Embed(title=self.label, description=comment)
        embed.set_footer(text=f'Searched by {self.user.display_name}', icon_url=self.user.avatar_url)
        await interaction.response.send_message(embed=embed)


class SearchLocationButton(discord.ui.View):
    def __init__(self, locations, user):
        super().__init__()
        for location in locations:
            self.add_item(SearchButton(location['location'], location, user))


async def search(ctx: Context):
    userGain = 5000
    with open('assets/search.json') as f:
        data = json.load(f)
        locations = data['searches']

    selected_locations = random.sample(locations, 3)
    view = SearchLocationButton(selected_locations, ctx.author)
    embed = discord.Embed(title="Search", description="Choose a location to search:", color=discord.Color.blue())
    embed.set_footer(text=f'Search initiated by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed, view=view)
