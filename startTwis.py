import asyncio # Required for running both bots at the same time

# Import both bot classes from twitch_bot.py and discord_bot.py
from twiscord_twitch import TwiscordTwitch 
from twiscord_discord import TwiscordDiscord

async def main():
    # Instantiate each class
    twitch_bot = TwiscordTwitch()
    discord_bot = TwiscordDiscord()
    
    # Add a reference to the other bot to each bot
    twitch_bot.discord_bot = discord_bot
    discord_bot.twitch_bot = twitch_bot
    
    # Start both bots
    task2 = discord_bot.start()
    task1 = twitch_bot.start()
    
    # Run both tasks concurrently
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    # Run the main function if this file is run
    # (if someone import this as a library, we don't want to run main immediately)
    asyncio.run(main())