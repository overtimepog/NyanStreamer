
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

cash = "⌬"

# Here we name the cog and create a new class for the cog.
class Games(commands.Cog, name="games"):
    def __init__(self, bot):
        self.bot = bot

    # Here we create a new command called "slots".
    @commands.hybrid_group(
        name="slots",
        description="Play a game of slots.",
        aliases=['slot']
    )
    async def slots(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    #slots play command
    @slots.command(
        name="play",
        description="Play a game of slots.",
    )
    async def play(self, ctx: Context, bet: int):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return
        await games.slots(self, ctx, ctx.author, bet)

    #slots rules command
    @slots.command(
        name="rules",
        description="Shows the rules for slots.",
    )
    async def rules(self, ctx: Context):
        await games.slot_rules(ctx)

    @staticmethod
    def hand_to_images(hand: List[Card]) -> List[Image.Image]:
        return ([
            Image.open(os.path.join('assets/pictures/cards/', card.image))
            for card in hand
        ])

    @staticmethod
    def center(*hands: Tuple[Image.Image]) -> Image.Image:
        bg: Image.Image = Image.open(
            os.path.join('assets/pictures/table.png')
        )
        bg_center_x = bg.size[0] // 2
        bg_center_y = bg.size[1] // 2

        img_w = hands[0][0].size[0]
        img_h = hands[0][0].size[1]

        start_y = bg_center_y - (((len(hands)*img_h) + \
            ((len(hands) - 1) * 15)) // 2)
        for hand in hands:
            start_x = bg_center_x - (((len(hand)*img_w) + \
                ((len(hand) - 1) * 10)) // 2)
            for card in hand:
                bg.alpha_composite(card, (start_x, start_y))
                start_x += img_w + 10
            start_y += img_h + 15
        return bg

    def output(self, name, *hands: Tuple[List[Card]]) -> None:
        self.center(*map(self.hand_to_images, hands)).save(f'{name}.png')

    @staticmethod
    def calc_hand(hand: List[List[Card]]) -> int:
        non_aces = [c for c in hand if c.symbol != 'A']
        aces = [c for c in hand if c.symbol == 'A']
        sum = 0
        for card in non_aces:
            if not card.down:
                if card.symbol in 'JQK': sum += 10
                else: sum += card.value
        for card in aces:
            if not card.down:
                if sum <= 10: sum += 11
                else: sum += 1
        return sum

    async def blackjack_game(self, ctx: Context, bet: int):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return

        user_cash = await db_manager.get_money(ctx.author.id)
        user_cash = int(user_cash[0])
        if bet > user_cash:
            await ctx.send(f"You don't have enough money to bet that much.")
            return
        elif bet < 0:
            await ctx.send(f"You can't bet a negative amount.")
            return
        elif bet == 0:
            await ctx.send(f"You can't bet nothing.")
            return
        deck = [Card(suit, num) for num in range(2,15) for suit in Card.suits]
        random.shuffle(deck)

        player_hand: List[Card] = []
        dealer_hand: List[Card] = []

        player_hand.append(deck.pop())
        dealer_hand.append(deck.pop())
        player_hand.append(deck.pop())
        dealer_hand.append(deck.pop().flip())
        
        luck = await db_manager.get_luck(ctx.author.id)
        luck = random.randint(luck, 100)
        if luck > 99:
            blackjackHands = [
                [Card("D", 10), Card("S", 14)], 
                [Card("C", 10), Card("D", 14)], 
                [Card("H", 10), Card("C", 14)], 
                [Card("S", 10), Card("D", 14)], 
                [Card("D", 10), Card("H", 14)], 
                [Card("C", 10), Card("S", 14)],
                [Card("D", 14), Card("S", 10)], 
                [Card("C", 14), Card("D", 10)], 
                [Card("H", 14), Card("C", 10)], 
                [Card("S", 14), Card("D", 10)], 
                [Card("D", 14), Card("H", 10)], 
                [Card("C", 14), Card("S", 10)],
                [Card("D", 11), Card("S", 14)], 
                [Card("C", 11), Card("D", 14)], 
                [Card("H", 11), Card("C", 14)], 
                [Card("S", 11), Card("D", 14)], 
                [Card("D", 11), Card("H", 14)], 
                [Card("C", 11), Card("S", 14)],
                [Card("D", 14), Card("S", 11)], 
                [Card("C", 14), Card("D", 11)], 
                [Card("H", 14), Card("C", 11)], 
                [Card("S", 14), Card("D", 11)], 
                [Card("D", 14), Card("H", 11)], 
                [Card("C", 14), Card("S", 11)],
                [Card("D", 12), Card("S", 14)], 
                [Card("C", 12), Card("D", 14)], 
                [Card("H", 12), Card("C", 14)], 
                [Card("S", 12), Card("D", 14)], 
                [Card("D", 12), Card("H", 14)], 
                [Card("C", 12), Card("S", 14)],
                [Card("D", 14), Card("S", 12)], 
                [Card("C", 14), Card("D", 12)], 
                [Card("H", 14), Card("C", 12)], 
                [Card("S", 14), Card("D", 12)], 
                [Card("D", 14), Card("H", 12)], 
                [Card("C", 14), Card("S", 12)],
                [Card("D", 13), Card("S", 14)], 
                [Card("C", 13), Card("D", 14)], 
                [Card("H", 13), Card("C", 14)], 
                [Card("S", 13), Card("D", 14)], 
                [Card("D", 13), Card("H", 14)], 
                [Card("C", 13), Card("S", 14)],
                [Card("D", 14), Card("S", 13)], 
                [Card("C", 14), Card("D", 13)], 
                [Card("H", 14), Card("C", 13)], 
                [Card("S", 14), Card("D", 13)], 
                [Card("D", 14), Card("H", 13)], 
                [Card("C", 14), Card("S", 13)],
            ]
            player_hand = random.choice(blackjackHands)
        
        player_score = self.calc_hand(player_hand)
        dealer_score = self.calc_hand(dealer_hand)

        async def out_table(**kwargs) -> discord.Message:
            self.output(ctx.author.id, dealer_hand, player_hand)
            embed = make_embed(**kwargs)
            file = discord.File(
                f"{ctx.author.id}.png", filename=f"{ctx.author.id}.png"
            )
            embed.set_image(url=f"attachment://{ctx.author.id}.png")
            msg: discord.Message = await ctx.send(file=file, embed=embed)
            return msg
        
        def check(
            reaction: discord.Reaction,
            user: Union[discord.Member, discord.User]
        ) -> bool:
            return all((
                str(reaction.emoji) in ("🇸", "🇭"), 
                user == ctx.author,                  
                user != self.bot.user,           
                reaction.message == msg            
            ))

        standing = False

        while True:
            player_score = self.calc_hand(player_hand)
            dealer_score = self.calc_hand(dealer_hand)
            if player_score == 21:
                bet = int(bet*1.5)
                await db_manager.add_money(ctx.author.id, bet)
                result = ("Blackjack!", 'won')
                break
            elif player_score > 21:
                await db_manager.remove_money(ctx.author.id, bet)
                result = ("Player busts", 'lost')
                break
            msg = await out_table(
                title="Your Turn",
                description=f"Your hand: {player_score}\n" \
                    f"Dealer's hand: {dealer_score}"
            )
            await msg.add_reaction("🇭")
            await msg.add_reaction("🇸")
            
            try:
                reaction, _ = await self.bot.wait_for(
                    'reaction_add', timeout=60, check=check
                )
            except asyncio.TimeoutError:
                await msg.delete()

            if str(reaction.emoji) == "🇭":
                player_hand.append(deck.pop())
                await msg.delete()
                continue
            elif str(reaction.emoji) == "🇸":
                standing = True
                break

        if standing:
            dealer_hand[1].flip()
            player_score = self.calc_hand(player_hand)
            dealer_score = self.calc_hand(dealer_hand)

            while dealer_score < 17:
                dealer_hand.append(deck.pop())
                dealer_score = self.calc_hand(dealer_hand)

            if dealer_score == 21:
                await db_manager.remove_money(ctx.author.id, bet)
                result = ('Dealer blackjack', 'lost')
            elif dealer_score > 21:
                await db_manager.add_money(ctx.author.id, bet)
                result = ("Dealer busts", 'won')
            elif dealer_score == player_score:
                result = ("Tie!", 'kept')
            elif dealer_score > player_score:
                await db_manager.remove_money(ctx.author.id, bet)
                result = ("You lose!", 'lost')
            elif dealer_score < player_score:
                await db_manager.add_money(ctx.author.id, bet)
                result = ("You win!", 'won')

        color = (
            discord.Color.red() if result[1] == 'lost'
            else discord.Color.green() if result[1] == 'won'
            else discord.Color.blue()
        )
        try:
            await msg.delete()
        except:
            pass
        msg = await out_table(
            title=result[0],
            color=color,
            description=(
                f"**You {result[1]} {cash}{bet}**\nYour hand: {player_score}\n" +
                f"Dealer's hand: {dealer_score}"
            )
        )
        os.remove(f'./{ctx.author.id}.png')

        # Add replay button
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Replay", style=discord.ButtonStyle.primary, custom_id="replay_blackjack"))

        replay_message = await ctx.send("Do you want to play again?", view=view)

        def button_check(interaction: discord.Interaction) -> bool:
            return interaction.custom_id == "replay_blackjack" and interaction.user == ctx.author

        try:
            interaction = await self.bot.wait_for("interaction", timeout=60.0, check=button_check)
            if interaction.custom_id == "replay_blackjack":
                await replay_message.delete()
                await self.blackjack_game(ctx, bet)
        except asyncio.TimeoutError:
            await replay_message.edit(content="Replay timed out.", view=None)

    @commands.hybrid_command(
        name="blackjack",
        description="Play a game of blackjack.",
        aliases=['bj']
    )
    async def blackjack(self, ctx: Context, bet: int):
        await Games.blackjack_game(ctx, bet)
        
        
    #fishing command
    @commands.hybrid_command(
        name="fish",
        description="Go fishing.",
    )
    async def fish(self, ctx: Context):
        #get the users luck stat
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return
        luck = await db_manager.get_luck(ctx.author.id)
        await games.fish(self, ctx, luck)

    #puzzle command
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.hybrid_command(
        name="puzzle",
        description="Solve a puzzle for a prize",
        aliases=['puz']
    )
    async def puzzle(self, ctx: Context):
        checkUser = await db_manager.check_user(ctx.author.id)
        if checkUser == None or checkUser == False or checkUser == [] or checkUser == "None" or checkUser == 0:
            await ctx.send("You are not in the database yet, please use the `s.start or /start` command to start your adventure!")
            return
        await games.trivia(self, ctx)

async def setup(bot):
    await bot.add_cog(Games(bot))