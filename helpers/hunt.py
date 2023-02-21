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

async def hunt(ctx: Context):
    firsthuntitems = await db_manager.view_huntable_items()
    #get the hunt chance for each item in the huntitems list
    huntItems = []
    for item in firsthuntitems:
        item_id = item[0]
        hunt_chance = item[16]
        huntItems.append([item_id, hunt_chance])
    #get the user's luck
    luck = await db_manager.get_luck(ctx.author.id)
    #make the luck an int
    luck = int(luck[0])
    