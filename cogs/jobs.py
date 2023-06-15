import asyncio
from collections import defaultdict
import datetime
import json
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

        # Calculate number of pages based on number of jobs
        num_pages = (len(jobs) // 5) + (1 if len(jobs) % 5 > 0 else 0)

        # Create a function to generate embeds from a list of jobs
        async def create_embeds(job_list):
            num_pages = (len(job_list) // 5) + (1 if len(job_list) % 5 > 0 else 0)
            embeds = []

            for i in range(num_pages):
                start_idx = i * 5
                end_idx = start_idx + 5
                job_embed = discord.Embed(
                    title="Job Board",
                    description=f"Jobs available for {ctx.author.name}. Use /jobinfo <job_id> to get more details.",
                )
                job_embed.set_footer(text=f"Page {i + 1}/{num_pages}")

                for job in job_list[start_idx:end_idx]:
                    job_id = job[0]
                    job_name = job[1]
                    icon = job[2]
                    desc = await db_manager.get_job_description_from_id(job_id)

                    job_embed.add_field(name=f"{icon}**{job_name}**", value=f"{desc} \n ID | `{job_id}`", inline=False)

                embeds.append(job_embed)

            return embeds

        # Create a list of embeds with 5 jobs per embed
        embeds = await create_embeds(jobs)

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

        # Get user's job
        job_id = await db_manager.get_user_job(user_id)
        if job_id is None:
            await ctx.send("You don't have a job!")
            return

        # Get a random minigame for this job
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
        elif minigame[2] == 'Choice':
            selected_option, result, message = await games.play_choice_game(ctx, game_data, minigameText, callback_processed_future)
        else:
            print("Unknown game type")
            return

        if result:
            # Assume user_luck is a value between 0 and 100
            user_luck = await db_manager.get_luck(user_id)

            # Adjust user's luck into scale of 0 to 1
            adjusted_luck = user_luck / 100

            if minigame[2] == 'Choice':
                # Get outcomes based on the selected option
                outcomes = [outcome for option in game_data if option['description'] == selected_option for outcome in option['outcomes']]
                # Sort outcomes by their probabilities
                outcomes = sorted(outcomes, key=lambda x: x['chance'], reverse=True)
            else:
                # Get the rewards and sort them by their probabilities
                outcomes = sorted(await db_manager.get_rewards_for_minigame(minigame[0]), key=lambda x: x[3], reverse=True)

            earned_reward = None

            # Go through the possible outcomes
            for outcome in outcomes:
                if minigame[2] == 'Choice':
                    outcome_id = outcome['id']
                    choice_id = outcome['choice_id']
                    outcome_message = outcome['result']
                    reward_type = outcome['reward_type']
                    reward_value = outcome['reward']
                    reward_probability = outcome['chance']

                else:
                    outcome_id, reward_type, reward_value, reward_probability = outcome
                    outcome_messages = await db_manager.get_results_for_minigame(minigame[0])
                    #pick a random outcome message
                    outcome_message = random.choice(outcome_messages)
                    id, outcome_message = outcome_message

                # Adjust the reward probability with the user's luck
                adjusted_probability = reward_probability + (adjusted_luck * (1 - reward_probability))

                # Roll a random number to see if the user gets this reward
                if random.random() <= adjusted_probability:
                    earned_reward = (outcome_message, reward_type, reward_value)
                    break

            # If no reward was won, default to the one with the highest probability
            if earned_reward is None:
                if minigame[2] == 'Choice':
                    outcome_id, outcome_message, reward_type, reward_value, reward_probability = outcomes[0]
                    earned_reward = (outcome_message, reward_type, reward_value)
                else:
                    outcome_id, reward_type, reward_value, reward_probability = outcomes[0]
                    earned_reward = (outcome_message, reward_type, reward_value)

            result_message, reward_type, reward_value = earned_reward
            reward_message = ""

            reward_embed = discord.Embed(
                title="Work Results",
                description=result_message,
                color=discord.Color.gold()
            )

            if reward_type == "money" or reward_type == "experience":
                # Check if reward_value can be converted into integer
                try:
                    int_reward_value = int(reward_value)
                except ValueError:
                    print(f"Invalid value for {reward_type} reward: {reward_value}")
                    return

                # Add the money or experience to the user's account
                if reward_type == "money":
                    await db_manager.add_money(user_id, int_reward_value) 
                if reward_type == "experience":
                    await db_manager.add_xp(user_id, int_reward_value)
                    canLevelUp = await db_manager.can_level_up(user_id)
                    if canLevelUp == True:
                        await db_manager.add_level(user_id, 1)
                        level = await db_manager.get_level(user_id)
                        level = str(level)
                        #remove the ( and ) and , from the level
                        level = level.replace("(", "")
                        level = level.replace(")", "")
                        level = level.replace(",", "")
                        await ctx.send(f"Congratulations {ctx.author.mention} you have leveled up, you are now level {level}!")

                reward_message = f"You earned {reward_value} {reward_type}!"
                reward_embed.add_field(name="Rewards Earned", value=reward_message, inline=False)
            elif reward_type == "item":
                # Give the item to the user
                await db_manager.add_item_to_inventory(user_id, reward_value, 1)
                reward_message = f"You earned {reward_value}!"
                reward_embed.add_field(name="Rewards Earned", value=reward_message, inline=False)

            await asyncio.wait_for(callback_processed_future, timeout=10.0)  # Adjust the timeout as needed
            await message.edit(embed=reward_embed, view=None)
        else:
            # Inform the user that their answer was incorrect and they can try again later.
            incorrect_embed = discord.Embed(
                title="Unsuccessful Attempt",
                description="I'm sorry, that wasn't right. You can try again later.",
                color=discord.Color.red()
            )
            await asyncio.wait_for(callback_processed_future, timeout=10.0)  # Adjust the timeout as needed
            await message.edit(embed=incorrect_embed, view=None)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Jobs(bot))