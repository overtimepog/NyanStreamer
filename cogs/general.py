""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import platform
import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
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
from helpers import db_manager
from helpers import checks
import math

EMBED_DESCRIPTION_LIMIT = 2048

class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="List all commands the bot has loaded."
    )
    @checks.not_blacklisted()
    async def help(self, context: Context, command: str = None) -> None:
        from discord.ext import commands
        checkUser = await db_manager.check_user(context.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await context.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return
        prefix = self.bot.config["prefix"]

        if command:
            command_or_group = self.bot.get_command(command.lower())
            if command_or_group and command_or_group.cog_name != 'owner':
                if isinstance(command_or_group, commands.Group):
                    group_commands = "\n".join(sorted([f'`{prefix}{command_or_group.name} {command.name}`: {command.description}' for command in command_or_group.commands if command.cog_name != 'owner']))
                    embed = discord.Embed(title=f'**{command_or_group.name}**', description=group_commands, color=0x9C84EF)
                    await context.send(embed=embed)
                else:
                    embed = discord.Embed(title=f'**{command_or_group.name}**', description=command_or_group.description, color=0x9C84EF)
                    embed.add_field(name="Usage", value=f'`{prefix}{command_or_group.name}`', inline=False)
                    await context.send(embed=embed)
                return
    
            cog = self.bot.get_cog(command.lower())
            if cog:
                commands = sorted(cog.get_commands(), key=lambda cmd: cmd.name)
                if commands:
                    command_list = [f'`{prefix}{command.name}`: {command.description}' for command in commands if command.cog_name != 'owner']
                    command_list_chunks = []
                    current_chunk = ""
                    for command in command_list:
                        if len(current_chunk) + len(command) > EMBED_DESCRIPTION_LIMIT:
                            command_list_chunks.append(current_chunk)
                            current_chunk = command
                        else:
                            current_chunk += "\n" + command
                    if current_chunk:
                        command_list_chunks.append(current_chunk)
    
                    for i, command_list_chunk in enumerate(command_list_chunks):
                        title = f'**{cog.qualified_name}** commands'
                        if len(command_list_chunks) > 1:
                            title += f' {i+1}'
                        embed = discord.Embed(title=title, description=command_list_chunk, color=0x9C84EF)
                        await context.send(embed=embed)
                else:
                    await context.send(f'The {cog.qualified_name} category has no commands.')
                return

            await context.send(f'No command or category named "{command}" was found.')
            return
    
        else:
            # If no command or cog was provided, create a page for each cog except the 'owner' cog
            cogs = self.bot.cogs
            cog_embeds = []
    
            for cog_name in cogs:
                # Skip the 'owner' cog
                if cog_name.lower() == 'owner':
                    continue
                
                cog = self.bot.get_cog(cog_name)
                cmd_list = sorted(cog.get_commands(), key=lambda cmd: cmd.name)
                if cmd_list:
                    command_list = []
                    for command in cmd_list:
                        if command.cog_name != 'owner':
                            if isinstance(command, commands.Group):
                                group_commands = "\n".join(sorted([f'`{prefix}{command.name} {subcommand.name}`: {subcommand.description}' for subcommand in command.commands]))
                                command_list.append(group_commands)
                            else:
                                command_list.append(f'`{prefix}{command.name}`: {command.description}')
    
                    command_list_chunks = []
                    current_chunk = ""
                    for command in command_list:
                        if len(current_chunk) + len(command) > EMBED_DESCRIPTION_LIMIT:
                            command_list_chunks.append(current_chunk)
                            current_chunk = command
                        else:
                            current_chunk += "\n" + command
                    if current_chunk:
                        command_list_chunks.append(current_chunk)
    
                    for i, command_list_chunk in enumerate(command_list_chunks):
                        title = f'**{cog.qualified_name}** commands'
                        if len(command_list_chunks) > 1:
                            title += f' {i+1}'
                        embed = discord.Embed(title=title, description=command_list_chunk, color=0x9C84EF)
                        cog_embeds.append(embed)
                else:
                    await context.send(f'The {cog.qualified_name} category has no commands.')

            class HelpButton(discord.ui.View):
                def __init__(self, current_page, embeds, **kwargs):
                    super().__init__(**kwargs)
                    self.current_page = current_page
                    self.embeds = embeds
                    for i, embed in enumerate(self.embeds):
                        embed.set_footer(text=f"Page {i+1}/{len(self.embeds)}")

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

            view = HelpButton(current_page=0, embeds=cog_embeds)
            await context.send(embed=cog_embeds[0], view=view)

    @commands.hybrid_command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
    )
    @checks.not_blacklisted()
    async def botinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the bot.

        :param context: The hybrid command context.
        """
        allitems = await db_manager.get_all_basic_items()
        embed = discord.Embed(
            description="An RPG Bot Built for Streamers!",
            color=0x9C84EF
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="OverTime#7858",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"/ (Slash Commands) or {self.bot.config['prefix']} for normal commands",
            inline=False
        )
        embed.add_field(
            name="Servers:",
            value=f"{len(self.bot.guilds)}",
            inline=True
        )
        embed.add_field(
            name="Users:",
            value=f"{len(self.bot.users)}",
            inline=True
        )
        embed.add_field(
            name="Total Items:",
            value=f"{len(allitems)}",
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {context.author}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Get some useful (or not) information about the server.",
    )
    @checks.not_blacklisted()
    async def serverinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the server.

        :param context: The hybrid command context.
        """
        roles = [role.name for role in context.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Server Name:**",
            description=f"{context.guild}",
            color=0x9C84EF
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(
                url=context.guild.icon.url
            )
        embed.add_field(
            name="Server ID",
            value=context.guild.id
        )
        embed.add_field(
            name="Member Count",
            value=context.guild.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{len(context.guild.channels)}"
        )
        embed.add_field(
            name=f"Roles ({len(context.guild.roles)})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {context.guild.created_at}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    @checks.not_blacklisted()
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="invite",
        description="Get the invite link of the bot to be able to invite it.",
    )
    @checks.not_blacklisted()
    async def invite(self, context: Context) -> None:
        """
        Get the invite link of the bot to be able to invite it.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id={self.bot.config['application_id']}&scope=bot+applications.commands&permissions={self.bot.config['permissions']}).",
            color=0xD75BF4
        )
        try:
            # To know what permissions to give to your bot, please see here: https://discordapi.com/permissions.html and remember to not give Administrator permissions.
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="server",
        description="Get the invite link of the discord server of the bot for some support.",
    )
    @checks.not_blacklisted()
    async def server(self, context: Context) -> None:
        """
        Get the invite link of the discord server of the bot for some support.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description=f"Join the support server for the bot by clicking [here](https://discord.gg/dMczvnPmAa).",
            color=0xD75BF4
        )
        try:
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)
            
    #starboard command group
    @commands.hybrid_group(
        name="starboard",
        description="The base command for all starboard commands.",
    )
    async def starboard(self, ctx: Context):
        """
        The base command for all starboard commands.

        :param ctx: The context in which the command was called.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("starboard")
            
    #starboard setup command
    @starboard.command(
        name="setup",
        description="setup the starboard",
    )
    @checks.not_blacklisted()
    @has_permissions(manage_channels=True)
    async def setup(self, ctx: Context, channel: discord.TextChannel, emoji: discord.Emoji = "⭐", amount: int = 5):
        """
        setup the starboard

        :param ctx: The context in which the command was called.
        :param channel: The channel to setup the starboard in.
        :param emoji: The emoji to use for the starboard.
        :param amount: The amount of stars needed to post to the starboard.
        """
        emojistr = str(emoji)
        await db_manager.set_starboard_channel(ctx.guild.id, channel.id)
        await db_manager.set_star_emoji(ctx.guild.id, emojistr)
        await db_manager.set_star_threshold(ctx.guild.id, amount)
        await ctx.send(f"Starboard setup in {channel.mention} with the emoji {emoji} and {amount} stars needed to post to the starboard.", ephemeral=True)
        
    #starboard emoji command
    @starboard.command(
        name="emoji",
        description="set the emoji for the starboard",
    )
    @checks.not_blacklisted()
    @has_permissions(manage_channels=True)
    async def emoji(self, ctx: Context, emoji: discord.Emoji):
        """
        set the emoji for the starboard

        :param ctx: The context in which the command was called.
        :param emoji: The emoji to use for the starboard.
        """
        await db_manager.set_star_emoji(ctx.guild.id, emoji)
        await ctx.send(f"Starboard emoji set to {emoji}.", ephemeral=True)
        
    #starboard threshold command
    @starboard.command(
        name="threshold",
        description="set the amount of stars needed to post to the starboard",
    )
    @checks.not_blacklisted()
    @has_permissions(manage_channels=True)
    async def threshold(self, ctx: Context, amount: int):
        """
        set the amount of stars needed to post to the starboard

        :param ctx: The context in which the command was called.
        :param amount: The amount of stars needed to post to the starboard.
        """
        await db_manager.set_star_threshold(ctx.guild.id, amount)
        await ctx.send(f"Starboard threshold set to {amount}.", ephemeral=True)
        
    
    #starboard config command, shows the current config
    @starboard.command(
        name="config",
        description="shows the current starboard config",
    )
    @checks.not_blacklisted()
    async def config(self, ctx: Context):
        """
        shows the current starboard config

        :param ctx: The context in which the command was called.
        """
        config = await db_manager.get_starboard_config(ctx.guild.id)
        if config == None:
            await ctx.send("Starboard not setup yet.", ephemeral=True)
            return
        #"server_id": row[0],
        #"starboard_channel_id": row[1],
        #"star_threshold": row[2],
        #"star_emoji": row[3]
        
        channel = self.bot.get_channel(config["starboard_channel_id"])
        emoji = config["star_emoji"]
        threshold = config["star_threshold"]
        embed = discord.Embed(
            title="Starboard Config",
            description=f"Starboard channel: {channel.mention}\nStarboard emoji: {emoji}\nStarboard threshold: {threshold}",
            color=0x9C84EF
        )
        await ctx.send(embed=embed, ephemeral=True)

    #explain command, tell the user to use /shop to see the shop, use /buy to buy some bait, and use /equip to equip the bait
    @commands.hybrid_command(
        name="explain",
        description="Explain how to use the bot.",
    )
    @checks.not_blacklisted()
    async def explain(self, ctx: Context):
        """
        Explain how to use the bot.

        :param ctx: The context in which the command was called.
        """
        embed = discord.Embed(
            title="How to use the bot",
            description=(
                "To see the shop, use `/shop`.\n"
                "To buy some bait, use `/buy`.\n"
                "To equip the bait, use `/equip` to equip it,\n"
                "then you can go fishing with `/fish`.\n\n"
                "**Searching for a Prize:**\n"
                "Use `/search` to search a location for a prize.\n\n"
                "**Daily Rewards:**\n"
                "Claim your daily cash rewards using `/daily`.\n"
                "Make sure to keep your streak up to earn more rewards!\n\n"
                "**Begging:**\n"
                "You can beg for money using `/beg`.\n"
                "Try begging famous people for money and sometimes you'll get stuff.\n\n"
                "**Jobs:**\n"
                "Check the job board with `/job board`.\n"
                "To accept a job, use `/job accept`.\n"
                "Work the job you accepted with `/work`."
                "To quit a job, use `/job quit`.\n\n"
                "Check out your profile with `/profile` to see your job and other stats.\n\n"
                "**Leaderboard:**\n"
                "Check the leaderboard with `/leaderboard`.\n"
                "To see your rank, use `/rank`.\n\n"
            ),
        )
        await ctx.send(embed=embed)

        

async def setup(bot):
    await bot.add_cog(General(bot))
