
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

cash = "<:cash:1077573941515792384>"

# Here we name the cog and create a new class for the cog.
class Games(commands.Cog, name="games"):
    def __init__(self, bot):
        self.bot = bot

    # Here we create a new command called "slots".
    @commands.hybrid_command(
        name="slots",
        description="Play a game of slots.",
    )
    async def slots(self, ctx: Context, bet: int):
        await games.slots(ctx, ctx.author, bet)

    #slots rules command
    @commands.hybrid_command(
        name="slotrules",
        description="Shows the rules for slots.",
    )
    async def slotrules(self, ctx: Context):
        await games.slot_rules(ctx)

    @staticmethod
    def hand_to_images(hand: List[Card]) -> List[Image.Image]:
        return ([
            Image.open(os.path.join('assets/pictures/cards/', card.image))
            for card in hand
        ])

    @staticmethod
    def center(*hands: Tuple[Image.Image]) -> Image.Image:
        """Creates blackjack table with cards placed"""
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
        """Calculates the sum of the card values and accounts for aces"""
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


    @commands.hybrid_command(
        name="blackjack",
        description="Play a game of blackjack.",
    )
    async def blackjack(self, ctx: Context, bet: int):
        #make sure bet is valid
        #get the players balance
        #if bet is greater than balance, return
        #if bet is less than 0, return

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
        random.shuffle(deck) # Generate deck and shuffle it
        #give the user a higher chance of drawing a good hand based on their luck stat


        player_hand: List[Card] = []
        dealer_hand: List[Card] = []

        player_hand.append(deck.pop())
        dealer_hand.append(deck.pop())
        player_hand.append(deck.pop())
        dealer_hand.append(deck.pop().flip())
        
        luck = await db_manager.get_luck(ctx.author.id)
        #roll a random number between the luck stat and 100
        luck = random.randint(luck, 100)
        print("Luck: " + str(luck))
        if luck > 99:
            #set the player's hand to 21
            #pick one of the random hands
            #set the player's hand to that hand
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
        print("Player hand: " + str(player_hand))
        player_score = self.calc_hand(player_hand)
        dealer_score = self.calc_hand(dealer_hand)

        async def out_table(**kwargs) -> discord.Message:
            """Sends a picture of the current table"""
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
                str(reaction.emoji) in ("🇸", "🇭"),  # correct emoji
                user == ctx.author,                  # correct user
                user != self.bot.user,           # isn't the bot
                reaction.message == msg            # correct message
            ))

        standing = False

        while True:
            player_score = self.calc_hand(player_hand)
            dealer_score = self.calc_hand(dealer_hand)
            if player_score == 21:  # win condition
                #return 3/2 of the bet
                bet = int(bet*1.5)
                await db_manager.add_money(ctx.author.id, bet)
                result = ("Blackjack!", 'won')
                break
            elif player_score > 21:  # losing condition
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
            
            try:  # reaction command
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

            while dealer_score < 17:  # dealer draws until 17 or greater
                dealer_hand.append(deck.pop())
                dealer_score = self.calc_hand(dealer_hand)

            if dealer_score == 21:  # winning/losing conditions
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
        
        
    #fishing command
    @commands.hybrid_command(
        name="fish",
        description="Go fishing.",
    )
    async def fish(self, ctx: Context):
        #get the users luck stat
        luck = await db_manager.get_luck(ctx.author.id)
        fish = await games.fishing_game()
        await fish(ctx, ctx.author, luck)

async def setup(bot):
    await bot.add_cog(Games(bot))