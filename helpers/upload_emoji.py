from typing import Union
from helpers.context import CustomContext
from utils.colour import Colour
from cogs.draw import DrawView
from utils.emoji_cache import EmojiCache
from helpers.constants import LOG_BORDER, NL
from helpers.keep_alive import keep_alive
from bot import bot
import discord
from discord.ext import commands

emoji_cache: EmojiCache = EmojiCache(bot=bot)
print("Emoji cache created.")

EMOJI_SERVER_IDS = [
        # 1095209373627846706,
        # 1095209373627846706,
        # 1095209396675559557,
        # 1095209424454418522,
        # 1095209448810749974,
        # 1095211521136656457,
        # 1095211546025656340,
        # 1095211570264559696,
        # 1095211594289528884,
        # 1095212928959004694,
        1124233463843795014,
    ]
print("Emoji server IDs set.")

EMOJI_SERVERS = [
    await bot.fetch_guild(_id) for _id in EMOJI_SERVER_IDS
]
print("Emoji servers fetched.")
    
async def upload_emoji(
            self, colour: Colour, *, draw_view: DrawView, interaction: discord.Interaction
        ) -> Union[discord.Emoji, discord.PartialEmoji]:
            print("upload_emoji function started.")
            # First look if there is cache of the emoji
            if (emoji := emoji_cache.get_emoji(colour.hex)) is not None:
                print("Emoji found in cache.")
                return emoji

            async with draw_view.disable(interaction=interaction):
                print("Draw view disabled.")
                # Look if emoji already exists in a server
                guild_emoji_lists = []
                for guild in EMOJI_SERVERS:
                    guild_emojis = await guild.fetch_emojis()
                    guild_emoji_lists.append(guild_emojis)
                    print(f"Fetched emojis for guild {guild}.")
                    for guild_emoji in guild_emojis:
                        if colour.hex == guild_emoji.name:
                            emoji_cache.add_emoji(guild_emoji)
                            print("Emoji found in guild and added to cache.")
                            return guild_emoji

                # Emoji does not exist already, proceed to create
                for guild in EMOJI_SERVERS:
                    try:
                        emoji = await colour.to_emoji(guild)
                        print("Emoji created.")
                    except discord.HTTPException:
                        print("HTTPException occurred.")
                        continue
                    else:
                        emoji_cache.add_emoji(emoji)
                        print("Emoji added to cache.")
                        return emoji
                # If it exits without returning aka there was no space available
                else:
                    emoji_to_delete = guild_emoji_lists[0][
                        0
                    ]  # Get first emoji from the first emoji server
                    await emoji_to_delete.delete()  # Delete the emoji to make space for the new one
                    print("Emoji deleted to make space.")
                    emoji_cache.remove_emoji(
                        emoji_to_delete
                    )  # Delete that emoji from cache if it exists
                    print("Emoji removed from cache.")
                    return await upload_emoji(
                        colour, draw_view=draw_view, interaction=interaction
                    )  # Run again