""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

from discord.ext import commands
from discord.ext.commands import Context, has_permissions
import discord
from discord import app_commands
from discord.ext import commands

from helpers import checks
from helpers import db_manager


# Here we name the cog and create a new class for the cog.
class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    #command to add a new streamer and their server and their ID to the database streamer table, using the add_streamer function from helpers\db_manager.py
    #registering a streamer will also add them to the database user table
    @commands.hybrid_command(
        name="register",
        description="This command will add a new streamer to the database.",
    )
    async def register(self, ctx: Context, streamer_channel: str, emoteprefix: str):
        """
        This command will add a new streamer to the database.

        :param ctx: The context in which the command was called.
        :param streamer_channel: The streamer's twitch channel.
        :param streamer_server: The streamer's server.
        :param streamer_id: The streamer's ID.
        """

        twitch_id = await db_manager.get_twitch_id(streamer_channel)
        broadcaster_cast_type = await db_manager.get_broadcaster_type(streamer_channel)
        user_id = ctx.author.id
        #check if the streamer already exists in the database
        if await db_manager.is_streamer(user_id):
            #this code fucking sucks, ive spent way too much time and now I have to rewrite it all because I cant figure out how to make it work, yay
            await ctx.send("this person is already a streamer. :)")
            return
        await db_manager.add_streamer(streamer_channel, user_id, emoteprefix, twitch_id, broadcaster_cast_type)
        await db_manager.add_user(user_id, True)
        await ctx.send("Streamer added to the database.")


    #command to remove a streamer from the database streamer table, using the remove_streamer function from helpers\db_manager.py
    @commands.hybrid_command(
        name="unregister",
        description="This command will remove a streamer from the database.",
    )
    async def unregister(self, ctx: Context, streamer_channel: str):
        """
        This command will remove a streamer from the database.

        :param ctx: The context in which the command was called.
        :param streamer_channel: The streamer's twitch channel.
        """
        user_id = ctx.author.id
        await db_manager.remove_streamer(user_id)
        await db_manager.remove_user(user_id)
        await ctx.send("Streamer removed from the database.")   

    #command to veiw all streamers in the database streamer table, using the view_streamers function from helpers\db_manager.py
    @commands.hybrid_command(
        name="viewstreamers",
        description="This command will view all streamers in the database.",
    )
    @checks.is_owner()
    async def view_streamers(self, ctx: Context):
        """
        This command will view all streamers in the database.

        :param ctx: The context in which the command was called.
        """
        streamers = await db_manager.view_streamers()
        embed = discord.Embed(title="Streamers", description="All streamers in the database.", color=0x00ff00)
        for i in streamers:
            streamer_channel = i[1]
            def remove_prefix(text, prefix):
                if text.startswith(prefix):
                    return text[len(prefix):]
                return text
            streamer_channel_name = remove_prefix(streamer_channel, "https://www.twitch.tv/")
            embed.add_field(name=streamer_channel_name, value=i[1], inline=False)
        await ctx.send(embed=embed)

#command to view inventory of a user, using the view_inventory function from helpers\db_manager.py
    @commands.hybrid_command(
        name="inventory",
        description="This command will view your inventory.",
    )
    async def inventory(self, ctx: Context):
        """
        This command will view your inventory.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        #check if the user exists in the database
        users = await db_manager.view_users()
        for i in users:
            user_id_if_exists = i[0]
            user_id_if_exists = int(user_id_if_exists)
            if user_id == user_id_if_exists:
                inventory = await db_manager.view_inventory(user_id)
                embed = discord.Embed(title="Inventory", description="Your inventory.", color=0x00ff00)
                for i in inventory:
                    item_id = i[1]
                    item_name = i[2]
                    item_emoji = i[4]
                    item_amount = i[6]
                    item_rarity = i[5]
                    embed.add_field(name=f"`ID:{item_id}` {item_name}{item_emoji} x{item_amount}", value=f"rarity: {item_rarity}", inline=False)
                await ctx.send(embed=embed)
                return
        await ctx.send(f"You do not exist in the database.")

        #command to add an item to a users inventory by its item_id
    @commands.hybrid_command(
        name="additem",
        description="This command will add an item to a users inventory.",
    )
    @checks.is_streamer()
    async def add_item(self, ctx: Context, user: discord.User, item_id: str, item_amount: int):
        """
        This command will add an item to a users inventory.

        :param ctx: The context in which the command was called.
        :param user: The user that should get the item.
        :param item_id: The id of the item that should be added.
        :param item_amount: The amount of the item that should be added.
        """
        user_id = user.id
        #check if the user exists in the database
        users = await db_manager.view_users()
        for i in users:
            isStreamer = i[3]
            isStreamer = bool(isStreamer)
            if isStreamer == True:

                item_name = await db_manager.get_streamer_item_name(item_id)
                item_price = await db_manager.get_streamer_item_price(item_id)
                item_emote = await db_manager.get_streamer_item_emote(item_id)
                item_rarity = await db_manager.get_streamer_item_rarity(item_id)
                item_amount = item_amount
                item_type = await db_manager.get_streamer_item_type(item_id)
                item_damage = await db_manager.get_basic_item_damage(item_id)


                if item_type == 'Collectable':
                    #set item damage to 0
                    item_damage = 0
                    #add the item to the users inventory
                    await db_manager.add_item_to_inventory(user_id, item_id, item_name, item_price, item_emote, item_rarity, item_amount, item_type, item_damage, False)
                else:

                    await db_manager.add_item_to_inventory(user_id, item_id, item_name, item_price, item_emote, item_rarity, item_amount, item_type, item_damage, False)
                await ctx.send(f"Added {item_name}{item_emote} x{item_amount} to {user.mention}'s inventory.")

    #command to create a new item in the database item table, using the add_item function from helpers\db_manager.py
    @commands.hybrid_command(
        name="createitem",
        description="This command will create a new item in the database.",
    )
    @checks.is_streamer()
    async def create_item(self, ctx: Context, item_name: str, item_price: int, item_emote: discord.Emoji):
        """
        This command will create a new item in the database.

        :param ctx: The context in which the command was called.
        :param item_name: The name of the item that should be added.
        :param item_price: The price of the item that should be added.
        """
        user_id = ctx.message.author.id
        #check if the item already exists in the database
        #grab the streamersID from the database
        streamerPrefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        streamerChannel = await db_manager.get_streamerChannel(user_id)
        twitchID = await db_manager.get_twitchID(user_id)
        twitchID = int(twitchID)
        items = await db_manager.view_streamer_items(streamerChannel)
        emojiString = f'<:{item_emote.name}:{item_emote.id}>'
        print(items)
        for i in items:
            if item_name in i:
                await ctx.send(f"`{item_name}` already exists in the database.")
                return
        await db_manager.add_item(streamerPrefix, item_name, item_price, "Legendary", emojiString, twitchID, "Collectable")
        await ctx.send(f"Added `{item_name}` {emojiString} to the database, with the price `{item_price}`.")

    #command to remove an item from the database item table, using the remove_item function from helpers\db_manager.py
    @commands.hybrid_command(
        name="removeitem",
        description="This command will remove an item from the database.",
    )
    @checks.is_streamer()
    async def remove_item(self, ctx: Context, item_name: str):
        """
        This command will remove an item from the database.

        :param ctx: The context in which the command was called.
        :param item_name: The name of the item that should be removed.
        """
        user_id = ctx.message.author.id
        #check if the item exists in the database
        streamerChannel = await db_manager.get_streamerChannel(user_id)
        streamerPrefix = await db_manager.get_streamerPrefix_with_user_id(user_id)
        items = await db_manager.view_streamer_items(streamerChannel)
        for i in items:
            if item_name in i:
                await db_manager.remove_item(streamerPrefix, item_name)
                await ctx.send(f"Removed `{item_name}` from the database.")
                return
        await ctx.send(f"`{item_name}` doesn't exist in the database.")


#command to view the items of a specific streamer by their ID, using the view_streamer_items function from helpers\db_manager.py
    @commands.hybrid_command(
        name="view_streamer_items",
        description="This command will view all items of a specific streamer.",
    )
    @checks.is_owner()
    #the user needs to input the streamers ID
    async def view_streamer_items(self, ctx: Context, streamer_channel: str):
        """
        This command will view all items of a specific streamer.

        :param ctx: The context in which the command was called.
        :param streamer_prefix: The ID of the streamer whose items should be viewed.
        """
        user_id = ctx.message.author.id
        #check if the streamer exists in the database
        streamers = await db_manager.view_streamers()
        #remove the https://www.twitch.tv/ from the streamerchannel
        #rmove prefix function
        def remove_prefix(text, prefix):
            if text.startswith(prefix):
                return text[len(prefix):]
            return text
        streamer_channel_name = remove_prefix(streamer_channel, "https://www.twitch.tv/")
        for i in streamers:
            if streamer_channel in i:
                items = await db_manager.view_streamer_items(streamer_channel)
                embed = discord.Embed(title="Items", description=f"All of `{streamer_channel_name}'s` Items.", color=0x00ff00)
                print(items)
                for i in items:
                    #remove the streamerPrefix from the name of the item
                    print(i)
                    item_id = i[1]
                    item_name = i[2]
                    item_price = i[3]
                    item_emote = i[4]
                    embed.add_field(name=f"`ID:{item_id}` {item_name}{item_emote}", value=f"Price: {item_price}", inline=True)
                await ctx.send(embed=embed)
                return
        await ctx.send(f"Streamer doesn't exist in the database.")

#shop command to view the shop using the display_shop function from helpers\db_manager.py
    @commands.hybrid_command(
        name="shop",
        description="This command will display the shop.",
    )
    async def shop(self, ctx: Context):
        """
        This command will display the shop.

        :param ctx: The context in which the command was called.
        """
        shop = await db_manager.display_shop_items()
        embed = discord.Embed(title="Shop", description="All of the items in the shop.", color=0x00ff00)
        for i in shop:
            item_id = i[0]
            item_name = i[1]
            item_price = i[2]
            item_emote = i[3]
            item_rarity = i[4]
            item_type = i[5]
            item_damage = i[6]
            item_amount = db_manager.get_shop_item_amount(item_id)
            if item_type == "Weapon":
                embed.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Damage**: `{item_damage}` \n **Rarity**: `{item_rarity}` ", inline=False)
            else:
                embed.add_field(name=f"{item_name}{item_emote} x{item_amount}", value=f"`ID:{item_id}` \n **Price**: `{item_price}` \n **Type**: `{item_type}` \n **Rarity**: `{item_rarity}` ", inline=False)
        await ctx.send(embed=embed)

     #buy command for buying items, multiple of the same item can be bought, and the user can buy multiple items at once, then removes them from the shop, and makes sure the user has enough bucks
    @commands.hybrid_command(
        name="buy",
        description="This command will buy an item from the shop.",
    )
    async def buy(self, ctx: Context, item_id: int, amount: int):
        """
        This command will buy an item from the shop.

        :param ctx: The context in which the command was called.
        :param item_id: The ID of the item that should be bought.
        :param amount: The amount of the item that should be bought.
        """
        user_id = ctx.message.author.id
        user_profile = await db_manager.profile(user_id)
        user_money = user_profile[1]
        user_money = int(user_money)
        user_health = user_profile[2]
        isStreamer = user_profile[3]
        #check if the item exists in the shop
        shop = await db_manager.display_shop_items()
        for i in shop:
            if item_id in i:
                #check if the user has enough bucks
                item_price = i[2]
                item_price = int(item_price)
                total_price = item_price * amount
                if user_money >= total_price:
                    item_name = db_manager.get_basic_item_name(item_id)
                    item_price = db_manager.get_shop_item_price(item_id)
                    item_emoji = db_manager.get_shop_item_emoji(item_id)
                    item_rarity = db_manager.get_basic_item_rarity(item_id)
                    item_type = db_manager.get_basic_item_type(item_id)
                    item_damage = db_manager.get_basic_item_damage(item_id)
                    #remove the item from the shop
                    await db_manager.remove_shop_item_amount(item_id, amount)
                    #add the item to the users inventory
                    await db_manager.add_item_to_inventory(user_id, item_id, item_name, item_price, item_emoji, item_rarity, amount, item_type, item_damage, False)
                    #remove the price from the users money
                    await db_manager.remove_money(user_id, total_price)
                    await ctx.send(f"You bought `{amount}` of `{i[1]}` for `{total_price}` bucks.")
                    return
                else:
                    await ctx.send(f"You don't have enough bucks to buy `{amount}` of `{i[1]}`.")
                    return
        await ctx.send(f"Item doesn't exist in the shop.")

#view a users profile using the view_profile function from helpers\db_manager.py
    @commands.hybrid_command(
        name="profile",
        description="This command will view your profile.",
    )
    async def profile(self, ctx: Context):
        """
        This command will view your profile.

        :param ctx: The context in which the command was called.
        """
        user_id = ctx.message.author.id
        user_profile = await db_manager.profile(user_id)
        user_id = user_profile[0]
        user_money = user_profile[1]
        user_health = user_profile[2]
        isStreamer = user_profile[3]
        user_items = await db_manager.view_inventory(user_id)
        embed = discord.Embed(title="Profile", description=f"{ctx.message.author.mention}'s Profile.", color=0x00ff00)
        embed.add_field(name="Health", value=f"{user_health} / 100", inline=True)
        embed.add_field(name="Money", value=f"{user_money}", inline=True)
        for i in user_items:
            item_name = i[2]
            item_emote = i[4]
            item_amount = i[6]
            embed.add_field(name=f"{item_name}{item_emote}", value=f"{item_amount}", inline=False)
        embed.set_thumbnail(url=ctx.message.author.avatar.url)
        if isStreamer == 1:
            isStreamer = "Yes"
        elif isStreamer == 0:
            isStreamer = "No"
        embed.set_footer(text=f"User ID: {user_id} | Streamer: {isStreamer}")

        await ctx.send(embed=embed)


#a command to give a user money using the add_money function from helpers\db_manager.py
    @commands.hybrid_command(
        name="give",
        description="This command will give a user money.",
    )
    async def give(self, ctx: Context, user: discord.Member, amount: int):
        """
        This command will give a user money.

        :param ctx: The context in which the command was called.
        :param user: The user that should be given money.
        :param amount: The amount of money that should be given.
        """
        user_id = ctx.message.author.id
        user_money = await db_manager.get_money(user_id)
        if user_money >= amount:
            await db_manager.add_money(user.id, amount)
            await db_manager.remove_money(user_id, amount)
            await ctx.send(f"You gave {user.mention} `{amount}`.")
        else:
            await ctx.send(f"You don't have enough money to give this user.")

    #a command to add money to a user using the add_money function from helpers\db_manager.py
    @commands.hybrid_command(
        name="addmoney",
        description="This command will add money to a user.",
    )
    @checks.is_owner()
    async def addmoney(self, ctx: Context, user: discord.Member, amount: int):
        """
        This command will add money to a user.

        :param ctx: The context in which the command was called.
        :param user: The user that should be given money.
        :param amount: The amount of money that should be given.
        """
        await db_manager.add_money(user.id, amount)
        await ctx.send(f"You gave {user.mention} `{amount}` bucks.")



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Template(bot))
