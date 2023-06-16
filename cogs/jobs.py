import asyncio
from collections import defaultdict
import datetime
import json
import os
import random
import re
import requests
from discord import Webhook, SyncWebhook
import aiohttp
import discord
from discord import Embed, app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context, has_permissions

from helpers import battle, checks, db_manager, hunt, mine, games
from typing import List, Tuple
from discord.ext.commands.errors import CommandInvokeError


global i
i = 0
cash = "⚙"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
    # Add more rarities and colors as needed
}

class Jobs(commands.Cog, name="jobs"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
    name="job",
    description="Job Commands",
    )
    async def job(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid job command passed...')

    @job.command(
    name="quit",
    description="quit your current job",
    )
    async def quitjob(self, ctx: Context):
        # Retrieve the specific job from the database
        #check if the user exists
        user_exists = await db_manager.check_user(ctx.author.id)
        if user_exists == None or user_exists == [] or user_exists == False or user_exists == 0 or user_exists == "None":
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        #check if the user has a job
        user = await db_manager.profile(ctx.author.id)
        user_job = user[26]
        user_job = str(user_job)
        if user_job is None or user_job == 0 or user_job == "None":
            await ctx.send("You don't have a job!")
            return
        #remove the job from the user
        await db_manager.remove_user_job(ctx.author.id)
        await ctx.send(f"You have quit your Position as a {user_job.title()}, if you want to get a new one please check the job board")

    @job.command(
    name="board",
    description="This command will show the job board.",
    )
    async def jobboard(self, ctx: Context):
        # Retrieve all jobs from the database
        jobs = await db_manager.get_jobs_on_board()

        if jobs == []:
            # If there are no jobs on the board, send a message
            await ctx.send("There are no jobs on the board.")
            return

        #check if the user exists
        user_exists = await db_manager.check_user(ctx.author.id)
        if user_exists == None or user_exists == [] or user_exists == False or user_exists == 0 or user_exists == "None":
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return

        # Calculate number of pages based on number of jobs
        num_pages = (len(jobs) // 5) + (1 if len(jobs) % 5 > 0 else 0)

        # Create a function to generate embeds from a list of jobs
        async def create_embeds(job_list, user_id):
            num_pages = (len(job_list) // 5) + (1 if len(job_list) % 5 > 0 else 0)
            embeds = []

            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                job_embed = discord.Embed(
                    title="Job Board",
                    description="Jobs available :)",
                )
                job_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                for job in job_list[start_idx:end_idx]:
                    job_id = job[0]
                    job_name = job[1]
                    icon = job[2]

                    # Get description
                    desc = await db_manager.get_job_description_from_id(job_id)

                    # Get requirements
                    hours_required = await db_manager.get_required_hours_from_id(job_id)
                    item_required = await db_manager.get_required_item_from_id(job_id)
                    level_required = await db_manager.get_required_level_from_id(job_id)

                    # If there's an item requirement, get the icon for it
                    item_icon = ""
                    if item_required is not None:
                        item_icon = await db_manager.get_basic_item_emoji(item_required)

                    # Check if the user meets the requirements
                    user_hours = await db_manager.get_hours_worked(user_id)
                    level = await db_manager.get_level(user_id)
                    user_has_item = item_required is None or await db_manager.check_user_has_item(user_id, item_required) > 0
                    requirements_met = (int(user_hours) >= int(hours_required)) and user_has_item and (int(level) >= int(level_required))

                    # Depending on whether the user meets the requirements, add a check mark or an X
                    requirements_met_icon = "✅" if requirements_met else "❌"

                    # Build the field value string with job description, requirements, and whether the user meets them
                    field_value = f"{desc}\n"
                    base_pay = await db_manager.get_base_pay_from_id(job_id)
                    cooldown = await db_manager.get_cooldown_from_id(job_id)
                    cooldown_reduction_per_level = await db_manager.get_cooldown_reduction_per_level_from_id(job_id)
                    remaining_cooldown = await db_manager.get_cooldown_status(user_id, cooldown, cooldown_reduction_per_level)
                    total_seconds = remaining_cooldown.total_seconds()
                    
                    # Get hours and remaining seconds
                    hours, remainder = divmod(total_seconds, 3600)
                    
                    # Get minutes from the remaining seconds
                    minutes = remainder // 60
                    
                    if hours > 0:
                        remaining_cooldown_str = f"{int(hours)}hr {int(minutes)}min"
                    else:
                        remaining_cooldown_str = f"{int(minutes)}min"
                    
                    field_value += f"> Cooldown Per Work: {remaining_cooldown_str}\n"
                    field_value += f"> Pay: {cash}{base_pay}\n"
                    field_value += f"> Cooldown Per Work: {remaining_cooldown_str}\n"
                    if level_required is not None or level_required != 0 or level_required != "None":
                        field_value += f"> Level required: `{level_required}`\n"
                    if hours_required is not None or hours_required != 0 or hours_required != "None":
                        field_value += f"> Hours required: `{hours_required}`\n"
                    if item_required is not None or item_required != 0 or item_required != "None":
                        field_value += f"> Item required: {item_icon} `{item_required}`\n"

                    #get the pay and cooldown
                    field_value += f"> ID: `{job_id}`\n"
                    

                    job_embed.add_field(name=f"{requirements_met_icon} {icon}**{job_name}**", value=field_value, inline=False)

                embeds.append(job_embed)

            return embeds

        # Create a list of embeds with 5 jobs per embed
        embeds = await create_embeds(jobs, ctx.author.id)

        class JobBoardButton(discord.ui.View):
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

        view = JobBoardButton(current_page=0, embeds=embeds)
        await ctx.send(embed=embeds[0], view=view)

    @job.command(
    name="accept",
    description="Accept a job from the job board.",
)
    async def acceptjob(self, ctx: Context, job: str):
        # Retrieve the specific job from the database
        #check if the user exists
        user_exists = await db_manager.check_user(ctx.author.id)
        if user_exists == None or user_exists == [] or user_exists == False or user_exists == 0 or user_exists == "None":
            await ctx.send("You are not in the database yet, please use the `nya start or /start` command to start your adventure!")
            return
        
        if job is None:
            # If the job does not exist, send a message
            await ctx.send("That job does not exist.")
            return

        # Check if the user already has a job
        user = await db_manager.profile(ctx.author.id)
        user_job = user[26]
        #if the user doesnt have a job
        if user_job is None or user_job == 0 or user_job == "None":
            #give the user the job
            #check the requirements
            hours_required = await db_manager.get_required_hours_from_id(job)
            if hours_required > 0:
                user_hours = await db_manager.get_hours_worked(ctx.author.id)
                if user_hours < hours_required:
                    await ctx.send(f"You need to have worked {hours_required} hours to accept this job!")
                    return
            #check the item 
            item_required = await db_manager.get_required_item_from_id(job)
            if item_required is not None:
                if await db_manager.check_user_has_item(ctx.author.id, item_required) == 0:
                    icon = await db_manager.get_basic_item_emoji(item_required)
                    await ctx.send(f"You need to have a {icon}`{item_required}` to accept this job!")
                    return
                
            #check the level
            level_required = await db_manager.get_required_level_from_id(job)
            if level_required is not None:
                level = await db_manager.get_level(ctx.author.id)
                if level < level_required:
                    await ctx.send(f"You need to be level {level_required} to accept this job!")
                    return
            await db_manager.add_user_job(ctx.author.id, job)
            job_icon = await db_manager.get_job_icon_from_id(job)
            await ctx.send(f"You have accepted the job {job_icon}{job.title()}!")
        else:
            await ctx.send("You already have a job!, please use `nya job quit or /job quit` command to quit your current job.")


    @acceptjob.autocomplete("job")
    async def job_autocomplete(self, ctx: discord.Interaction, argument):
        #print(argument)
        user_jobs = await db_manager.get_jobs_on_board()
        choices = []
        for job in user_jobs:
            if argument.lower() in job[1].lower():
                choices.append(app_commands.Choice(name=job[1], value=job[0]))
        return choices[:25]


    @commands.hybrid_command(
        name="work",
        description="Work your job to earn money.",
        )
    async def work(self, ctx: commands.Context):
        user_id = ctx.author.id
        job_id = await db_manager.get_user_job(user_id)
        if job_id is None:
            await ctx.send("You don't have a job!")
            return
        
        cooldown = await db_manager.get_cooldown_from_id(job_id)
        cooldown_reduction_per_level = await db_manager.get_cooldown_reduction_per_level_from_id(job_id)
        remaining_cooldown = await db_manager.get_cooldown_status(user_id, cooldown, cooldown_reduction_per_level)

        if remaining_cooldown.total_seconds() > 0:
            await ctx.send(f"You're still on cooldown! Wait for {remaining_cooldown}.")
            return
        
        base_pay = await db_manager.get_base_pay_from_id(job_id)
        penalty_percentage = 0.2

        minigame = await db_manager.get_minigame_for_job(job_id)
        if minigame is None:
            await ctx.send("No minigames found for this job!")
            return
        minigameText = minigame[3]

        game_data = await db_manager.get_data_for_minigame(minigame)

        callback_processed_future = ctx.bot.loop.create_future()

        if minigame[2] == 'Trivia':
            result, message = await games.play_trivia(ctx, game_data, minigameText, callback_processed_future)
        elif minigame[2] == 'Order':
            result, message = await games.play_order_game(ctx, game_data, minigameText, callback_processed_future)
        elif minigame[2] == 'Matching':
            result, message = await games.play_matching_game(ctx, game_data, minigameText, callback_processed_future)
        else:
            print("Unknown game type")
            return

        if result:
            user_luck = await db_manager.get_luck(user_id)
            adjusted_luck = user_luck / 100

            outcomes = sorted(await db_manager.get_rewards_for_minigame(minigame[0]), key=lambda x: x[3], reverse=True)
            earned_reward = None

            for outcome in outcomes:
                outcome_id, reward_type, reward_value, reward_probability = outcome
                adjusted_probability = reward_probability + (adjusted_luck * (1 - reward_probability))

                if random.random() <= adjusted_probability:
                    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                    BASE_DIR = os.path.dirname(CURRENT_DIR)
                    SUCCESS_PATH = os.path.join(BASE_DIR, "assets", "jobs", "job_success.json")

                    with open(SUCCESS_PATH, 'r') as f:
                        success_messages = json.load(f)

                    outcome_message = random.choice(success_messages)['message']
                    earned_reward = (outcome_message, reward_type, reward_value)
                    break

            if earned_reward is None:
                outcome_id, reward_type, reward_value, reward_probability = outcomes[0]
                CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                BASE_DIR = os.path.dirname(CURRENT_DIR)
                SUCCESS_PATH = os.path.join(BASE_DIR, "assets", "jobs", "job_success.json")

                with open(SUCCESS_PATH, 'r') as f:
                    success_messages = json.load(f)

                outcome_message = random.choice(success_messages)['message']
                earned_reward = (outcome_message, reward_type, reward_value)

            outcome_message, reward_type, reward_value = earned_reward

            if reward_type == "money":
                reward_value += base_pay  # Add base pay to the reward
                thing = f"⚙{reward_value}"
            elif reward_type == "experience" or reward_type == "item":
                await db_manager.add_money(user_id, base_pay)  # Add the base pay separately
                base_pay_message = f"You also earned your base pay of ⚙{base_pay}."
                if reward_type == "experience":
                    thing = f"⭐{reward_value} XP"
                else:  # reward_type == "item"
                    emoji = await db_manager.get_basic_item_emoji(reward_value)
                    name = await db_manager.get_basic_item_name(reward_value)
                    thing = f"{emoji} {name} (1)"

            result_message = outcome_message.format(user=ctx.author.mention, thing=thing) + " " + base_pay_message

            if reward_type == "money" or reward_type == "experience":
                try:
                    int_reward_value = int(reward_value)
                except ValueError:
                    print(f"Invalid value for {reward_type} reward: {reward_value}")
                    return

                if reward_type == "money":
                    await db_manager.add_money(user_id, int_reward_value)
                if reward_type == "experience":
                    await db_manager.add_xp(user_id, int_reward_value)
                    canLevelUp = await db_manager.can_level_up(user_id)
                    if canLevelUp == True:
                        await db_manager.add_level(user_id, 1)
                        level = await db_manager.get_level(user_id)
                        level = str(level)
                        level = level.replace("(", "")
                        level = level.replace(")", "")
                        level = level.replace(",", "")
                        await ctx.send(f"Congratulations {ctx.author.mention} you have leveled up, you are now level {level}!")

                await asyncio.wait_for(callback_processed_future, timeout=10.0)
                await ctx.send(content=result_message, view=None)
            elif reward_type == "item":
                await db_manager.add_item_to_inventory(user_id, reward_value, 1)
                await asyncio.wait_for(callback_processed_future, timeout=10.0)
                await ctx.send(content=result_message, view=None)

        else:
            CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
            BASE_DIR = os.path.dirname(CURRENT_DIR)
            FAIL_PATH = os.path.join(BASE_DIR, "assets", "jobs", "job_fail.json")

            with open(FAIL_PATH, 'r') as f:
                fail_messages = json.load(f)

            fail_message = random.choice(fail_messages)['message']

            reduced_base_pay = base_pay - (base_pay * penalty_percentage)
            await db_manager.add_money(user_id, reduced_base_pay)  # Give the reduced base pay to the user
            base_pay_message = f"But don't worry, you still get your base pay of ⚙{reduced_base_pay} after a 20% penalty."
            fail_message = fail_message.format(user=ctx.author.mention, thing="Nothing lol")

            await asyncio.wait_for(callback_processed_future, timeout=10.0)
            await ctx.send(content=fail_message + " " + base_pay_message, view=None)
            #add the cooldown

        await db_manager.set_last_worked(user_id)
        await db_manager.add_hours_worked(user_id, 1)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Jobs(bot))