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

from helpers import battle, checks, db_manager, games
import asyncio
import os
import random
from typing import List, Tuple, Union

import discord
from discord.ext import commands
from helpers.card import Card
from helpers.embed import make_embed
from PIL import Image
import lavalink


class Music(commands.Cog, name="music"):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # Initialize an empty dictionary to hold the queues for each guild
        self.repeat_modes = {}  # 'none', 'one', 'all'
        self.vote_skips = {}  # Holds vote skip data for each guild
        self.vote_clears = {}  # Holds vote clear data for each guild
        
        bot.lavalink = lavalink.Client(self.bot.user.id)
        bot.lavalink.add_node('localhost', 2333, 'youshallnotpass', 'na', 'default-node')  # Your Lavalink server info
        bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        lavalink.add_event_hook(Music.track_hook)


    def get_queue(self, guild_id):
        """Return the queue for the given guild."""
        return self.queues.setdefault(guild_id, [])

    def get_repeat_mode(self, guild_id):
        """Return the repeat mode for the given guild."""
        return self.repeat_modes.setdefault(guild_id, 'none')

    async def play_next(self, guild_id):
        """Play the next song in the queue."""
        player = await self.bot.lavalink.get_player(guild_id)
        repeat_mode = self.get_repeat_mode(guild_id)

        if repeat_mode == 'none' and not self.get_queue(guild_id):
            return

        if repeat_mode == 'one':
            await player.play(player.current_track)
            return

        if repeat_mode == 'all' and not player.queue:
            self.get_queue(guild_id).append(player.current_track)

        next_track = self.get_queue(guild_id).pop(0)
        await player.play(next_track)

    async def initiate_vote(self, ctx, vote_type):
        """Initiate a vote for skipping or clearing."""
        if vote_type == 'skip':
            vote_dict = self.vote_skips
            action = "skip the song"
        elif vote_type == 'clear':
            vote_dict = self.vote_clears
            action = "clear the queue"
        else:
            return

        if ctx.guild.id in vote_dict:
            return await ctx.send("A vote is already in progress!")

        message = await ctx.send(f"Vote to {action}! React with 👍 to vote.")
        await message.add_reaction("👍")

        def check(reaction, user):
            return user != self.bot.user and str(reaction.emoji) == "👍" and reaction.message.id == message.id

        vote_dict[ctx.guild.id] = {"message_id": message.id, "votes": 0}

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                vote_dict[ctx.guild.id]["votes"] += 1

                # If votes reach a certain threshold (e.g., 3 votes), perform the action
                if vote_dict[ctx.guild.id]["votes"] >= 3:
                    if vote_type == 'skip':
                        await ctx.invoke(self.force_skip)
                    elif vote_type == 'clear':
                        await ctx.invoke(self.force_clear)
                    del vote_dict[ctx.guild.id]
                    return

            except asyncio.TimeoutError:
                await ctx.send(f"Vote to {action} failed!")
                del vote_dict[ctx.guild.id]
                return

    @commands.hybrid_command(
        name="play",
        description="Plays a song or adds it to the queue."
    )
    async def play(self, ctx, *, query: str):
        player = await self.bot.lavalink.get_player(ctx.guild.id)

        # If the bot is not connected to a voice channel
        if not player.is_connected:
            if ctx.author.voice:
                await ctx.invoke(self.join)
            else:
                return await ctx.send("You are not connected to any voice channel.")

        query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send('No songs were found with that query.')

        track = results['tracks'][0]

        # If something is already playing, add the track to the queue
        if player.is_playing:
            self.get_queue(ctx.guild.id).append(track)
            return await ctx.send(f'Added {track["info"]["title"]} to the queue.')
        else:
            await player.play(track)
            await ctx.send(f'Now playing: {track["info"]["title"]}')

    @commands.hybrid_command(
        name="skip",
        description="Vote to skip the currently playing song."
    )
    async def skip(self, ctx):
        await self.initiate_vote(ctx, 'skip')

    @commands.hybrid_command(
        name="force_skip",
        description="Force skip the currently playing song (internal use)."
    )
    async def force_skip(self, ctx):
        player = await self.bot.lavalink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("Nothing is playing.")
        await player.skip()
        await self.play_next(ctx.guild.id)

    @commands.hybrid_command(
        name="clear",
        description="Vote to clear the queue."
    )
    async def clear(self, ctx):
        await self.initiate_vote(ctx, 'clear')

    @commands.hybrid_command(
        name="force_clear",
        description="Force clear the queue (internal use)."
    )
    async def force_clear(self, ctx):
        self.get_queue(ctx.guild.id).clear()
        await ctx.send("Queue cleared!")

    @commands.hybrid_command(
        name="shuffle",
        description="Shuffle the queue."
    )
    async def shuffle(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            return await ctx.send("The queue is empty.")
        random.shuffle(queue)
        await ctx.send("Queue shuffled!")

    @commands.hybrid_command(
        name="repeat",
        description="Set the repeat mode. Modes: none, one, all."
    )
    async def repeat(self, ctx, mode: str):
        if mode not in ['none', 'one', 'all']:
            return await ctx.send("Invalid mode. Choose from 'none', 'one', or 'all'.")
        self.repeat_modes[ctx.guild.id] = mode
        await ctx.send(f"Repeat mode set to: {mode}")

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.TrackEndEvent):
            await self.play_next(int(event.player.guild_id))

async def setup(bot):
    await bot.add_cog(Music(bot))