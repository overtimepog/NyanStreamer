import asyncio
import datetime
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
from discord import Color, Embed
from discord.ui import Button, View, Select

from helpers import db_manager, battle
import asyncio
import os
import random
from io import BytesIO
from random import shuffle
from typing import List, Tuple, Union

import discord
from discord.ext import commands
from helpers.card import Card
from PIL import Image

cash = "⌬"
slot_spin = "<a:spin:1245491420165312594>"
rarity_colors = {
    "Common": 0x808080,  # Grey
    "Uncommon": 0x319236,  # Green
    "Rare": 0x4c51f7,  # Blue
    "Epic": 0x9d4dbb,  # Purple
    "Legendary": 0xf3af19,  # Gold
    # Add more rarities and colors as needed
}

#slots
async def slots(self, ctx: Context, user, gamble):
    emoji = [
        ":apple:", ":cherries:", ":grapes:", ":lemon:", ":peach:",
        ":tangerine:", ":watermelon:", ":strawberry:", ":banana:",
        ":pineapple:", ":kiwi:", ":pear:", ":crown:", ":gem:",
        ":bell:", ":star:", ":seven:", ":heart:"
    ]
    slot_spin = "<a:spin:1245491420165312594>"
    redo_emoji = "🔁"

    async def update_embed(slot_machine, grid, gamble, result=None, profit=None, win=False, total_balance=None):
        description = "\n".join(" | ".join(row) for row in grid) + f"\n\n **{user.name}** is gambling **{gamble:,}**"
        if result is not None:
            color = 0x00ff00 if win else 0xff0000
            profit_str = f"{int(profit):,}" if isinstance(profit, int) else f"{profit:,.2f}"
            description += f"\n {'Won' if win else 'Lost'}: **{profit_str}**"
            description += f"\n Total Balance: **{total_balance:,}**" if isinstance(total_balance, int) else f"\n Total Balance: **{total_balance:,.2f}**"
            embed = discord.Embed(title="Slot Machine", description=description, color=color)
            embed.set_footer(text="use 🔁 to play again")
            await slot_machine.edit(embed=embed)
            await slot_machine.add_reaction(redo_emoji)
        else:
            embed = discord.Embed(title="Slot Machine", description=description)
            await slot_machine.edit(embed=embed)

    async def spin_slot():
        return random.choice(emoji)

    async def play_slots(user, gamble):
        money = await db_manager.get_money(user.id)
        luck = await db_manager.get_luck(user.id)
        await db_manager.add_money_spent(user.id, gamble)
        money = int(money[0])
        gamble = int(gamble)

        if money < gamble:
            return await ctx.send(f"**{user.name}** doesn't have enough money to gamble **{gamble:,}**.")

        slot_machine = await ctx.send(embed=discord.Embed(
            title="Slot Machine",
            description=f"{slot_spin} | {slot_spin} | {slot_spin}\n{slot_spin} | {slot_spin} | {slot_spin}\n{slot_spin} | {slot_spin} | {slot_spin}\n\n **{user.name}** is gambling **{gamble:,}**"
        ))

        def check(reaction, user_check):
            return user_check == ctx.author and str(reaction.emoji) == redo_emoji and reaction.message.id == slot_machine.id

        grid = [[slot_spin] * 3 for _ in range(3)]
        for col in range(3):
            await asyncio.sleep(1)
            for row in range(3):
                grid[row][col] = await spin_slot()
            await update_embed(slot_machine, grid, gamble)

        winnings = calculate_winnings(grid, gamble)
        net_winnings = winnings - gamble if winnings > 0 else winnings
        profit = net_winnings if net_winnings > 0 else -gamble
        total_balance = money + net_winnings

        if net_winnings > 0:
            await db_manager.add_money(user.id, net_winnings)
            await db_manager.add_money_earned(user.id, net_winnings)
            await update_embed(slot_machine, grid, gamble, result=winnings, profit=profit, win=True, total_balance=total_balance)
        else:
            await db_manager.remove_money(user.id, -net_winnings)  # This is because net_winnings is negative for a loss
            await db_manager.add_money_spent(user.id, gamble)
            await update_embed(slot_machine, grid, gamble, result=winnings, profit=profit, win=False, total_balance=total_balance)

        try:
            reaction, user_check = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await slot_machine.clear_reaction(redo_emoji)
        else:
            await slot_machine.clear_reaction(redo_emoji)
            return await play_slots(user, gamble)

    def calculate_winnings(grid, gamble):
        lines = grid + list(zip(*grid))  # Rows and columns
        diagonals = [[grid[i][i] for i in range(3)], [grid[i][2-i] for i in range(3)]]
        all_lines = lines + diagonals

        for line in all_lines:
            unique_symbols = set(line)
            if len(unique_symbols) == 1:
                symbol = unique_symbols.pop()
                if symbol == ":gem:":
                    return gamble * 8
                elif symbol == ":crown:":
                    return gamble * 6
                elif symbol == ":seven:":
                    return gamble * 5
                elif symbol in [":apple:", ":cherries:", ":grapes:", ":lemon:", ":peach:", ":tangerine:", ":watermelon:", ":strawberry:", ":banana:", ":pineapple:", ":kiwi:", ":pear:"]:
                    return gamble * 3
                else:
                    return gamble * 4

        for line in all_lines:
            if ":gem:" in line:
                return gamble * 2
            elif ":crown:" in line:
                return gamble * 1.5
            elif ":seven:" in line:
                return gamble * 1.2
            elif any(fruit in line for fruit in [":apple:", ":cherries:", ":grapes:", ":lemon:", ":peach:", ":tangerine:", ":watermelon:", ":strawberry:", ":banana:", ":pineapple:", ":kiwi:", ":pear:"]):
                return gamble * 1.1

        if (grid[0][1] == grid[1][1] == grid[2][1] and grid[0][1] in [":apple:", ":cherries:", ":grapes:", ":lemon:", ":peach:", ":tangerine:", ":watermelon:", ":strawberry:", ":banana:", ":pineapple:", ":kiwi:", ":pear:"]):
            return gamble * 4

        if (grid[0][0] == grid[0][2] == grid[2][0] == grid[2][2] and grid[0][0] in [":apple:", ":cherries:", ":grapes:", ":lemon:", ":peach:", ":tangerine:", ":watermelon:", ":strawberry:", ":banana:", ":pineapple:", ":kiwi:", ":pear:"]):
            return gamble * 5

        return -gamble

    await play_slots(user, gamble)

#create slots_rules function
#this function will be called when the user types !slots_rules
# /slots_rules will show the rules of the slots game
# /slots_rules will also show the user how to play the slots game
# /slots_rules will also show the user the rewards for each slot
async def slot_rules(ctx: Context):
    #create the embed
    embed = discord.Embed(
        title="Slots Rules",
        description="Slots is a game where you bet money and spin the slots. If the slots are the same, you win money. If the slots are different, you lose money. \n :gem: | :gem: | :gem: | 10x \n :crown: | :crown: | :crown: | 7.5x \n :apple: | :apple: | :apple: | 5x \n :apple: | :apple: | :question: | 3x \n :gem: | :question: | :question: | 1.5x \n :crown: | :question: | :question: | 1.2x",
        color=discord.Color.blue()
    )
    #send the embed
    await ctx.send(embed=embed)

import logging
import traceback

async def fish(self, ctx, user_luck: int):
    rarity_colors = {
        "Common": 0x808080,
        "Uncommon": 0x319236,
        "Rare": 0x4c51f7,
        "Epic": 0x9d4dbb,
        "Legendary": 0xf3af19,
    }

    rarity_xp = {
        "Common": 10,
        "Uncommon": 20,
        "Rare": 50,
        "Epic": 100,
        "Legendary": 200,
    }

    async def catch_fish(user_luck):
        try:
            fishes = await db_manager.get_fish_from_db()
        except Exception as e:
            logging.error(f"Error fetching fish from DB: {e}\n{traceback.format_exc()}")
            await ctx.send("An error occurred while fetching fish data.")
            return None

        # Select fishes based on the user's luck and the fish's catch rate
        catchable_fishes = [fish for fish in fishes if random.randint(1, 100) <= (fish[2] + user_luck)]
        if not catchable_fishes:
            catchable_fishes = fishes
        return random.choice(catchable_fishes)

    equipped_items = await db_manager.get_equipped_items(ctx.author.id)
    equipped_baits = [item for item in equipped_items if item[1].startswith('bait_')]
    
    if not equipped_baits:
        await ctx.send("You don't have any bait equipped to go fishing.")
        return

    equipped_baits.sort(key=lambda x: x[3], reverse=True)  # Assuming the price is at index 3
    selected_bait = equipped_baits[0]

    try:
        initial_bait_amount = await db_manager.get_item_amount_from_inventory(ctx.author.id, selected_bait[1])
    except Exception as e:
        logging.error(f"Error fetching bait amount: {e}\n{traceback.format_exc()}")
        await ctx.send("An error occurred while fetching bait data.")
        return

    if initial_bait_amount == 0:
        await ctx.send("You don't have any bait to go fishing.")
        return

    max_catches = 5
    catches = {}
    total_xp = 0
    fish_caught = 0
    bait_amount = initial_bait_amount

    while bait_amount > 0 and fish_caught < max_catches:
        caught_fish = await catch_fish(user_luck)
        if not caught_fish:
            continue

        item_id = caught_fish[0]
        if item_id in catches:
            catches[item_id] += 1
        else:
            catches[item_id] = 1

        try:
            await db_manager.remove_item_from_inventory(ctx.author.id, selected_bait[1], 1)
            bait_amount -= 1
        except Exception as e:
            logging.error(f"Error removing bait from inventory: {e}\n{traceback.format_exc()}")
            await ctx.send("An error occurred while removing bait from your inventory.")
            return

        fish_caught += 1

    description = "**YOU CAUGHT: ** \n"
    for fish_id, count in catches.items():
        try:
            fish_data = await db_manager.get_basic_item_data(fish_id)
        except Exception as e:
            logging.error(f"Error fetching fish data: {e}\n{traceback.format_exc()}")
            await ctx.send("An error occurred while fetching fish data.")
            continue

        fish_emoji = fish_data["item_emoji"]  # Assuming emoji is at index 3
        fish_name = fish_data["item_name"]  # Assuming name is at index 1
        fish_rarity = fish_data["item_rarity"]  # Assuming rarity is at index 4
        xp_gained = rarity_xp.get(fish_rarity, 0) * count
        total_xp += xp_gained

        description += f"{count} {fish_emoji}{fish_name} - XP: {xp_gained}\n"
        try:
            await db_manager.add_item_to_inventory(ctx.author.id, fish_id, count)
        except Exception as e:
            logging.error(f"Error adding item to inventory: {e}\n{traceback.format_exc()}")
            await ctx.send("An error occurred while adding items to your inventory.")
            continue

    try:
        await db_manager.add_xp(ctx.author.id, total_xp)
    except Exception as e:
        logging.error(f"Error adding XP: {e}\n{traceback.format_exc()}")
        await ctx.send("An error occurred while adding XP.")
        return

    description += f"\nTotal XP gained: {total_xp}"
    # Level the user up if they have enough XP
    canLevelUp = await db_manager.can_level_up(ctx.author.id)
    if canLevelUp:
        await db_manager.add_level(ctx.author.id, 1)
        new_level = await db_manager.get_level(ctx.author.id)
        description += f"\n{ctx.author.mention} has leveled up! They are now level " + str(new_level) + "!"

    embed = discord.Embed(
        title=f"{ctx.author.name}",
        description=description,
    )

    bait_used = initial_bait_amount - bait_amount
    embed.set_footer(text=f"\nTotal bait used: {bait_used} | Remaining bait: {bait_amount}")

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Sell Fish", style=discord.ButtonStyle.primary, custom_id="sell_fish"))
    view.add_item(discord.ui.Button(label="Replay", style=discord.ButtonStyle.primary, custom_id="replay_fish"))
    view.add_item(discord.ui.Button(label="Return", style=discord.ButtonStyle.danger, custom_id="return"))

    message = await ctx.send(embed=embed, view=view)

    async def sell_fish(interaction: discord.Interaction):
        total_earned = 0
        sell_description = "**YOU SOLD: **\n"
        for fish_id, count in catches.items():
            try:
                fish_data = await db_manager.get_basic_item_data(fish_id)
                fish_price = fish_data['item_price']
                earned = int(fish_price) * count
                total_earned += earned
                await db_manager.remove_item_from_inventory(ctx.author.id, fish_id, count)

                fish_emoji = fish_data["item_emoji"]  # Assuming emoji is at index 3
                fish_name = fish_data["item_name"]  # Assuming name is at index 1
                sell_description += f"{count} {fish_emoji}{fish_name} - ⌬{earned}\n"
            except Exception as e:
                logging.error(f"Error processing sell fish: {e}\n{traceback.format_exc()}")
                await interaction.response.send_message("An error occurred while selling fish.")
                return

        try:
            await db_manager.add_money(ctx.author.id, total_earned)
            money = await db_manager.get_money(ctx.author.id)
        except Exception as e:
            logging.error(f"Error adding money: {e}\n{traceback.format_exc()}")
            await interaction.response.send_message("An error occurred while adding money.")
            return
        #turn money into a string, remove the ( ) and , and turn it into an int
        money = int(str(money).replace("(", "").replace(")", "").replace(",", ""))
        sell_description += f"\nTotal money earned from selling: ⌬{total_earned} | You now have ⌬{money}"
        sell_embed = discord.Embed(
            title=f"{ctx.author.name}",
            description=sell_description,
        )

        sell_view = discord.ui.View()
        sell_view.add_item(discord.ui.Button(label="Replay", style=discord.ButtonStyle.primary, custom_id="replay_fish"))
        sell_view.add_item(discord.ui.Button(label="Return", style=discord.ButtonStyle.danger, custom_id="return"))

        await interaction.response.edit_message(embed=sell_embed, view=sell_view)

    def button_check(interaction: discord.Interaction) -> bool:
        return interaction.data.get('custom_id') in ["sell_fish", "replay_fish", "return"] and interaction.user == ctx.author

    try:
        while True:
            interaction = await self.bot.wait_for("interaction", timeout=60.0, check=button_check)
            if interaction.data.get('custom_id') == "sell_fish":
                await sell_fish(interaction)
            elif interaction.data.get('custom_id') == "replay_fish":
                await interaction.response.defer()
                await fish(self, ctx, user_luck)
                break
            elif interaction.data.get('custom_id') == "return":
                await interaction.response.defer()
                await interaction.message.delete()
                break
    except asyncio.TimeoutError:
        await message.delete()
    except Exception as e:
        logging.error(f"Error handling interaction: {e}\n{traceback.format_exc()}")
        await ctx.send("An unknown error occurred during the interaction.")

class TriviaButton(Button):
    def __init__(self, label, trivia_view, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.trivia_view = trivia_view

    async def callback(self, interaction: discord.Interaction):
        selected_choice = self.label
        if selected_choice == self.trivia_view.answer:
            color = discord.Color.green()
            text = f"Correct! The answer was {self.trivia_view.answer}."
            self.style = discord.ButtonStyle.success
            #give the user a prize and some xp
            #decide if the user is gonna get a chest or pet chest
            random_number = random.randint(1, 100)
            if random_number <= 5:
                await db_manager.add_item_to_inventory(interaction.user.id, "pet_chest", 1)
                await db_manager.add_xp(interaction.user.id, 50)
                pet_chest_emoji = await db_manager.get_chest_icon("pet_chest")
                await interaction.message.reply(f"{interaction.user.mention} got a {pet_chest_emoji}Pet Chest and ⭐50 xp!")
                canLevelUp = await db_manager.can_level_up(interaction.user.id)
                if canLevelUp:
                    await db_manager.add_level(interaction.user.id, 1)
                    new_level = await db_manager.get_level(interaction.user.id)
                    await interaction.message.reply(f"{interaction.user.mention} has leveled up! They are now level " + str(new_level) + "!")
            else:
                await db_manager.add_item_to_inventory(interaction.user.id, "chest", 1)
                await db_manager.add_xp(interaction.user.id, 10)
                chest_emoji = await db_manager.get_chest_icon("chest")
                await interaction.message.reply(f"{interaction.user.mention} got a {chest_emoji}Chest and ⭐10 xp!")
                #check if the user can level up 
                canLevelUp = await db_manager.can_level_up(interaction.user.id)
                if canLevelUp:
                    await db_manager.add_level(interaction.user.id, 1)
                    new_level = await db_manager.get_level(interaction.user.id)
                    await interaction.message.reply(f"{interaction.user.mention} has leveled up! They are now level " + str(new_level) + "!")



        else:
            color = discord.Color.red()
            text = f"Sorry, that's incorrect. The correct answer was {self.trivia_view.answer}."
            self.style = discord.ButtonStyle.danger

        embed = interaction.message.embeds[0]
        embed.color = color
        embed.set_footer(text=text)
        await interaction.message.edit(embed=embed, view=None)

class TriviaView(View):
    def __init__(self, answer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.answer = answer

    def add_choice(self, choice):
        self.add_item(TriviaButton(label=choice, trivia_view=self, style=discord.ButtonStyle.secondary))


async def trivia(self, ctx: commands.Context):
        def load_questions(filename):
            with open(filename, 'r') as file:
                data = json.load(file)
            return data

        math = load_questions('assets/items/puzzles/math.json')
        random_math_question = random.choice(math['mathPuzzles'])
        math_problem = random_math_question['problem']
        math_choices = random_math_question['choices']
        math_answer = random_math_question['answer']

        riddles = load_questions('assets/items/puzzles/riddles.json')
        random_riddle_question = random.choice(riddles['riddles'])
        riddle = random_riddle_question['riddle']
        riddle_choices = random_riddle_question['choices']
        riddle_answer = random_riddle_question['answer']

        sequences = load_questions('assets/items/puzzles/sequence.json')
        random_sequence_question = random.choice(sequences['sequencePuzzles'])
        sequence = random_sequence_question['sequence']
        sequence_choices = random_sequence_question['choices']
        sequence_answer = random_sequence_question['answer']

        word_puzzles = load_questions('assets/items/puzzles/word.json')
        random_word_question = random.choice(word_puzzles['wordPuzzles'])
        word_problem = random_word_question['problem']
        word_choices = random_word_question['choices']
        word_answer = random_word_question['answer']

        # Load the logic puzzles
        logic_puzzles = load_questions('assets/items/puzzles/logic.json')
        random_logic_question = random.choice(logic_puzzles['logicPuzzles'])
        logic_problem = random_logic_question['problem']
        logic_choices = random_logic_question['choices']
        logic_answer = random_logic_question['answer']

        puzzles = [
            {"type": "Math Problem", "question": math_problem, "choices": math_choices, "answer": math_answer},
            {"type": "Riddle", "question": riddle, "choices": riddle_choices, "answer": riddle_answer},
            {"type": "Sequence", "question": sequence, "choices": sequence_choices, "answer": sequence_answer},
            {"type": "Word Puzzle", "question": word_problem, "choices": word_choices, "answer": word_answer},
            {"type": "Logic Puzzle", "question": logic_problem, "choices": logic_choices, "answer": logic_answer}
        ]

        selected_puzzle = random.choice(puzzles)

        embed = Embed(
            title=f"{selected_puzzle['type']}",
            description=f"{selected_puzzle['question']}",
            color=discord.Color.blue()
        )

        view = TriviaView(selected_puzzle['answer'])

        for choice in selected_puzzle['choices']:
            view.add_choice(choice)

        await ctx.send(embed=embed, view=view)

# -------------------- for WORK COMMAND --------------------

class TriviaGameView(View):
    def __init__(self, answer, resolve_callback, callback_processed_future, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.answer = answer
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.user.id:
            return True
        return False

    def add_choice(self, choice):
        self.add_item(TriviaGameButton(label=choice, trivia_view=self, callback_processed_future=self.callback_processed_future, style=discord.ButtonStyle.secondary))

class TriviaGameButton(Button):
    def __init__(self, label, trivia_view, callback_processed_future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.trivia_view = trivia_view
        self.callback_processed_future = callback_processed_future

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        selected_choice = self.label
        if not self.trivia_view.resolve_callback.done():
            if selected_choice == self.trivia_view.answer:
                self.style = discord.ButtonStyle.success
                self.trivia_view.resolve_callback.set_result(True)
                try:
                    await interaction.response.defer()
                except(discord.errors.InteractionResponded):
                    pass
            else:
                self.style = discord.ButtonStyle.danger
                self.trivia_view.resolve_callback.set_result(False)
                try:
                    await interaction.response.defer()
                except(discord.errors.InteractionResponded):
                    pass
                
        # Check if callback_processed_future is done before trying to set its result
        if not self.callback_processed_future.done():
            self.callback_processed_future.set_result(True)
            try:
                await interaction.response.defer()
            except(discord.errors.InteractionResponded):
                pass

async def play_trivia(ctx, game_data, minigameText, callback_processed_future):
    random_trivia = random.choice(game_data)
    trivia_question = random_trivia[1]  # accessing the second element of tuple
    trivia_choices = json.loads(random_trivia[2])  # accessing the third element of tuple
    trivia_answer = random_trivia[3]

    resolve_promise = ctx.bot.loop.create_future()

    view = TriviaGameView(answer=trivia_answer, resolve_callback=resolve_promise, callback_processed_future=callback_processed_future, user=ctx.author)

    random.shuffle(trivia_choices)  # Shuffle the choices

    for choice in trivia_choices:
        view.add_choice(choice)

    sendingMessage = minigameText + "\n" + f"`{trivia_question}`"

    message = await ctx.reply(content=sendingMessage, view=view)
    try:
        result = await asyncio.wait_for(resolve_promise, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.reply("Time's up!")
        result = False

    return result, message

class OrderGameSelect(Select):
    def __init__(self, correct_order, resolve_callback, callback_processed_future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_order = correct_order
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future

    async def callback(self, interaction: discord.Interaction):
        user_order = self.values

        if user_order == self.correct_order:
            self.resolve_callback.set_result(True)
            try:
                await interaction.response.defer()
            except(discord.errors.InteractionResponded):
                pass
        else:
            self.resolve_callback.set_result(False)
            try:
                await interaction.response.defer()
            except(discord.errors.InteractionResponded):
                pass

        self.callback_processed_future.set_result(True)
        try:
            await interaction.response.defer()
        except(discord.errors.InteractionResponded):
            pass

async def play_order_game(ctx, game_data, minigameText, callback_processed_future):
    game = random.choice(game_data)
    print(game)
    correct_order = json.loads(game[3])  # accessing the second element of tuple
    items = json.loads(game[2])

    resolve_promise = ctx.bot.loop.create_future()
    select_menu = OrderGameSelect(correct_order=correct_order, resolve_callback=resolve_promise, callback_processed_future=callback_processed_future, placeholder="Select the correct order", max_values=len(items), options=[discord.SelectOption(label=item, value=item) for item in items])

    view = View()
    view.add_item(select_menu)

    sendingMessage = minigameText + "\n" + game[1]
    message = await ctx.reply(content=sendingMessage, view=view)

    try:
        result = await asyncio.wait_for(resolve_promise, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.reply("Time's up!")
        result = False

    return result, message

class MatchingGameSelect(Select):
    def __init__(self, correct_match, resolve_callback, callback_processed_future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_match = correct_match
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future

    async def callback(self, interaction: discord.Interaction):
        user_match = self.values[0]

        if user_match == self.correct_match:
            self.resolve_callback.set_result(True)
            try:
                await interaction.response.defer()
            except(discord.errors.InteractionResponded):
                pass
        else:
            self.resolve_callback.set_result(False)
            try:
                await interaction.response.defer()
            except(discord.errors.InteractionResponded):
                pass

        self.callback_processed_future.set_result(True)
        try:
            await interaction.response.defer()
        except(discord.errors.InteractionResponded):
            pass

async def play_matching_game(ctx, game_data, minigameText, callback_processed_future):
    game = random.choice(game_data)
    print(game)
    items = json.loads(game[1])  # accessing the second element of tuple
    correct_matches = json.loads(game[2])

    target = random.choice(items)

    correct_description = [item['description'] for item in correct_matches if item['name'] == target['name']][0]

    other_descriptions = [item['description'] for item in items if item['name'] != target['name']]
    random.shuffle(other_descriptions)
    descriptions = [correct_description] + other_descriptions[:3]
    random.shuffle(descriptions)

    resolve_promise = ctx.bot.loop.create_future()
    select_menu = MatchingGameSelect(correct_match=correct_description, resolve_callback=resolve_promise, callback_processed_future=callback_processed_future, placeholder="Match the item", options=[discord.SelectOption(label=desc, value=desc) for desc in descriptions])

    view = discord.ui.View()
    view.add_item(select_menu)

    sendingMessage = minigameText + "\n" + "Match the item: " + target['name']
    message = await ctx.reply(content=sendingMessage, view=view)

    try:
        result = await asyncio.wait_for(resolve_promise, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.reply("Time's up!")
        result = False

    return result, message

class ChoiceGameButton(Button):
    def __init__(self, label, resolve_callback, callback_processed_future, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future

    async def callback(self, interaction: discord.Interaction):
        self.resolve_callback.set_result(self.label)  # Return the label of the selected option
        self.callback_processed_future.set_result(True)
        try:
            await interaction.response.defer()
        except(discord.errors.InteractionResponded):
            pass

class ChoiceGameView(View):
    def __init__(self, resolve_callback, callback_processed_future, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolve_callback = resolve_callback
        self.callback_processed_future = callback_processed_future
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.user.id:
            return True
        return False

    def add_choice(self, choice):
        self.add_item(ChoiceGameButton(label=choice, resolve_callback=self.resolve_callback, callback_processed_future=self.callback_processed_future, style=discord.ButtonStyle.secondary))

async def play_choice_game(ctx, game_data, minigameText, callback_processed_future):
    prompt = game_data[0]['minigame_id']

    resolve_promise = ctx.bot.loop.create_future()
    view = ChoiceGameView(resolve_callback=resolve_promise, callback_processed_future=callback_processed_future, user=ctx.author)

    for game_option in game_data:
        view.add_choice(game_option['description'])

    sendingMessage = minigameText + "\n" + "Choose your action"
    message = await ctx.reply(content=sendingMessage, view=view)

    try:
        result = await asyncio.wait_for(resolve_promise, timeout=60.0)
        game_outcomes = next((option['outcomes'] for option in game_data if option['description'] == result), None)
    except asyncio.TimeoutError:
        await ctx.reply("Time's up!")
        result = False
        game_outcomes = None

    return result, game_outcomes, message

async def play_retype_game(ctx, game_data, minigameText, callback_processed_future):
    game = random.choice(game_data)
    phrase = game[1]  # accessing the second element of tuple

    sendingMessage = minigameText + "\n" + "Retype this phrase: `" + phrase + "`"
    await ctx.send(content=sendingMessage)

    def check(m):
        return m.author == ctx.author

    try:
        message = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        if message.content == phrase:
            result = True
        else:
            result = False
    except asyncio.TimeoutError:
        await ctx.reply("Time's up!")
        result = False
    finally:
        callback_processed_future.set_result(result)  # set the future's result to the game result

    return result, message


async def play_backwards_game(ctx, game_data, minigameText, callback_processed_future):
    try:
        game = random.choice(game_data)
        print(game)
        word = game[1]  # accessing the second element of tuple
    except IndexError:
        await ctx.reply("There are no words to play this game!")
        return False

    print(word)
    reversed_word = ' '.join(w[::-1] for w in word.split())  # Reverse each word separately

    sendingMessage = minigameText + "\n" + "Type this word backwards: `" + word + "`"
    await ctx.send(content=sendingMessage)

    def check(m):
        return m.author == ctx.author

    try:
        message = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        if message.content == reversed_word:
            result = True
        else:
            result = False
    except asyncio.TimeoutError:
        await ctx.reply("Time's up!")
        result = False
    finally:
        callback_processed_future.set_result(result)  # set the future's result to the game result

    return result, message

class HangmanGame:
    def __init__(self, ctx, word, sentence, minigameText, callback_processed_future, attempts=7):
        self.ctx = ctx
        self.word = word
        self.sentence = sentence
        self.attempts = attempts
        self.minigameText = minigameText
        self.guessed_letters = []
        self.blanks = ['_']*len(self.word)  # Simplify blank creation
        self.callback_processed_future = callback_processed_future

    async def play(self):
        # Display initial state
        embed = Embed(color=discord.Color.dark_purple())
        embed.add_field(name="State", value=self.get_message(), inline=False)
        embed.add_field(name="Info", value="Please guess a letter.", inline=False)
        embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
        message = await self.ctx.send(content=self.minigameText, embed=embed)
        result = False

        while self.attempts > 0 and '_' in self.blanks:
            try:
                guess = await self.ctx.bot.wait_for('message', check=self.check_message, timeout=60.0)
            except asyncio.TimeoutError:
                embed.set_field_at(0, name="State", value='Time out! Game over.', inline=False)
                await message.edit(embed=embed)
                break

            letter = guess.content.lower()

            if letter in self.guessed_letters:
                update = 'You have already guessed this letter.'
            elif letter in self.word:
                for i, l in enumerate(self.word):
                    if l == letter:
                        self.blanks[i] = letter
                update = 'Correct guess.'
            else:
                self.attempts -= 1
                update = 'Incorrect guess.'

            self.guessed_letters.append(letter)

            # Update game state
            embed.set_field_at(0, name="State", value=self.get_message(), inline=False)
            embed.set_field_at(1, name="Info", value=f"{update} Please guess another letter.", inline=False)
            await message.edit(embed=embed)

            # Delete user's guess message
            await guess.delete()

        if '_' not in self.blanks:
            embed.set_field_at(0, name="State", value='Congratulations! You have guessed the word.', inline=False)
            await message.edit(embed=embed)
            result = True
        else:
            embed.set_field_at(0, name="State", value='Game over. You have not guessed the word.', inline=False)
            await message.edit(embed=embed)
            result = False

        # Set callback_processed_future result here
        self.callback_processed_future.set_result(result)

    def get_message(self):
        blanks_string = ''.join(self.blanks)
        return f"{self.sentence.replace('{word}', f'`{blanks_string}`')}\nAttempts left: {self.attempts}"

    def check_message(self, message):
        return message.author == self.ctx.author and len(message.content) == 1 and message.content.isalpha()


# Somewhere in your command
async def play_hangman_game(ctx, game_data, minigameText, callback_processed_future):
    game = random.choice(game_data)
    sentence = game[1]  # accessing the second element of tuple
    word = game[2]  # accessing the third element of tuple

    hangman = HangmanGame(ctx, word, sentence, minigameText, callback_processed_future)
    await hangman.play()
    return callback_processed_future.result(), ctx.message


async def play_anagram_game(ctx, game_data, minigameText, callback_processed_future):
    game = random.choice(game_data)
    scrambled_word = game[1]  # accessing the second element of tuple
    solution = game[2]  # accessing the third element of tuple

    sendingMessage = minigameText + "\n" + "Unscramble this word: `" + scrambled_word + "`"
    await ctx.send(content=sendingMessage)

    def check(m):
        return m.author == ctx.author

    try:
        message = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        if message.content.lower() == solution.lower():  # Comparing ignoring case
            result = True
        else:
            result = False
    except asyncio.TimeoutError:
        await ctx.reply("Time's up!")
        result = False
    finally:
        callback_processed_future.set_result(result)  # set the future's result to the game result

    return result, message