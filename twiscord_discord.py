import os # for importing environment variables for the bots to use
import discord
from discord.ext import commands as discord_commands
import json
from helpers import db_manager

class TwiscordDiscord(discord_commands.Bot):
  def __init__(self):
    with open("config.json") as file:
        config = json.load(file)

    self.token = config['token']
    self.channel = None  # Will be set later
    self._is_ready_ = False

    command_prefix = config['prefix']
    self.enabled_channels_file = 'enabled_channels.json'
    if os.path.exists(self.enabled_channels_file):
      with open(self.enabled_channels_file, 'r') as file:
        self.enabled_channels = set(json.load(file))
    else:
      self.enabled_channels = set()
    
    super().__init__(command_prefix=command_prefix, intents=discord.Intents.all())
    
  def start(self):
    # This function overrides the default `start` function
    # since I want to be able to just call `start` from
    # `main.py` and configure the token from here.
    # This returns the co-routine of the bot, needed for running both bots at once.
    return super().start(self.token)
  
  async def on_ready(self):
    self.channel_ids = await db_manager.get_all_twiscord_discord_channels()
    if self.channel_ids:
      print(f"Twiscord Enabled for Discord Channels | {self.channel_ids}")

      # Check for new or removed channels
      current_channels = set(self.channel_ids)
      new_channels = current_channels - self.enabled_channels
      removed_channels = self.enabled_channels - current_channels

      # Send a start message to each new channel
      for channel in new_channels:
        self.channel = self.get_channel(channel)
        await self.channel.send("Twiscord is now enabled for this channel!")

      # Update the set of enabled channels
      self.enabled_channels = current_channels
      # Save the set of enabled channels to a file
      with open(self.enabled_channels_file, 'w') as file:
        json.dump(list(self.enabled_channels), file)
      self.channels = [self.get_channel(id) for id in self.channel_ids]

    self._is_ready_ = True
    if self.twitch_bot._is_ready_:
        pass
  
  async def on_message(self, message):
    if message.author == self.user:
      return # Don't respond to messages from yourself
    
    if not self.twitch_bot._is_ready_: # Make sure that the twitch bot is up and running
      #await message.channel.send("[Twiscord] Twitch not initialized.")
      print("[Twiscord] Twitch not initialized.")
      return
    
    #print("Channel ID: " + str(message.channel.id))
    #print("Channel IDs: " + str(self.channel_ids))
    try:
      channel_ids = await db_manager.get_all_twiscord_discord_channels()
    except:
      channel_ids = []
    if message.channel.id in channel_ids:
      content = f"{'[' + str(message.author.top_role) + '] ' if message.author.top_role else ''}{message.author} » {message.clean_content}"[:300] # Only take the first 300 characters, 500 is officially the max but 300 should be all you need
      print(f"[discord] {content}")
      if message.clean_content.startswith(self.command_prefix): await self.handle_commands(message) # If the message starts with the prefix, then send the message to self.handle_commands 
      else: await self.twitch_bot.channel.send(content) # If it's not a command, then send the message to the twitch chat
      
    else:
      return # Wrong channel
  
  async def handle_commands(self, message):
    """
    Class based discord.ext.commands.Bot extenders don't have
    a simple way to handle functional based commands.
    
    If you're making a discord bot that is class based like this,
    then I'd recommend using this.
    """
    command = message.clean_content[len(self.command_prefix):].split(" ")[0] # Get the first word after the prefix
    arguments = message.clean_content[len(self.command_prefix):].split(" ")[1:] # Get a list of all the arguments after the prefix and after the command keyword
    
    if command == 'twitch':
      await self.twitch(message, arguments)
  
  async def twitch(self, message, arguments):
    # If people type PREFIXtwitch, then reply with the twitch channel link
    # For example, if the prefix was '!', then !twitch would run this
    await message.channel.send(self.twitch_bot.twitch_link)

if __name__ == "__main__":
  # This file shouldn't be run, this is just the class extender
  # ./main.py is the file that should be ran
  print("Sorry, this isn't the file you meant to run.")
  print("You need to run for Twiscord to work ./main.py")