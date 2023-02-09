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

async def slots(ctx: Context, user, gamble):
    #create the slot machine, this will be a discord embed with 3 slots that will spin, through all the possible slot machine emojis, and then stop on 3 emojis
    #if the 3 emojis are the same, the user wins, if not, they lose
    #if the user wins, they get 3x their bet back
    #if the user loses, they lose their bet
    #if the user gets 2 of the same emojis, they get 1.5x their bet back
    pass