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


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="List all commands the bot has loaded."
    )
    @checks.not_blacklisted()
    async def help(self, context: Context, command_or_cog: str = None) -> None:
        prefix = self.bot.config["prefix"]
    
        if command_or_cog:
            command_or_group = self.bot.get_command(command_or_cog.lower())
            if command_or_group and command_or_group.cog_name != 'Owner':
                from discord.ext import commands
                if isinstance(command_or_group, commands.HybridGroup):
                    group_commands = "\n".join([f'`{prefix}{command.name}`: {command.description}' for command in command_or_group.commands if command.cog_name != 'Owner'])
                    embed = discord.Embed(title=f'**{command_or_group.name}**', description=group_commands, color=0x9C84EF)
                    await context.send(embed=embed)
                else:
                    embed = discord.Embed(title=f'**{command_or_group.name}**', description=command_or_group.description, color=0x9C84EF)
                    embed.add_field(name="Usage", value=f'`{prefix}{command_or_group.name}`', inline=False)
                    await context.send(embed=embed)
                return
    
            cog = self.bot.get_cog(command_or_cog.title())
            if cog:
                commands = cog.get_commands()
                if commands:
                    command_list = "\n".join([f'`{prefix}{command.name}`: {command.description}' for command in commands if command.cog_name != 'Owner'])
                    embed = discord.Embed(title=f'**{cog.qualified_name}** commands', description=command_list, color=0x9C84EF)
                    await context.send(embed=embed)
                else:
                    await context.send(f'The {cog.qualified_name} category has no commands.')
                return
    
            await context.send(f'No command or category named "{command_or_cog}" was found.')
            return
    
        else:
            # If no command or cog was provided, list all commands
            all_commands = {command for command in self.bot.commands if command.cog_name != 'Owner'}
            command_list = "\n".join([f'`{prefix}{command.name}`: {command.description}' for command in all_commands])
            embed = discord.Embed(title='**All commands**', description=command_list, color=0x9C84EF)
            await context.send(embed=embed)

        # Get all cogs and their commands
        cogs_data = []
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            for command in commands:
                if command.cog_name != 'Owner':
                    description = command.description.partition('\n')[0]
                    cogs_data.append((i, f"{command.name}", description))

        # Calculate number of pages based on number of cogs
        num_pages = (len(cogs_data) // 5) + (1 if len(cogs_data) % 5 > 0 else 0)

        # Create a function to generate embeds from a list of cogs
        async def create_embeds(cogs_list):
            embeds = []
            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                help_embed = discord.Embed(title="Help", description="List of available commands: use nya  or /", color=0x9C84EF)
                help_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                for cog in cogs_list[start_idx:end_idx]:
                    cog_name, command_name, command_description = cog
                    help_embed.add_field(name=f'{command_name}', value=f'```{command_description}```', inline=False)

                embeds.append(help_embed)

            return embeds

        # Create a list of embeds with 5 cogs per embed
        embeds = await create_embeds(cogs_data)

        class HelpButton(discord.ui.View):
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

        view = HelpButton(current_page=0, embeds=embeds)
        await context.send(embed=embeds[0], view=view)

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

async def setup(bot):
    await bot.add_cog(General(bot))
