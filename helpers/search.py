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
    def __init__(self, label: str, location: dict):
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.location = location

    async def callback(self, interaction: discord.Interaction):
        comment_type = random.choice(["positive_comments", "negative_comments", "death_comments"])
        comment = random.choice(self.location[comment_type])
        embed = discord.Embed(title=self.label, description=comment, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SearchLocationButton(discord.ui.View):
    def __init__(self, locations):
        super().__init__()
        for location in locations:
            self.add_item(SearchButton(location['location'], location))


async def search(ctx: Context):
# Path: helpers\search.py
    userGain = 5000
    with open('assets/search.json') as f:
        data = json.load(f)
        locations = data['searches']

    selected_locations = random.sample(locations, 3)
    view = SearchLocationButton(selected_locations)
    embed = discord.Embed(title="Search", description="Choose a location to search:", color=discord.Color.blue())
    await ctx.send(embed=embed, view=view)