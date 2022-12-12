""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import aiosqlite
import requests
import aiohttp
import discord
from typing import Tuple, Any, Optional, Union
import random


#`item_id` varchar(20) NOT NULL,
#`item_name` varchar(255) NOT NULL,
#`item_price` varchar(255) NOT NULL,
#`item_emoji` varchar(255) NOT NULL,
#`item_rarity` varchar(255) NOT NULL,
#`item_type` varchar(255) NOT NULL,
#`item_damage` int(11) NOT NULL,
#`isUsable` boolean NOT NULL,
#`isEquippable` boolean NOT NULL    
      
      
#STUB - Basic items
basic_items = [
    {
        "item_id": "WoodenSword",
        "item_name": "Wooden Sword",
        "item_price": 25,
        "item_emoji": "<:Wooden_Sword:1051976486283919360>",
        "item_rarity": "Common",
        "item_type": "Weapon",
        "item_damage": 5,
        "isUsable": False,
        "inShop": True,
        "isEquippable": True,
        "item_description": "A wooden sword. It's not very strong, but it's better than nothing."
    },
    {
        "item_id": "SmallHealthPotion",
        "item_name": "Small Health Potion",
        "item_price": 100,
        "item_emoji": "🧪",
        "item_rarity": "Common",
        "item_type": "Consumable",
        "item_damage": 10,
        "isUsable": True,
        "inShop": True,
        "isEquippable": False,
        "item_description": "A small health potion. It's not very strong, but it's better than nothing."
    },
    {
        "item_id": "MediumHealthPotion",
        "item_name": "Medium Health Potion",
        "item_price": 250,
        "item_emoji": "🧪",
        "item_rarity": "Uncommon",
        "item_type": "Consumable",
        "item_damage": 20,
        "isUsable": True,
        "inShop": True,
        "isEquippable": False,
        "item_description": "A medium health potion. Nice to have in a pinch"
    },
    {
        "item_id": "LargeHealthPotion",
        "item_name": "Large Health Potion",
        "item_price": 500,
        "item_emoji": "🧪",
        "item_rarity": "Rare",
        "item_type": "Consumable",
        "item_damage": 30,
        "isUsable": True,
        "inShop": True,
        "isEquippable": False,
        "item_description": "A large health potion. Bigger is better, right?"
    },
    {
        "item_id": "IronArmor",
        "item_name": "Iron Armor",
        "item_price": 500,
        "item_emoji": "🛡️",
        "item_rarity": "Uncommon",
        "item_type": "Armor",
        "item_damage": 25,
        #item damage on Armor is the amount of damage it reduces when equipped
        "isUsable": False,
        "inShop": True,
        "isEquippable": True,
        "item_description": "A basic iron armor. It's not very strong, but it's better than nothing."
    }
]

class Database:
    @staticmethod
    async def _connect():
        return await aiosqlite.connect("database/database.db")

    @staticmethod
    async def _fetch(cursor, mode) -> Optional[Any]:
        if mode == "one":
            return await cursor.fetchone()
        if mode == "many":
            return await cursor.fetchmany()
        if mode == "all":
            return await cursor.fetchall()

        return None

    async def execute(self, query: str, values: Tuple = (), *, fetch: str = None) -> Optional[Any]:
        db = await self._connect()
        cursor = await db.cursor()

        await cursor.execute(query, values)
        data = await self._fetch(cursor, fetch)
        await db.commit()

        await cursor.close()
        await db.close()

        return data


DB = Database

async def get_money(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            users = await db.execute(f"SELECT `money` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
            return users
        else:
            await db.execute(f"INSERT INTO `users` (`user_id`, `bucks`) VALUES (?, ?)", (user_id, 0))
            users = await db.execute(f"SELECT `money` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
            return users

#add money to a user
async def add_money(user_id: int, amount: int) -> None: 
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `money` = `money` + ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await db.execute(f"INSERT INTO `users` (`user_id`, `money`) VALUES (?, ?)", (user_id, amount))

#remove money from a user
async def remove_money(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `money` = `money` - ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await db.execute(f"INSERT INTO `users` (`user_id`, `money`) VALUES (?, ?)", (user_id, 0))

#add health to a user
async def add_health(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `health` = `health` + ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await db.execute(f"INSERT INTO `users` (`user_id`, `health`) VALUES (?, ?)", (user_id, 100))

#remove health from a user
async def remove_health(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `health` = `health` - ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await db.execute(f"INSERT INTO `users` (`user_id`, `health`) VALUES (?, ?)", (user_id, 100))

async def get_health(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `health` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    else:
        await db.execute(f"INSERT INTO `users` (`user_id`, `health`) VALUES (?, ?)", (user_id, 100))
        users = await db.execute(f"SELECT `health` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    
#get user, if they don't exist, create them
async def get_user(user_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return None
    else:
        await db.execute(f"INSERT INTO `users` (`user_id`, `money`, `health`, isStreamer) VALUES (?, ?, ?, ?)", (user_id, 0, 100, False))

#look at a user's profile, returns a list
async def profile(user_id: int) -> list:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    else:
        await db.execute(f"INSERT INTO `users` (`user_id`, `money`, `health`, isStreamer) VALUES (?, ?, ?, ?)", (user_id, 0, 100, False))
        users = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users

#add the basic items to the database basic_items table
async def add_basic_items() -> None:
    db = DB()
    for item in basic_items:
        data = await db.execute(f"SELECT * FROM `basic_items` WHERE item_id = ?", (item['item_id'],), fetch="one")
        if data is not None:
            print(f"|{item['item_name']}| is already in the database")
            pass
        else:
            await db.execute(f"INSERT INTO `basic_items` (`item_id`, `item_name`, `item_price`, `item_emoji`, `item_rarity`, `item_type`, `item_damage`, `isUsable`, `inShop`, `isEquippable`, `item_description`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (item['item_id'], item['item_name'], item['item_price'], item['item_emoji'], item['item_rarity'], item['item_type'], item['item_damage'], item['isUsable'], item['inShop'], item['isEquippable'], item['item_description']))
            print(f"Added |{item['item_name']}| to the database")

#function to add all the items with inShop = True to the shop table and then add a random int between 1 and 10 to the amount column
async def add_shop_items() -> None:
    db = DB()
    #clear the shop table
    await db.execute(f"DELETE FROM `shop`")
    data = await db.execute(f"SELECT * FROM `basic_items` WHERE inShop = ?", (True,), fetch="all")
    for item in data:
        ItemAmount = random.randint(1, 10)
        await db.execute(f"INSERT INTO `shop` (`item_id`, `item_name`, `item_price`, `item_emoji`, `item_rarity`, `item_type`, `item_damage`, `isUsable`, `isEquippable`, `item_amount`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[9], ItemAmount))
        print(f"Added |{item[1]} x{ItemAmount}| to the shop")

#function to display the shop items
async def display_shop_items() -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `shop`", fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#remove an amount of an item from the shop, if the amount is 0 then remove the item from the shop
async def remove_shop_item_amount(item_id: str, amount: int) -> None:
        db = DB()
        data = await db.execute(f"SELECT * FROM `shop` WHERE item_id = ?", (item_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `shop` SET `item_amount` = `item_amount` - ? WHERE `item_id` = ?", (amount, item_id))
            data = await db.execute(f"SELECT * FROM `shop` WHERE item_id = ?", (item_id,), fetch="one")
            if data[9] <= 0:
                await db.execute(f"DELETE FROM `shop` WHERE item_id = ?", (item_id,))
        else:
            return None
        
#add an amount of an item to the shop
async def add_shop_item_amount(item_id: str, amount: int) -> None:
        db = DB()
        data = await db.execute(f"SELECT * FROM `shop` WHERE item_id = ?", (item_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `shop` SET `item_amount` = `item_amount` + ? WHERE `item_id` = ?", (amount, item_id))
        else:
            return None
        
#get the amount of an item in the shop
async def get_shop_item_amount(item_id: str) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `shop` WHERE item_id = ?", (item_id,), fetch="one")
        if data is not None:
            return data[9]
        else:
            return None
        
#get the price of an item in the shop
async def get_shop_item_price(item_id: str) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `shop` WHERE item_id = ?", (item_id,), fetch="one")
        if data is not None:
            return data[2]
        else:
            return None

#get shop item emoji
async def get_shop_item_emoji(item_id: str) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `shop` WHERE item_id = ?", (item_id,), fetch="one")
        if data is not None:
            return data[3]
        else:
            return None
        
#equip an item, if the item is not in the inventory then return None, if there is an item already equipped then unequip it,
async def equip_item(user_id: int, item_id: str) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND item_id = ?", (user_id, item_id), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `inventory` SET `isEquipped` = 1 WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            return 1
        else:
            return None

#unequip an item
async def unequip_item(user_id: int, item_id: str) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND item_id = ?", (user_id, item_id), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `inventory` SET `isEquipped` = 0 WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            return 1
        else:
            return None

#check if an item is equipped
async def check_item_equipped(user_id: int, item_id: str) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND item_id = ?", (user_id, item_id), fetch="one")
        if data is not None:
            if data[9] == 1:
                return 1
            else:
                return None
        else:
            return None
        
#check if the item ID is a streamer item
async def check_streamer_item(item_id: str) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `streamer_items` WHERE item_id = ?", (item_id,), fetch="one")
        if data is not None:
            return 1
        else:
            return 0

#check if the item ID is a basic item
async def check_basic_item(item_id: str) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `basic_items` WHERE item_id = ?", (item_id,), fetch="one")
        if data is not None:
            return 1
        else:
            return 0
        
        
#check if the user_id is a user
async def check_user(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            return 1
        else:
            return None
        
#get a streamers name from an item ID
async def get_streamer_name_from_item(item_id: str) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `streamer_items` WHERE item_id = ?", (item_id,), fetch="one")
        if data is not None:
            return data[1]
        else:
            return None

#check if the emoji on the item has < and > around it
async def check_emoji(emoji: str) -> int:
        if emoji.startswith("<") and emoji.endswith(">"):
            return 1
        else:
            return 0

#make a request to the twitch api to get the twitch id of the streamer
async def get_twitch_id(streamer_channel: str) -> int:

    headers = {
    'Authorization': 'Bearer obotkbh9829mgr4t8x165z6orsdfvr',
    'Client-Id': 'fh0hp0ectgvo0f7mky467of5jmo83n',
    }
    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    streamer_channel = remove_prefix(streamer_channel, "https://www.twitch.tv/")

    params = {
        'login': f'{streamer_channel}',
    }

    async with aiohttp.ClientSession() as session:
            async with session.get('https://api.twitch.tv/helix/users', params=params, headers=headers) as request:
                data = await request.json()
                print(data)
                twitch_id = data['data'][0]['id']
                print(twitch_id)
                return twitch_id

#make a request to the twitch api to get the broadcaster type of the streamer
async def get_broadcaster_type(streamer_channel: str) -> str:
    
    headers = {
    'Authorization': 'Bearer obotkbh9829mgr4t8x165z6orsdfvr',
    'Client-Id': 'fh0hp0ectgvo0f7mky467of5jmo83n',
    }
    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    streamer_channel = remove_prefix(streamer_channel, "https://www.twitch.tv/")

    params = {
        'login': f'{streamer_channel}',
    }

    async with aiohttp.ClientSession() as session:
            async with session.get('https://api.twitch.tv/helix/users', params=params, headers=headers) as request:
                data = await request.json()
                broadcaster_type = data['data'][0]['broadcaster_type']
                print(broadcaster_type)
                return broadcaster_type

#update the isStreamer column in the user table to True
async def update_is_streamer(user_id: int) -> int:
    db = DB()
    await db.execute(f"UPDATE `user` SET `isStreamer` = 1 WHERE user_id = ?", (user_id,))
    return 1

             

#function to add a new streamer and their server and their ID to the database streamer table, if the streamer already exists, it will say that the streamer already exists
async def add_streamer(streamer_channel: str, user_id: int, emotePrefix: str, twitch_id: int, broadcaster_type: str) -> int:
    """
    This function will add a streamer to the database.

    :param streamer_name: The name of the streamer that should be added.
    :param server_id: The ID of the server where the streamer should be added.
    :param emotePrefix: The emote prefix for the streamer.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("INSERT INTO `streamer` (streamer_prefix, streamer_channel, user_id, twitch_id, broadcaster_type) VALUES (?, ?, ?, ?, ?)", (emotePrefix, streamer_channel, user_id, twitch_id, broadcaster_type))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM `streamer`")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0
   
#function to remove a streamer from the database streamer table using the streamers user ID
async def remove_streamer(user_id: int) -> int:
    """
    This function will remove a streamer from the database.

    :param user_id: The ID of the user that should be removed.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("DELETE FROM streamer WHERE user_id = ?", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM streamer")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0
        
#veiw all streamers in the database streamer table
async def view_streamers() -> list:
    """
    This function will view all streamers in the database.

    :return: A list of all streamers in the database.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer") as cursor:
            result = await cursor.fetchall()
            return result if result is not None else []
        
#add an item to the streamer_items table, uses the streamersID from the streamer table and the item name and the item price
async def add_item(streamerPrefix: str, itemName: str, itemPrice: int, itemRarity: str, itemEmoji: str, twitchID : int, item_type: str) -> int:
    """
    This function will add an item to the streamer_items table.

    :param streamerPrefix: The ID of the streamer that the item should be added to.
    :param itemName: The name of the item that should be added.
    :param itemPrice: The price of the item that should be added.
    """
    #create an item_id for the item that is being added by combining the streamerPrefix and the itemName
    item_id = str(streamerPrefix) + " " + itemName
    #convert all spaces in the item name to underscores
    item_id = item_id.replace(" ", "_")
    async with aiosqlite.connect("database/database.db") as db:
        #add all of it to the database
        await db.execute("INSERT INTO streamer_items(streamer_prefix, item_id, item_name, item_price, item_emoji, item_rarity, twitch_id, item_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (streamerPrefix, item_id, itemName, itemPrice, itemEmoji, itemRarity, twitchID, item_type))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM streamer_items")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0
        
#remove an item from the streamer_items table using the streamersID from the streamer table and the item name
async def remove_item(streamerPrefix: str, itemName: str) -> int:
    """
    This function will remove an item from the streamer_items table.

    :param streamerPrefix: The ID of the streamer that the item should be removed from.
    :param itemName: The name of the item that should be removed.
    """
    #create an item_id for the item that is being removed by combining the streamerPrefix and the itemName
    item_id = str(streamerPrefix) + " " + itemName
    #convert all spaces in the item name to underscores
    item_id = item_id.replace(" ", "_")
    async with aiosqlite.connect("database/database.db") as db:
        #remove the item from the database
        await db.execute("DELETE FROM streamer_items WHERE item_id = ?", (item_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM streamer_items")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0
        
#view all the items with a specific streamer_channel
async def view_streamer_items(streamer_channel: str) -> list:
    """
    This function will view all streamer items in the database.

    :return: A list of all streamer items in the database.
    """
    #get the streamerPrefix from the streamer table using the streamers channel
    streamerChannel = str(streamer_channel)
    streamerPrefix = await get_streamerPrefix_with_channel(streamerChannel)
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE streamer_prefix=?", (streamerPrefix,)) as cursor:
            result = await cursor.fetchall()
            return result if result is not None else []

#view all the basic items in the database
async def view_basic_items() -> list:
    """
    This function will view all basic items in the database.

    :return: A list of all basic items in the database.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items") as cursor:
            result = await cursor.fetchall()
            return result if result is not None else []
        
#view an item from the basic_items table using the items id
async def view_basic_item(item_id: str) -> list:
    """
    This function will view an item from the basic_items table.

    :return: A list of the item from the basic_items table.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchall()
            return result if result is not None else []


#add a user to the users table using the users ID, setting the users balance to 0, and setting the users streamer status to false, and add them to the inventory table
async def add_user(user_id: int, isStreamer: bool) -> int:
    """
    This function will add a user to the users table.

    :param user_id: The ID of the user that should be added.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("INSERT INTO users(user_id, money, health, isStreamer) VALUES (?, ?, ?, ?)", (user_id, 0, 100, isStreamer))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM users")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0
        
#remove a user from the users table using the users ID
async def remove_user(user_id: int) -> int:
    """
    This function will remove a user from the users table.

    :param user_id: The ID of the user that should be removed.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM users")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0
        
#view all the users in the users table
async def view_users() -> list:
    """
    This function will view all users in the database.

    :return: A list of all users in the database.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            result = await cursor.fetchall()
            return result if result is not None else []
        
#view all of a users inventory 
async def view_inventory(user_id: int) -> list:
    """
    This function will view all items in a users imventory.

    :return: A list of all items in a users imventory.
    """
    db = DB()
    data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ?", (user_id,), fetch="all")
    if data is not None:
        return data
    else:
        return []
        
#add an item to the inventory table, uses the usersID from the users table and the item ID from the streamer_items table, if the item already exists in the inventory table, it will add 1 to the item_amount
async def add_item_to_inventory(user_id: int, item_id: str, item_name: str, item_price: int, item_emoji: str, item_rarity: str, item_amount: int, item_type: str, item_damage: int, isEquipped: bool) -> int:
    """
    This function will add an item to the inventory table.

    :param user_id: The ID of the user that the item should be added to.
    :param item_id: The ID of the item that should be added.
    :param item_name: The name of the item that should be added.
    :param item_price: The price of the item that should be added.
    :param item_emoji: The emoji of the item that should be added.
    :param item_rarity: The rarity of the item that should be added.
    :param item_amount: The amount of the item that should be added.
    """
    async with aiosqlite.connect("database/database.db") as db:
        #check if the item already exists in the inventory table
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_id=?", (user_id, item_id)) as cursor:
            result = await cursor.fetchone()
            if result is not None:
                #if the item already exists in the inventory table, add 1 to the item_amount
                await db.execute("UPDATE inventory SET item_amount = item_amount + 1 WHERE user_id = ? AND item_id = ?", (user_id, item_id))
                await db.commit()
                return 1
            else:
                #if the item does not exist in the inventory table, add it to the inventory table
                await db.execute("INSERT INTO inventory(user_id, item_id, item_name, item_price, item_emoji, item_rarity, item_amount, item_type, item_damage, isEquipped) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, item_id, item_name, item_price, item_emoji, item_rarity, item_amount, item_type, item_damage, isEquipped))
                await db.commit()
                rows = await db.execute("SELECT COUNT(*) FROM inventory")
                async with rows as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result is not None else 0

#remove an item from the inventory table, uses the usersID from the users table and the item ID from the streamer_items table, if the item already exists in the inventory table, it will remove 1 from the item_amount
async def remove_item_from_inventory(user_id: int, item_id: str) -> int:
    """
    This function will remove an item from the inventory table.

    :param user_id: The ID of the user that the item should be removed from.
    :param item_id: The ID of the item that should be removed.
    """
    async with aiosqlite.connect("database/database.db") as db:
        #check if the item already exists in the inventory table
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_id=?", (user_id, item_id)) as cursor:
            result = await cursor.fetchone()
            if result is not None:
                #if the item already exists in the inventory table, remove 1 from the item_amount
                await db.execute("UPDATE inventory SET item_amount = item_amount - 1 WHERE user_id = ? AND item_id = ?", (user_id, item_id))
                await db.commit()
                return 1
            else:
                #if the item does not exist in the inventory table, return 0
                return 0
            
#get streamerPrefix from the streamer table using the streamers user ID
async def get_streamerPrefix_with_user_id(user_id: int) -> str:
    """
    This function will get the streamerPrefix from the streamer table.

    :param user_id: The ID of the user that the streamerPrefix should be gotten from.
    :return: The streamerPrefix of the user.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

#get streamerPrefix from the streamer table using the streamers channel
async def get_streamerPrefix_with_channel(streamer_channel: str) -> str:
    """
    This function will get the streamerPrefix from the streamer table.

    :param streamer_channel: The channel of the streamer that the streamerPrefix should be gotten from.
    :return: The streamerPrefix of the streamer.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer WHERE streamer_channel=?", (streamer_channel,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0
        
#get twitchID from the streamer table using the streamers user ID
async def get_twitchID(user_id: int) -> str:
    """
    This function will get the twitchID from the streamer table.

    :param user_id: The ID of the user that the twitchID should be gotten from.
    :return: The twitchID of the user.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[3] if result is not None else 0
        
#get an streamer items name via its id
async def get_streamer_item_name(item_id: str) -> str:
    """
    This function will get the name of an item.

    :param item_id: The ID of the item that the name should be gotten from.
    :return: The name of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[2] if result is not None else 0
        
#get an streamer items price via its id
async def get_streamer_item_price(item_id: str) -> int:
    """
    This function will get the price of an item.

    :param item_id: The ID of the item that the price should be gotten from.
    :return: The price of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[3] if result is not None else 0
        
#get an streamer items emote via its id
async def get_streamer_item_emote(item_id: str) -> str:
    """
    This function will get the emote of an item.

    :param item_id: The ID of the item that the emote should be gotten from.
    :return: The emote of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[4] if result is not None else 0

#get an streamer items rarity via its id
async def get_streamer_item_rarity(item_id: str) -> str:
    """
    This function will get the rarity of an item.

    :param item_id: The ID of the item that the rarity should be gotten from.
    :return: The rarity of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[5] if result is not None else 0
        
#get an streamer items type via its id
async def get_streamer_item_type(item_id: str) -> str:
    """
    This function will get the type of an item.

    :param item_id: The ID of the item that the type should be gotten from.
    :return: The type of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[7] if result is not None else 0
        
#get items basic items damage via its id
async def get_basic_item_damage(item_id: str) -> int:
    """
    This function will get the damage of an item.

    :param item_id: The ID of the item that the damage should be gotten from.
    :return: The damage of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[6] if result is not None else 0
        
#get items basic items name via its id
async def get_basic_item_name(item_id: str) -> str:
    """
    This function will get the name of an item.

    :param item_id: The ID of the item that the name should be gotten from.
    :return: The name of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0

#get items basic items price via its id
async def get_basic_item_price(item_id: str) -> int:
    """
    This function will get the price of an item.

    :param item_id: The ID of the item that the price should be gotten from.
    :return: The price of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[2] if result is not None else 0
        
#get items basic items emote via its id
async def get_basic_item_emote(item_id: str) -> str:
    """
    This function will get the emote of an item.

    :param item_id: The ID of the item that the emote should be gotten from.
    :return: The emote of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[3] if result is not None else 0

#get items basic items rarity via its id
async def get_basic_item_rarity(item_id: str) -> str:
    """
    This function will get the rarity of an item.

    :param item_id: The ID of the item that the rarity should be gotten from.
    :return: The rarity of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[4] if result is not None else 0

#get items basic items type via its id
async def get_basic_item_type(item_id: str) -> str:
    """
    This function will get the type of an item.

    :param item_id: The ID of the item that the type should be gotten from.
    :return: The type of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[5] if result is not None else 0
        
#get items basic items damage via its id
async def get_basic_item_damage(item_id: str) -> int:
    """
    This function will get the damage of an item.

    :param item_id: The ID of the item that the damage should be gotten from.
    :return: The damage of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[6] if result is not None else 0
        
#get basic items description via its id
async def get_basic_item_description(item_id: str) -> str:
    """
    This function will get the description of an item.

    :param item_id: The ID of the item that the description should be gotten from.
    :return: The description of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[10] if result is not None else 0
        
#check if a baic item is usable
async def is_basic_item_usable(item_id: str) -> bool:
    """
    This function will check if a basic item is usable.

    :param item_id: The ID of the item that should be checked.
    :return: True if the item is usable, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[7] if result is not None else 0
        
#check if a baic item is in the shop
async def is_basic_item_in_shop(item_id: str) -> bool:
    """
    This function will check if a basic item is in the shop.

    :param item_id: The ID of the item that should be checked.
    :return: True if the item is in the shop, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[8] if result is not None else 0

#check if a baic item is equipable
async def is_basic_item_equipable(item_id: str) -> bool:
    """
    This function will check if a basic item is equipable.

    :param item_id: The ID of the item that should be checked.
    :return: True if the item is equipable, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[9] if result is not None else 0
        
#check the inventory of a user for any items with the item_type Armor and if they are equiped with the item_type Armor
async def is_armor_equipped(user_id: int) -> bool:
    """
    This function will check if a user has armor equiped.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user has armor equiped, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_type=? AND isEquipped=?", (user_id, "Armor", 1)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0
        
#check the inventory of a user for any items with the item_type Weapon and if they are equiped with the item_type Weapon
async def is_weapon_equipped(user_id: int) -> bool:
    """
    This function will check if a user has a weapon equiped.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user has a weapon equiped, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_type=? AND isEquipped=?", (user_id, "Weapon", 1)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0
        
#check the inventory of a user for any items with the item_type Accessory and if they are equiped with the item_type Accessory
async def is_accessory_equipped(user_id: int) -> bool:
    """
    This function will check if a user has an accessory equiped.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user has an accessory equiped, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_type=? AND isEquipped=?", (user_id, "Accessory", 1)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0

#check if an item has its isEquipped value set to 1 in the inventory table
async def id_of_item_equipped(user_id: int, item_id: str) -> str:
    """
    This function will check if an item is equipped.

    :param user_id: The ID of the user that should be checked.
    :param item_id: The ID of the item that should be checked.
    :return: True if the item is equipped, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_id=? AND isEquipped=?", (user_id, item_id, 1)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0
        
#get id of the weapon that is equiped
async def id_of_weapon_equipped(user_id: int) -> str:
    """
    This function will get the ID of the weapon that is equipped.

    :param user_id: The ID of the user that should be checked.
    :return: The ID of the weapon that is equipped.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_type=? AND isEquipped=?", (user_id, "Weapon", 1)) as cursor:
            result = await cursor.fetchone()
            return result[2] if result is not None else 0
        
#get id of the armor that is equiped
async def id_of_armor_equipped(user_id: int) -> str:
    """
    This function will get the ID of the armor that is equipped.

    :param user_id: The ID of the user that should be checked.
    :return: The ID of the armor that is equipped.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_type=? AND isEquipped=?", (user_id, "Armor", 1)) as cursor:
            result = await cursor.fetchone()
            return result[2] if result is not None else 0

#get streamer channel from the streamer table using the streamers user ID
async def get_streamerChannel(user_id: int) -> str:
    """
    This function will get the streamerChannel from the streamer table.

    :param user_id: The ID of the user that the streamerChannel should be gotten from.
    :return: The streamerChannel of the user.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0
    
#check if the user is a streamer using the users user ID from the users table
async def is_streamer(user_id: int) -> bool:
    """
    This function will check if a user is a streamer.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user is a streamer, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None
        
async def is_blacklisted(user_id: int) -> bool:
    """
    This function will check if a user is blacklisted.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user is blacklisted, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM blacklist WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def add_user_to_blacklist(user_id: int) -> int:
    """
    This function will add a user based on its ID in the blacklist.

    :param user_id: The ID of the user that should be added into the blacklist.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("INSERT INTO blacklist(user_id) VALUES (?)", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def remove_user_from_blacklist(user_id: int) -> int:
    """
    This function will remove a user based on its ID from the blacklist.

    :param user_id: The ID of the user that should be removed from the blacklist.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("DELETE FROM blacklist WHERE user_id=?", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def add_warn(user_id: int, server_id: int, moderator_id: int, reason: str) -> int:
    """
    This function will add a warn to the database.

    :param user_id: The ID of the user that should be warned.
    :param reason: The reason why the user should be warned.
    """
    async with aiosqlite.connect("database/database.db") as db:
        rows = await db.execute("SELECT id FROM warns WHERE user_id=? AND server_id=? ORDER BY id DESC LIMIT 1", (user_id, server_id,))
        async with rows as cursor:
            result = await cursor.fetchone()
            warn_id = result[0] + 1 if result is not None else 1
            await db.execute("INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)", (warn_id, user_id, server_id, moderator_id, reason,))
            await db.commit()
            return warn_id


async def remove_warn(warn_id: int, user_id: int, server_id: int) -> int:
    """
    This function will remove a warn from the database.

    :param warn_id: The ID of the warn.
    :param user_id: The ID of the user that was warned.
    :param server_id: The ID of the server where the user has been warned
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("DELETE FROM warns WHERE id=? AND user_id=? AND server_id=?", (warn_id, user_id, server_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?", (user_id, server_id,))
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def get_warnings(user_id: int, server_id: int) -> list:
    """
    This function will get all the warnings of a user.

    :param user_id: The ID of the user that should be checked.
    :param server_id: The ID of the server that should be checked.
    :return: A list of all the warnings of the user.
    """
    async with aiosqlite.connect("database/database.db") as db:
        rows = await db.execute("SELECT user_id, server_id, moderator_id, reason, strftime('%s', created_at), id FROM warns WHERE user_id=? AND server_id=?", (user_id, server_id,))
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row)
            return result_list