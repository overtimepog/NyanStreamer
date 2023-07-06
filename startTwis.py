import asyncio # Required for running both bots at the same time

# Import both bot classes from twitch_bot.py and discord_bot.py
from twiscord_twitch import TwitchBot 
from twiscord_discord import DiscordBot

async def main():
    # Instantiate each class
    twitch_bot = TwitchBot()
    discord_bot = DiscordBot()
    
    # Add a reference to the other bot to each bot
    twitch_bot.discord_bot = discord_bot
    discord_bot.twitch_bot = twitch_bot
    
    # Start both bots
    task1 = twitch_bot.start()
    task2 = discord_bot.start()
    
    # Run both tasks concurrently
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    # Run the main function if this file is run
    # (if someone import this as a library, we don't want to run main immediately)
    asyncio.run(main())