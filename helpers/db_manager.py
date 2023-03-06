""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.4
"""

import json
import random
from typing import Any, Optional, Tuple, Union

import aiohttp
import aiosqlite
import discord
import requests

#`item_id` varchar(20) NOT NULL,
#`item_name` varchar(255) NOT NULL,
#`item_price` varchar(255) NOT NULL,
#`item_emoji` varchar(255) NOT NULL,
#`item_rarity` varchar(255) NOT NULL,
#`item_type` varchar(255) NOT NULL,
#`item_damage` int(11) NOT NULL,
#`isUsable` boolean NOT NULL,
#`isEquippable` boolean NOT NULL    
      
#Items
with open("assets/items/weapons.json", "r", encoding="utf8") as f:
    weapons = json.load(f)
with open("assets/items/materials.json", "r", encoding="utf8") as f:
    materials = json.load(f)
with open("assets/items/tools.json", "r", encoding="utf8") as f:
    tools = json.load(f)
with open("assets/items/armor.json", "r", encoding="utf8") as f:
    armor = json.load(f)
with open("assets/items/consumables.json", "r", encoding="utf8") as f:
    consumables = json.load(f)
with open("assets/items/misc.json", "r", encoding="utf8") as f:
    misc = json.load(f)
basic_items = weapons + materials + tools + armor + consumables + misc
    
#Enemies
with open("assets/enemies/enemies.json", "r", encoding="utf8") as f:
    enemies = json.load(f)
with open("assets/enemies/creatures.json", "r", encoding="utf8") as f:
    creatures = json.load(f)
with open("assets/enemies/bosses.json", "r", encoding="utf8") as f:
    bosses = json.load(f)
enemies = enemies + creatures + bosses

#Quests
with open("assets/quests/quests.json", "r", encoding="utf8") as f:
    quests = json.load(f)


#chests
with open("assets/items/chests.json", "r", encoding="utf8") as f:
    chests = json.load(f)
    
#structures
with open("assets/items/structures.json", "r", encoding="utf8") as f:
    structures = json.load(f)


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
            await get_user(user_id)
            users = await db.execute(f"SELECT `money` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
            return users

#add money to a user
async def add_money(user_id: int, amount: int) -> None: 
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `money` = `money` + ? WHERE `user_id` = ?", (amount, user_id))
    else:
        #create a new user
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `money` = `money` + ? WHERE `user_id` = ?", (amount, user_id))
        

#remove money from a user
async def remove_money(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `money` = `money` - ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `money` = `money` - ? WHERE `user_id` = ?", (amount, user_id))

#add health to a user
async def add_health(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `health` = `health` + ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `health` = `health` + ? WHERE `user_id` = ?", (amount, user_id))

#remove health from a user
async def remove_health(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `health` = `health` - ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `health` = `health` - ? WHERE `user_id` = ?", (amount, user_id))

async def get_health(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `health` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    else:
        await get_user(user_id)
        users = await db.execute(f"SELECT `health` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    
#get an enemy's health
async def get_enemy_health(enemy_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `enemy_health` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    else:
        await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_health`) VALUES (?, ?)", (enemy_id, 100))
        users = await db.execute(f"SELECT `enemy_health` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    
#add health to an enemy
async def add_enemy_health(enemy_id: str, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `enemies` SET `enemy_health` = `enemy_health` + ? WHERE `enemy_id` = ?", (amount, enemy_id))
    else:
        await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_health`) VALUES (?, ?)", (enemy_id, 100))
        
#get enemy damage
async def get_enemy_damage(enemy_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `enemy_damage` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    else:
        await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_damage`) VALUES (?, ?)", (enemy_id, 10))
        users = await db.execute(f"SELECT `enemy_damage` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    
#get enemy emoji
async def get_enemy_emoji(enemy_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `enemy_emoji` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    else:
        await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_emoji`) VALUES (?, ?)", (enemy_id, "👹"))
        users = await db.execute(f"SELECT `enemy_emoji` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    
    

#remove health from an enemy
async def remove_enemy_health(enemy_id: str, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `enemies` SET `enemy_health` = `enemy_health` - ? WHERE `enemy_id` = ?", (amount, enemy_id))
    else:
        await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_health`) VALUES (?, ?)", (enemy_id, 100))

#set enemy health
async def set_enemy_health(enemy_id: str, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `enemies` SET `enemy_health` = ? WHERE `enemy_id` = ?", (amount, enemy_id))
    else:
        await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_health`) VALUES (?, ?)", (enemy_id, 100))

#add get the xp of an enemy
async def get_enemy_xp(enemy_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `enemy_xp` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    else:
        await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_xp`) VALUES (?, ?)", (enemy_id, 0))
        users = await db.execute(f"SELECT `enemy_xp` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    
#get an enemy's money
async def get_enemy_money(enemy_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `enemy_money` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    else:
        await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_money`) VALUES (?, ?)", (enemy_id, 0))
        users = await db.execute(f"SELECT `enemy_money` FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        return users
    
#get the users xp 
async def get_xp(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `player_xp` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    else:
        await get_user(user_id)
        users = await db.execute(f"SELECT `player_xp` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    
#add xp to a user
async def add_xp(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `player_xp` = `player_xp` + ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `player_xp` = `player_xp` + ? WHERE `user_id` = ?", (amount, user_id))
        
#remove xp from a user
async def remove_xp(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `player_xp` = `player_xp` - ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `player_xp` = `player_xp` - ? WHERE `user_id` = ?", (amount, user_id))
        
#set the users xp
async def set_xp(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `player_xp` = ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `player_xp` = ? WHERE `user_id` = ?", (amount, user_id))
        
#get the users level player_level
async def get_level(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `player_level` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    else:
        await get_user(user_id)
        users = await db.execute(f"SELECT `player_level` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    
#add level to a user
async def add_level(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `player_level` = `player_level` + ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await get_user(user_id)
        
#remove level from a user
async def remove_level(user_id: int, amount: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `player_level` = `player_level` - ? WHERE `user_id` = ?", (amount, user_id))
    else:
        await get_user(user_id)
    
#calculate the amount of xp needed to level up
async def xp_needed(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `player_level` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        #times the users level by 6 to get the amount of xp needed to level up
        #convert users to int
        users = int(users[0])
        xp_needed = (users * 6)
        print(xp_needed)
        return xp_needed
    else:
        await get_user(user_id)
        users = await db.execute(f"SELECT `player_level` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        users = int(users[0])
        xp_needed = (users * 6)
        print(xp_needed)
        return xp_needed
    
#check if a user can level up
async def can_level_up(user_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `player_xp` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if users[0] >= await xp_needed(user_id):
            return True
        else:
            return False
    else:
        await get_user(user_id)
        users = await db.execute(f"SELECT `player_xp` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if users[0] >= await xp_needed(user_id):
            return True
        else:
            return False
    
#get user, if they don't exist, create them
async def get_user(user_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return None
    else:
        
  #`user_id` varchar(20) NOT NULL,
  #`money` int(11) NOT NULL,
  #`health` int(11) NOT NULL,
  #`isStreamer` boolean NOT NULL,
  #`isBurning` boolean NOT NULL,
  #`isPoisoned` boolean NOT NULL,
  #`isFrozen` boolean NOT NULL,
  #`isParalyzed` boolean NOT NULL,
  #`isBleeding` boolean NOT NULL,
  #`isDead` boolean NOT NULL,
  #`isInCombat` boolean NOT NULL,
  #`player_xp` int(11) NOT NULL,
  #`player_level` int(11) NOT NULL,
  #`quest_id` varchar(255) NOT NULL,
  #`twitch_id` varchar(255) NOT NULL,
  #`twitch_name` varchar(255) NOT NULL,
  #`dodge_chance` int(11) NOT NULL,
  #`crit_chance` int(11) NOT NULL,
  #`damage_boost` int(11) NOT NULL,
  #`health_boost` int(11) NOT NULL,
  #`fire_resistance` int(11) NOT NULL,
  #`poison_resistance` int(11) NOT NULL,
  #`frost_resistance` int(11) NOT NULL,
  #`paralysis_resistance` int(11) NOT NULL,
        
        #add the user to the database with all the data from above + the new quest data + the new twitch data + the new dodge chance + the new crit chance + the new damage boost + the new health boost + the new fire resistance + the new poison resistance + the new frost resistance + the new paralysis resistance
        await db.execute("INSERT INTO users (user_id, money, health, isStreamer, isBurning, isPoisoned, isFrozen, isParalyzed, isBleeding, isDead, isInCombat, player_xp, player_level, quest_id, twitch_id, twitch_name, dodge_chance, crit_chance, damage_boost, health_boost, fire_resistance, poison_resistance, frost_resistance, paralysis_resistance, luck) VALUES (?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(user_id, 0, 100, False, False, False, False, False, False, False, False, 0, 1, "None", "None", "None", 0, 0, 0, 0, 0, 0, 0, 0, 0))
        return None
        
        
#get a users luck 
async def get_luck(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        luck = await db.execute(f"SELECT `luck` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        luck = int(luck[0])
        return luck
    else:
        await get_user(user_id)
        luck = await db.execute(f"SELECT `luck` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        luck = int(luck[0])
        return luck

#add lcuk to a user
async def add_luck(user_id: int, luck: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `luck` = `luck` + ? WHERE `user_id` = ?", (luck, user_id))
    else:
        #create a new user
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `luck` = `luck` + ? WHERE `user_id` = ?", (luck, user_id))

#remove luck from a user
async def remove_luck(user_id: int, luck: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `luck` = `luck` - ? WHERE `user_id` = ?", (luck, user_id))
    else:
        #create a new user
        await get_user(user_id)
        await db.execute(f"UPDATE `users` SET `luck` = `luck` - ? WHERE `user_id` = ?", (luck, user_id))
    
#set luck to a user
async def set_luck(user_id: int, luck: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `luck` = ? WHERE `user_id` = ?", (luck, user_id))
    else:
        return None
    
#connect a twitch account to a discord account
async def connect_twitch_id(user_id: int, twitch_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `twitch_id` = ? WHERE `user_id` = ?", (twitch_id, user_id))
    else:
        return None
        
#add a twitch name to a discord account
async def connect_twitch_name(user_id: int, twitch_name: str) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `twitch_name` = ? WHERE `user_id` = ?", (twitch_name, user_id))
    else:
        return None

#disconnect a twitch account from a discord account
async def disconnect_twitch_id(user_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `twitch_id` = ? WHERE `user_id` = ?", ("None", user_id))
    else:
        return None
    
#disconnect a twitch account from a discord account
async def disconnect_twitch_name(user_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `twitch_name` = ? WHERE `user_id` = ?", ("None", user_id))
    else:
        return None

#check if a user is connected to a twitch account
async def is_connected(user_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `twitch_id` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if users[0] == "None" or users[0] == None:
            return False
        else:
            return True
    else:
        return False
    
#check if a twitch account is connected to a discord account
async def is_twitch_connected(twitch_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE twitch_id = ?", (twitch_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `user_id` FROM `users` WHERE twitch_id = ?", (twitch_id,), fetch="one")
        if users[0] == "None" or users[0] == None:
            return False
        else:
            return True
    else:
        return False
    
#get the discord id of a twitch account
async def get_user_id(twitch_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE twitch_id = ?", (twitch_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `user_id` FROM `users` WHERE twitch_id = ?", (twitch_id,), fetch="one")
        return users[0]
    else:
        return None
    
#check if a twitch_id already exists in the database
async def twitch_exists(twitch_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE twitch_id = ?", (twitch_id,), fetch="one")
    if data is not None:
        return True
    else:
        return False
    
#return a list of all items in the database
async def get_all_basic_items() -> list:
    db = DB()
    data = await db.execute(f"SELECT * FROM `basic_items`", fetch="all")
    return data

#return a list of all of a streamers created items by channel name
async def get_all_streamer_items(twitch_id: int) -> list:
    db = DB()
    data = await db.execute(f"SELECT * FROM `streamer_items` WHERE twitch_id = ?", (twitch_id,), fetch="all")
    return data


#make sure no two users have the same twitch account
async def is_unique(twitch_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE twitch_id = ?", (twitch_id,), fetch="one")
    if data is not None:
        return False
    else:
        return True

#check if a user is not dead
async def is_alive(user_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `isDead` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if users[0] == 0:
            return True
        else:
            return False
    else:
        return False
    
#set a user's dead status to true
async def set_dead(user_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `isDead` = ? WHERE `user_id` = ?", (True, user_id))
    else:
        return None
        
#set a user's dead status to false
async def set_alive(user_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `isDead` = ? WHERE `user_id` = ?", (False, user_id))
    else:
        return None

async def check_if_user_in_db(user_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return True
    else:
        return False

#check if a user is in combat
async def is_in_combat(user_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT `isInCombat` FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if users[0] == 0:
            return False
        else:
            return True
        
#set a user's InCombat status to true
async def set_in_combat(user_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `isInCombat` = ? WHERE `user_id` = ?", (True, user_id))
    else:
        return False

#set a user's InCombat status to false
async def set_not_in_combat(user_id: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `isInCombat` = ? WHERE `user_id` = ?", (False, user_id))
    else:
        return False

#set a user's health
async def set_health(user_id: int, health: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `users` SET `health` = ? WHERE `user_id` = ?", (health, user_id))
    else:
        return None

#look at a user's profile, returns a list
async def profile(user_id: int) -> list:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        users = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users
    else:
        await db.execute("INSERT INTO users (user_id, money, health, isStreamer, isBurning, isPoisoned, isFrozen, isParalyzed, isBleeding, isDead, isInCombat, player_xp, player_level, quest_id, twitch_id, twitch_name, dodge_chance, crit_chance, damage_boost, health_boost, fire_resistance, poison_resistance, frost_resistance, paralysis_resistance, luck) VALUES (?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(user_id, 0, 100, False, False, False, False, False, False, False, False, 0, 1, "None", "None", "None", 0, 0, 0, 0, 0, 0, 0, 0, 0))
        users = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        return users

#add the basic items to the database basic_items table
async def add_basic_items() -> None:
    db = DB()
    for item in basic_items:
        data = await db.execute(f"SELECT * FROM `basic_items` WHERE item_id = ?", (item['item_id'],), fetch="one")
        if data is not None:
            #delete the item from the database, then add it again
            await db.execute(f"DELETE FROM `basic_items` WHERE item_id = ?", (item['item_id'],))
            await db.execute(f"INSERT INTO `basic_items` (`item_id`, `item_name`, `item_price`, `item_emoji`, `item_rarity`, `item_type`, `item_damage`, `isUsable`, `inShop`, `isEquippable`, `item_description`, `item_element`, `item_crit_chance`, `item_projectile`, `recipe_id`, `isHuntable`, `item_hunt_chance`, `item_effect`, `isMineable`, `item_mine_chance`, quote_id, item_sub_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (item['item_id'], item['item_name'], item['item_price'], item['item_emoji'], item['item_rarity'], item['item_type'], item['item_damage'], item['isUsable'], item['inShop'], item['isEquippable'], item['item_description'], item['item_element'], item['item_crit_chance'], item['item_projectile'], item['recipe_id'], item['isHuntable'], item['item_hunt_chance'], item['item_effect'], item['isMineable'], item['item_mine_chance'], item['quote_id'], item['item_sub_type']))
            print(f"Updated {item['item_name']}")
            if item['quote_id'] != "None":
                #remove the old quotes from the database
                await db.execute(f"DELETE FROM `item_quotes` WHERE item_id = ?", (item['quote_id'],))
                #for each item in the recipe add it to the database with the item_id being the recipe_id
                for quote in item['item_quotes']:
                    await db.execute(f"INSERT INTO `item_quotes` (`item_id`, `quote`) VALUES (?, ?)", (item['quote_id'], quote['quote']))
                    print(f"Updated Quote: |{quote['quote']}| to the item_quotes for |{item['item_name']}|")
                print(f"Updated |{item['item_name']}|'s item_quotes to the database")
            if item['recipe_id'] != "None":
                #remove the old recipes from the database
                await db.execute(f"DELETE FROM `recipes` WHERE item_id = ?", (item['recipe_id'],))
                #for each item in the recipe add it to the database with the item_id being the recipe_id
                for ingredient in item['item_recipe']:
                    await db.execute(f"INSERT INTO `recipes` (`item_id`, `ingredient_id`, `ingredient_amount`) VALUES (?, ?, ?)", (item['recipe_id'], ingredient['ingredient_id'], ingredient['ingredient_amount']))
                    print(f"Updated Ingredient: |{ingredient['ingredient_id']}| to the recipe for |{item['item_name']}|")
                print(f"Updated |{item['item_name']}|'s recipe to the database")
            pass
        else:
            #CREATE TABLE IF NOT EXISTS `basic_items` (
            #`item_id` varchar(255) PRIMARY KEY,
            #`item_name` varchar(255) NOT NULL,
            #`item_price` varchar(255) NOT NULL,
            #`item_emoji` varchar(255) NOT NULL,
            #`item_rarity` varchar(255) NOT NULL,
            #`item_type` varchar(255) NOT NULL,
            #`item_damage` int(11) NOT NULL,
            #`isUsable` boolean NOT NULL,
            #`inShop` boolean NOT NULL,
            #`isEquippable` boolean NOT NULL,
            #`item_description` varchar(255) NOT NULL,
            #`item_element` varchar(255) NOT NULL,
            #`item_crit_chance` int(11) NOT NULL,
            #`item_projectile` varchar(255) NOT NULL,
            #`recipe_id` varchar(255) NOT NULL,
            #`isHuntable` boolean NOT NULL,
            #`item_hunt_chance` int(11) NOT NULL,
            #`item_effect` varchar(255) NOT NULL,
            #`isMineable` boolean NOT NULL,
            #`item_mine_chance` int(11) NOT NULL,
            
            #add the item to the database
            await db.execute(f"INSERT INTO `basic_items` (`item_id`, `item_name`, `item_price`, `item_emoji`, `item_rarity`, `item_type`, `item_damage`, `isUsable`, `inShop`, `isEquippable`, `item_description`, `item_element`, `item_crit_chance`, `item_projectile`, `recipe_id`, `isHuntable`, `item_hunt_chance`, `item_effect`, `isMineable`, `item_mine_chance`, quote_id, item_sub_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (item['item_id'], item['item_name'], item['item_price'], item['item_emoji'], item['item_rarity'], item['item_type'], item['item_damage'], item['isUsable'], item['inShop'], item['isEquippable'], item['item_description'], item['item_element'], item['item_crit_chance'], item['item_projectile'], item['recipe_id'], item['isHuntable'], item['item_hunt_chance'], item['item_effect'], item['isMineable'], item['item_mine_chance'], item['quote_id'], item['item_sub_type']))
            print(f"Added |{item['item_name']}| to the database")
            
            #add the items recipe to the database
            #CREATE TABLE IF NOT EXISTS recipes (
            # item_id VARCHAR(255) NOT NULL,
            # ingredient_id VARCHAR(255) NOT NULL,
            # ingredient_amount INTEGER NOT NULL
            if item['quote_id'] != "None":
                #for each item in the recipe add it to the database with the item_id being the recipe_id
                for quote in item['item_quotes']:
                    await db.execute(f"INSERT INTO `item_quotes` (`item_id`, `quote`) VALUES (?, ?)", (item['quote_id'], quote['quote']))
                    print(f"Added Quote: |{quote['quote']}| to the item_quotes for |{item['item_name']}|")
                print(f"Added |{item['item_name']}|'s item_quotes to the database")
            if item['recipe_id'] != "None":
                #for each item in the recipe add it to the database with the item_id being the recipe_id
                for ingredient in item['item_recipe']:
                    await db.execute(f"INSERT INTO `recipes` (`item_id`, `ingredient_id`, `ingredient_amount`) VALUES (?, ?, ?)", (item['recipe_id'], ingredient['ingredient_id'], ingredient['ingredient_amount']))
                    print(f"Added Ingredient: |{ingredient['ingredient_id']}| to the recipe for |{item['item_name']}|")
                print(f"Added |{item['item_name']}|'s recipe to the database")

async def add_structures() -> None:
    db = DB()
    # Insert data into structures table
    for structure in structures['structures']:
        structure_id = structure['structure_id']
        structure_name = structure['structure_name']
        structure_image = structure['structure_image']
        structure_description = structure['structure_description']
        structure_outcomesID = structure['structure_outcomesID']
        await db.execute("INSERT INTO structures (structure_id, structure_name, structure_image, structure_description, structure_outcomesID) VALUES (?, ?, ?, ?, ?)", (structure_id, structure_name, structure_image, structure_description, structure_outcomesID))
        print(f"Added |{structure_name}| to the structures table")
        
        
        # Insert data into structure_outcomes table
        for outcome in structure['structure_outcomes']:
            structure_quote = outcome['structure_quote']
            structure_state = outcome['structure_state']
            outcome_chance = outcome['outcome_chance']
            outcome_type = outcome['outcome_type']
            outcome_output = outcome['outcome_output']
            outcome_amount = outcome['outcome_amount']
            outcome_money = outcome['outcome_money']
            outcome_xp = outcome['outcome_xp']
            
            # Insert data into structure_outcomes table
            await db.execute("INSERT INTO structure_outcomes (structure_id, structure_quote, structure_state, outcome_chance, outcome_type, outcome, outcome_amount, outcome_money, outcome_xp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (structure_id, structure_quote, structure_state, outcome_chance, outcome_type, outcome_output, outcome_amount, outcome_money, outcome_xp))
            print(f"Added |{structure_state}, {outcome_type}, {outcome_output}/{outcome_amount}| to the |{structure_name}| structure")
    

#add the chests to the chest table
async def add_chests() -> None:
    db = DB()
    for chest in chests:
        data = await db.execute(f"SELECT * FROM `chests` WHERE chest_id = ?", (chest['chest_id'],), fetch="one")
        if data is not None:
            await db.execute(f"INSERT INTO `chests` (`chest_id`, `chest_name`, `chest_emoji`, `chest_rarity`, `chest_price`, `chest_type`, `chest_description`, `key_id`, `chest_contentsID`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (chest['chest_id'], chest['chest_name'], chest['chest_emoji'], chest['chest_rarity'], chest['chest_price'], chest['chest_type'], chest['chest_description'], chest['key_id'], chest['chest_contentsID']))
            print(f"Updated |{chest['chest_name']}| to the database")
            
            #add the chests contents to the database
            if chest['chest_contentsID'] != "None":
                for item in chest['chest_contents']:
                    await db.execute(f"INSERT INTO `chest_contents` (`chest_id`, `item_id`, `item_amount`, `drop_chance`) VALUES (?, ?, ?, ?)", (chest['chest_contentsID'], item['item_id'], item['item_amount'], item['drop_chance']))
                    print(f"Updated |{item['item_id']}| to the chest |{chest['chest_name']}| with a drop chance of |{item['drop_chance']}|")
                print(f"Updated |{chest['chest_name']}|'s contents to the database")
            
        else:
            #  item_id int(11) NOT NULL,
            #  item_name varchar(255) NOT NULL,
            #  item_price varchar(255) NOT NULL,
            #  item_emoji varchar(255) NOT NULL,
            #  item_rarity varchar(255) NOT NULL,
            #  item_type varchar(255) NOT NULL,
            #  item_description varchar(255) NOT NULL,
            #  key_id varchar(255) NOT NULL,
            #  chest_contentsID varchar(255) NOT NULL
            #  FOREIGN KEY (key_id) REFERENCES basic_items(item_id)
            #  FOREIGN KEY (chest_contentsID) REFERENCES chest_contents(item_id)
            #);
            #
            #CREATE TABLE IF NOT EXISTS `chest_contents` (
            #  `chest_id` varchar(255) NOT NULL,
            #  `item_id` varchar(255) NOT NULL,
            #  `item_amount` int(11) NOT NULL,
            #  `drop_chance` int(11) NOT NULL,
            #);
            
            #add the chest to the database
            await db.execute(f"INSERT INTO `chests` (`chest_id`, `chest_name`, `chest_emoji`, `chest_rarity`, `chest_price`, `chest_type`, `chest_description`, `key_id`, `chest_contentsID`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (chest['chest_id'], chest['chest_name'], chest['chest_emoji'], chest['chest_rarity'], chest['chest_price'], chest['chest_type'], chest['chest_description'], chest['key_id'], chest['chest_contentsID']))
            print(f"Added |{chest['chest_name']}| to the database")
            
            #add the chests contents to the database
            if chest['chest_contentsID'] != "None":
                for item in chest['chest_contents']:
                    await db.execute(f"INSERT INTO `chest_contents` (`chest_id`, `item_id`, `item_amount`, `drop_chance`) VALUES (?, ?, ?, ?)", (chest['chest_contentsID'], item['item_id'], item['item_amount'], item['drop_chance']))
                    print(f"Added |{item['item_id']}| to the chest |{chest['chest_name']}| with a drop chance of |{item['drop_chance']}|")
                print(f"Added |{chest['chest_name']}|'s contents to the database")
            
            

#function to add all the items with inShop = True to the shop table and then add a random int between 1 and 10 to the amount column
async def add_shop_items() -> None:
    db = DB()
    #clear the shop table
    await db.execute(f"DELETE FROM `shop`")
    data = await db.execute(f"SELECT * FROM `basic_items` WHERE inShop = ?", (True,), fetch="all")
    #only add 10 items to the shop
    data = random.sample(data, 10)
    for item in data:
        ItemAmount = random.randint(1, 15)
        await db.execute(f"INSERT INTO `shop` (`item_id`, `item_name`, `item_price`, `item_emoji`, `item_rarity`, `item_type`, `item_damage`, `isUsable`, `isEquippable`, `item_amount`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[9], ItemAmount))
        print(f"Added |{item[1]} x{ItemAmount}| to the shop")
        
#clear the shop table
async def clear_shop() -> None:
    db = DB()
    await db.execute(f"DELETE FROM `shop`")
    print("Cleared the shop table")
        
#add the enemies to the database enemies table
async def add_enemies() -> None:
    db = DB()
    for enemy in enemies:
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy['enemy_id'],), fetch="one")
        if data is not None:
            await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_name`, `enemy_health`, `enemy_damage`, `enemy_emoji`, `enemy_description`, `enemy_rarity`, `enemy_type`, `enemy_xp`, `enemy_money`, `enemy_crit_chance`, `enemy_drop_id`, `enemy_element`, `isFrozen`, `isBurning`, `isPoisoned`, `isParalyzed`, `quote_id`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (enemy['enemy_id'], enemy['enemy_name'], enemy['enemy_health'], enemy['enemy_damage'], enemy['enemy_emoji'], enemy['enemy_description'], enemy['enemy_rarity'], enemy['enemy_type'], enemy['enemy_xp'], enemy['enemy_money'], enemy['enemy_crit_chance'], enemy['enemy_drop_id'], enemy['enemy_element'], False, False, False, False, enemy['quote_id']))
            print(f"Updated |{enemy['enemy_name']}| to the database")
            
            #add enemy quotes to the database
            if enemy['quote_id'] != "None":
                #delete the enemy quotes from the database
                await db.execute(f"DELETE FROM `enemy_quotes` WHERE enemy_id = ?", (enemy['enemy_id'],))
                #for each item in the recipe add it to the database with the item_id being the recipe_id
                for quote in enemy['enemy_quotes']:
                    await db.execute(f"INSERT INTO `enemy_quotes` (`enemy_id`, `quote`) VALUES (?, ?)", (enemy['quote_id'], quote['quote']))
                    print(f"Updated Quote: |{quote['quote']}| to the enemy_quotes for |{enemy['enemy_name']}|")
                print(f"Updated |{enemy['enemy_name']}|'s enemy_quotes to the database")
                    
            #add the enemies drops to the database
            if enemy['enemy_drop_id'] != "None":
                #delete the enemy drops from the database
                await db.execute(f"DELETE FROM `enemy_drops` WHERE enemy_id = ?", (enemy['enemy_id'],))
                #  `enemy_id` varchar(20) NOT NULL,
                #`item_id` varchar(20) NOT NULL,
                #`item_amount` int(11) NOT NULL,
                #`item_drop_chance` int(11) NOT NULL
                #for each item in the recipe add it to the database with the item_id being the recipe_id
                for drop in enemy['enemy_drops']:
                    await db.execute(f"INSERT INTO `enemy_drops` (`enemy_id`, `item_id`, `item_amount`, `item_drop_chance`) VALUES (?, ?, ?, ?)", (enemy['enemy_id'], drop['item_id'], drop['item_amount'], drop['item_drop_chance']))
                    print(f"Updated Drop: |{drop['item_id']} x{drop['item_amount']}| with drop chance |{drop['item_drop_chance']}| to |{enemy['enemy_name']}|'s Drops")
                print(f"Updated |{enemy['enemy_name']}|'s Drops to the database" + '\n')
        else:
            #`enemy_id` varchar(20) NOT NULL,
            #`enemy_name` varchar(255) NOT NULL,
            #`enemy_health` int(11) NOT NULL,
            #`enemy_damage` int(11) NOT NULL,
            #`enemy_emoji` varchar(255) NOT NULL,
            #`enemy_description` varchar(255) NOT NULL,
            #`enemy_rarity` varchar(255) NOT NULL,
            #`enemy_type` varchar(255) NOT NULL,
            #`enemy_xp` int(11) NOT NULL,
            #`enemy_money` int(11) NOT NULL,
            #`enemy_crit_chance` int(11) NOT NULL,
            #`enemy_drop_id` varchar(255) NOT NULL,
            #`enemy_element` varchar(255) NOT NULL,
            #`isFrozen ` boolean NOT NULL,
            #`isBurning` boolean NOT NULL,
            #`isPoisoned` boolean NOT NULL,
            #`isParalyzed` boolean NOT NULL,
            #quote_id varchar(255) NOT NULL,
            
            #add the enemys properties to the database
            await db.execute(f"INSERT INTO `enemies` (`enemy_id`, `enemy_name`, `enemy_health`, `enemy_damage`, `enemy_emoji`, `enemy_description`, `enemy_rarity`, `enemy_type`, `enemy_xp`, `enemy_money`, `enemy_crit_chance`, `enemy_drop_id`, `enemy_element`, `isFrozen`, `isBurning`, `isPoisoned`, `isParalyzed`, `quote_id`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (enemy['enemy_id'], enemy['enemy_name'], enemy['enemy_health'], enemy['enemy_damage'], enemy['enemy_emoji'], enemy['enemy_description'], enemy['enemy_rarity'], enemy['enemy_type'], enemy['enemy_xp'], enemy['enemy_money'], enemy['enemy_crit_chance'], enemy['enemy_drop_id'], enemy['enemy_element'], False, False, False, False, enemy['quote_id']))
            print(f"Added |{enemy['enemy_name']}| to the database")
            
            #add enemy quotes to the database
            if enemy['quote_id'] != "None":
                #for each item in the recipe add it to the database with the item_id being the recipe_id
                for quote in enemy['enemy_quotes']:
                    await db.execute(f"INSERT INTO `enemy_quotes` (`enemy_id`, `quote`) VALUES (?, ?)", (enemy['quote_id'], quote['quote']))
                    print(f"Added Quote: |{quote['quote']}| to the enemy_quotes for |{enemy['enemy_name']}|")
                print(f"Added |{enemy['enemy_name']}|'s enemy_quotes to the database")
                    
            #add the enemies drops to the database
            if enemy['enemy_drop_id'] != "None":
                #  `enemy_id` varchar(20) NOT NULL,
                #`item_id` varchar(20) NOT NULL,
                #`item_amount` int(11) NOT NULL,
                #`item_drop_chance` int(11) NOT NULL
                #for each item in the recipe add it to the database with the item_id being the recipe_id
                for drop in enemy['enemy_drops']:
                    await db.execute(f"INSERT INTO `enemy_drops` (`enemy_id`, `item_id`, `item_amount`, `item_drop_chance`) VALUES (?, ?, ?, ?)", (enemy['enemy_id'], drop['item_id'], drop['item_amount'], drop['item_drop_chance']))
                    print(f"Added Drop: |{drop['item_id']} x{drop['item_amount']}| with drop chance |{drop['item_drop_chance']}| to |{enemy['enemy_name']}|'s Drops")
                print(f"Added |{enemy['enemy_name']}|'s Drops to the database" + '\n')
                    
                
            
#add quests to the database
async def add_quests() -> None:
  #`quest_id` varchar(20) NOT NULL,
  #`quest_name` varchar(255) NOT NULL,
  #`quest_description` varchar(255) NOT NULL,
  #`quest_xp_reward` int(11) NOT NULL,
  #`quest_reward` varchar(255) NOT NULL,
  #`quest_reward_amount` int(11) NOT NULL,
  #`quest_level_required` int(11) NOT NULL,
  #`quest_type` varchar(255) NOT NULL,
  #`quest` varchar(255) NOT NULL,
  #`OnBoard` boolean NOT NULL,
  
  #add the quests to the database, check if they are already in the database
    db = DB()
    for quest in quests:
        data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest['quest_id'],), fetch="one")
        if data is not None:
            print(f"|{quest['quest_name']}| is already in the database")
            pass
        else:
            await db.execute("INSERT INTO `quests` (`quest_id`, `quest_name`, `quest_description`, `quest_xp_reward`, `quest_reward_type`, `quest_reward`, `quest_reward_amount`, `quest_level_required`, `quest_type`, `quest`, `OnBoard`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (quest['quest_id'], quest['quest_name'], quest['quest_description'], quest['quest_xp_reward'], quest['quest_reward_type'], quest['quest_reward'], quest['quest_reward_amount'], quest['quest_level_required'], quest['quest_type'], quest['quest'], quest['OnBoard']))
            print(f"Added |{quest['quest_name']}| to the database")
        
    
#add the quests to the board if they have the OnBoard property set to True, check if they are already on the board
async def add_quests_to_board() -> None:
    db = DB()
    for quest in quests:
        data = await db.execute(f"SELECT * FROM `questBoard` WHERE quest_id = ?", (quest['quest_id'],), fetch="one")
        if data is not None:
            print(f"|{quest['quest_name']}| is already on the board")
            pass
        else:
            if quest['OnBoard'] == True:
                await db.execute("INSERT INTO `questBoard` (`quest_id`, `quest_name`, `quest_description`, `quest_xp_reward`, `quest_reward`, `quest_reward_amount`, `quest_level_required`, `quest_type`, `quest`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (quest['quest_id'], quest['quest_name'], quest['quest_description'], quest['quest_xp_reward'], quest['quest_reward'], quest['quest_reward_amount'], quest['quest_level_required'], quest['quest_type'], quest['quest']))
                print(f"Added |{quest['quest_name']}| to the board")
                
#create an entry in questProgress for a user and a quest
async def create_quest_progress(user_id: int, quest_id: str) -> None:
    db = DB()
    await db.execute("INSERT INTO `questProgress` (`user_id`, `quest_id`, `quest_progress`, `quest_completed`) VALUES (?, ?, 0, False)", (user_id, quest_id))

#get the quest progress of a user
async def get_quest_progress(user_id: int, quest_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `questProgress` WHERE user_id = ? AND quest_id = ?", (user_id, quest_id), fetch="one")
    if data is not None:
        return data[2]
    else:
        return 0
    
#get quest from quest ID
async def get_quest_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        quest = data[9]
        quest = str(quest)
        #get the second part of the quest, the part that is the enemy or item
        quest = quest.split(" ")[1]
        return quest
    else:
        return 0
    
#get quest item / enemy from quest ID
async def get_quest_item_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[9]
    
    else:
        return 0
    
#get quest reward from quest ID
async def get_quest_reward_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[5]
    else:
        return 0
    
#get quest total from quest ID
async def get_quest_total_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        #get data[9] and remove all letters and spaces from it
        quest = data[9]
        quest = str(quest)
        quest = quest.replace(" ", "")
        #remove all letters
        quest = ''.join(filter(str.isdigit, quest))
        return quest
    else:
        return 0
    
#get what quest a user has 
async def get_user_quest(user_id: int) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `questProgress` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[1]
    else:
        return 0
    
#get the quest objective from its ID
async def get_quest_objective_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[9]
    else:
        return 0
    
#get the quest reward type from its ID
async def get_quest_reward_type_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[4]
    else:
        return 0
    
#get quest reward amount from quest ID
async def get_quest_reward_amount_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[6]
    else:
        return 0

#get the quest reward amount from its ID
async def get_quest_reward_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[5]
    else:
        return 0

#get the quest xp reward from its ID
async def get_quest_xp_reward_from_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[3]
    else:
        return 0

#update the progress of a quest for a user
async def update_quest_progress(user_id: int, quest_id: str, quest_progress: int) -> None:
    db = DB()
    await db.execute("UPDATE `questProgress` SET quest_progress = ? WHERE user_id = ? AND quest_id = ?", (quest_progress, user_id, quest_id))
    
#mark a quest as completed for a user
async def mark_quest_completed(user_id: int, quest_id: str) -> None:
    db = DB()
    await db.execute("UPDATE `questProgress` SET quest_completed = ? WHERE user_id = ? AND quest_id = ?", (True, user_id, quest_id))

#check if a user has completed a quest
async def check_quest_completed(user_id: int, quest_id: str) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `questProgress` WHERE user_id = ? AND quest_id = ? AND quest_completed = ?", (user_id, quest_id, True), fetch="one")
    if data is not None:
        return True
    else:
        return False
    
#get quest level requirements
async def get_quest_level_required(quest_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[7]
    else:
        return 0
    
#get the quest type
async def get_quest_type(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[8]
    else:
        return None
    
    
#get a quests name from the Id
async def get_quest_name_from_quest_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[1]
    else:
        return None
    
#get a quests description from the Id
async def get_quest_description_from_quest_id(quest_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_id = ?", (quest_id,), fetch="one")
    if data is not None:
        return data[2]
    else:
        return None
            
#get quests on the board
async def get_quests_on_board() -> list:
    db = DB()
    data = await db.execute("SELECT * FROM `questBoard`", fetch="all")
    if data is not None:
        return data
    else:
        return None

#get quest id from quest name
async def get_quest_id_from_quest_name(quest_name: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `quests` WHERE quest_name = ?", (quest_name,), fetch="one")
    if data is not None:
        return data[0]
    else:
        return None
    
    
#check if a user has a specific quest in their quest slots
async def check_user_has_quest(user_id: int, quest_id: str) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ? AND quest_id = ?", (user_id, quest_id), fetch="one")
    if data is not None:
        return True
    else:
        return False
    
#give a user a specific quest
async def give_user_quest(user_id: int, quest_id: str) -> None:
    db = DB()
    await db.execute("UPDATE `users` SET quest_id = ? WHERE user_id = ?", (quest_id, user_id))
    
#check if a user has any quest
async def check_user_has_any_quest(user_id: int) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ? AND quest_id != ?", (user_id, "None"), fetch="one")
    if data is not None:
        return True
    else:
        return False
    
#remove a quest from a user
async def remove_quest_from_user(user_id: int) -> None:
    db = DB()
    await db.execute("UPDATE `users` SET quest_id = ? WHERE user_id = ?", ("None", user_id))
    
#check if the enemy is in the database
async def check_enemy(enemy_id: str) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        return True
    else:
        return False

#get the monster name from its ID
async def get_enemy_name(enemy_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        return data[1]
    else:
        return None

#get the monster description from its ID
async def get_enemy_description(enemy_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        return data[5]
    else:
        return None
    
#get the enemy drop from its ID
async def get_enemy_drop(enemy_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        return data[11]
    else:
        return None
    
#get enemy drops from the enemy_drops table from the enemy ID
async def get_enemy_drops(enemy_id: str) -> list:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemy_drops` WHERE enemy_id = ?", (enemy_id,), fetch="all")
    if data is not None:
        return data
    else:
        return None
    
    
#get the enemy drop chance from its ID
async def get_enemy_drop_chance(enemy_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        return data[12]
    elif data[12] == 0 or data[12] == None or data[12] == "" or data[12] == "None":
        return 0
    
#get the enemy drop amount min from its ID
async def get_enemy_drop_amount_min(enemy_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        return data[14]
    else:
        return 0

#get the enemy drop amount max from its ID
async def get_enemy_drop_amount_max(enemy_id: str) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        return data[15]
    else:
        return 0
    
#get the drop chance from its ID
async def get_enemy_drop_rarity(enemy_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
    if data is not None:
        return data[16]
    else:
        return None
    
#get the enemy quotes from its ID from the enemy_quotes table
#fix
async def get_enemy_quotes(enemy_id: str) -> list:
    db = DB()
    data = await db.execute(f"SELECT * FROM `enemy_quotes` WHERE enemy_id = ?", (enemy_id,), fetch="all")
    if data is not None:
        return data[1]
    else:
        return None
    
#get the item quotes from its ID, from the item_quotes table
async def get_item_quotes(item_id: str) -> list:
    db = DB()
    data = await db.execute(f"SELECT * FROM `item_quotes` WHERE item_id = ?", (item_id,), fetch="all")
    if data is not None:
        return data
    else:
        return None
    
#get the players stats from the stats table using the user ID
async def get_player_stats(user_id: int) -> list:
    db = DB()
    data = await db.execute(f"SELECT * FROM `stats` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data
    else:
        return None
    
#make commands to add and remove the following stats
  #`money_earned`
  #`money_spent` 
  #`items_bought`
  #`items_sold``
  #`items_used`
  #`items_equipped`
  #`quests_completed`
  #`enemies_killed` 
  #`users_killed`
  #`battles_fought` 
  #`battles_won`
  
#add money earned
async def add_money_earned(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET money_earned = money_earned + ? WHERE user_id = ?", (amount, user_id))
    
#remove money earned
async def remove_money_earned(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET money_earned = money_earned - ? WHERE user_id = ?", (amount, user_id))

#add money spent
async def add_money_spent(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET money_spent = money_spent + ? WHERE user_id = ?", (amount, user_id))
    
#remove money spent
async def remove_money_spent(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET money_spent = money_spent - ? WHERE user_id = ?", (amount, user_id))
    
#get the item id from its name
async def get_item_id(item_name: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `basic_items` WHERE item_name = ?", (item_name,), fetch="one")
    if data is not None:
        return data[0]
    else:
        return None
#add items bought
async def add_items_bought(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET items_bought = items_bought + ? WHERE user_id = ?", (amount, user_id))
    
#remove items bought
async def remove_items_bought(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET items_bought = items_bought - ? WHERE user_id = ?", (amount, user_id))
    
#add items sold
async def add_items_sold(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET items_sold = items_sold + ? WHERE user_id = ?", (amount, user_id))
    
#remove items sold
async def remove_items_sold(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET items_sold = items_sold - ? WHERE user_id = ?", (amount, user_id))
    
#add items used
async def add_items_used(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET items_used = items_used + ? WHERE user_id = ?", (amount, user_id))
    
#remove items used
async def remove_items_used(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET items_used = items_used - ? WHERE user_id = ?", (amount, user_id))
    
#add items equipped
async def add_items_equipped(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET items_equipped = items_equipped + ? WHERE user_id = ?", (amount, user_id))
    
#remove items equipped
async def remove_items_equipped(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET items_equipped = items_equipped - ? WHERE user_id = ?", (amount, user_id))
    
#add quests completed
async def add_quests_completed(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET quests_completed = quests_completed + ? WHERE user_id = ?", (amount, user_id))
    
#remove quests completed
async def remove_quests_completed(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET quests_completed = quests_completed - ? WHERE user_id = ?", (amount, user_id))
    
#add enemies killed
async def add_enemies_killed(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET enemies_killed = enemies_killed + ? WHERE user_id = ?", (amount, user_id))
    
#remove enemies killed
async def remove_enemies_killed(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET enemies_killed = enemies_killed - ? WHERE user_id = ?", (amount, user_id))
    
#add users killed
async def add_users_killed(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET users_killed = users_killed + ? WHERE user_id = ?", (amount, user_id))
    
#remove users killed
async def remove_users_killed(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET users_killed = users_killed - ? WHERE user_id = ?", (amount, user_id))

#add battles fought
async def add_battles_fought(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET battles_fought = battles_fought + ? WHERE user_id = ?", (amount, user_id))
    
#remove battles fought
async def remove_battles_fought(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET battles_fought = battles_fought - ? WHERE user_id = ?", (amount, user_id))
    
#add battles won
async def add_battles_won(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET battles_won = battles_won + ? WHERE user_id = ?", (amount, user_id))
    
#remove battles won
async def remove_battles_won(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET battles_won = battles_won - ? WHERE user_id = ?", (amount, user_id))

#create commands to add and remove the following user stats:
  #`dodge_chance`
  #`crit_chance` 
  #`damage_boost`
  #`health_boost`
  #`fire_resistance`
  #`poison_resistance`
  #`frost_resistance` 
  #`paralysis_resistance`
  
#get the user's dodge chance
async def get_dodge_chance(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[16]
    else:
        return None
    

#get the user's crit chance
async def get_crit_chance(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[17]
    else:
        return None
    
#get the user's damage boost
async def get_damage_boost(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[18]
    else:
        return None
    
#get the user's health boost
async def get_health_boost(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[19]
    else:
        return None
    
#get the user's fire resistance
async def get_fire_resistance(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[20]
    else:
        return None
    
#get the user's poison resistance
async def get_poison_resistance(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[21]
    else:
        return None
    
#get the user's frost resistance
async def get_frost_resistance(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[22]
    else:
        return None
    
#get the user's paralysis resistance
async def get_paralysis_resistance(user_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
    if data is not None:
        return data[23]
    else:
        return None

  
#add dodge chance
async def add_dodge_chance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET dodge_chance = dodge_chance + ? WHERE user_id = ?", (amount, user_id))

#remove dodge chance
async def remove_dodge_chance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET dodge_chance = dodge_chance - ? WHERE user_id = ?", (amount, user_id))
    
#add crit chance
async def add_crit_chance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET crit_chance = crit_chance + ? WHERE user_id = ?", (amount, user_id))
    
#remove crit chance
async def remove_crit_chance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET crit_chance = crit_chance - ? WHERE user_id = ?", (amount, user_id))
    
#add damage boost
async def add_damage_boost(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET damage_boost = damage_boost + ? WHERE user_id = ?", (amount, user_id))
    
#remove damage boost
async def remove_damage_boost(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET damage_boost = damage_boost - ? WHERE user_id = ?", (amount, user_id))
    
#add health boost
async def add_health_boost(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET health_boost = health_boost + ? WHERE user_id = ?", (amount, user_id))
    
#remove health boost
async def remove_health_boost(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET health_boost = health_boost - ? WHERE user_id = ?", (amount, user_id))
    
#add fire resistance
async def add_fire_resistance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET fire_resistance = fire_resistance + ? WHERE user_id = ?", (amount, user_id))
    
#remove fire resistance
async def remove_fire_resistance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET fire_resistance = fire_resistance - ? WHERE user_id = ?", (amount, user_id))
    
#add poison resistance
async def add_poison_resistance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET poison_resistance = poison_resistance + ? WHERE user_id = ?", (amount, user_id))
    
#remove poison resistance
async def remove_poison_resistance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET poison_resistance = poison_resistance - ? WHERE user_id = ?", (amount, user_id))
    
#add frost resistance
async def add_frost_resistance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET frost_resistance = frost_resistance + ? WHERE user_id = ?", (amount, user_id))
    
#remove frost resistance
async def remove_frost_resistance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET frost_resistance = frost_resistance - ? WHERE user_id = ?", (amount, user_id))
    
#add paralysis resistance
async def add_paralysis_resistance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET paralysis_resistance = paralysis_resistance + ? WHERE user_id = ?", (amount, user_id))
    
#remove paralysis resistance
async def remove_paralysis_resistance(user_id: int, amount: int) -> None:
    db = DB()
    await db.execute("UPDATE `stats` SET paralysis_resistance = paralysis_resistance - ? WHERE user_id = ?", (amount, user_id))
    
#check if an item has a recipe
async def check_item_recipe(item_id: str) -> bool:
    db = DB()
    data = await db.execute(f"SELECT * FROM `recipes` WHERE item_id = ?", (item_id,), fetch="one")
    if data is not None:
        return True
    else:
        return False
    
#get the items effect from its ID
async def get_basic_item_effect(item_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `basic_items` WHERE item_id = ?", (item_id,), fetch="one")
    if data is not None:
        return data[17]
    else:
        return None
    
#get the projectile of a basic item
async def get_basic_item_projectile(item_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `basic_items` WHERE item_id = ?", (item_id,), fetch="one")
    if data is not None:
        return data[13]
    else:
        return None
    
    
#get streamer item effect from its ID
async def get_streamer_item_effect(item_id: str) -> str:
    db = DB()
    data = await db.execute(f"SELECT * FROM `streamer_items` WHERE item_id = ?", (item_id,), fetch="one")
    if data is not None:
        return data[11]
    else:
        return None
    

#function to display the shop items
async def display_shop_items() -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `shop`", fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#get a list of all items in a specific item_type from the shop table
async def get_all_shop_items_off_one_type(item_type: str) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `shop` WHERE item_type = ?", (item_type,), fetch="all")
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
        
#get a users arrows 
async def get_arrows(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND item_id = 'arrow'", (user_id,), fetch="one")
        if data is not None:
            return data[8]
        else:
            return None
        
#get all the equipped items
async def get_equipped_items(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1", (user_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#get all the equipped items where the item effect has the word luck in it
async def get_equipped_luck_items(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_effect LIKE '%luck%'", (user_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None

        
#get all the equipped items with the item type "Weapon"
async def get_equipped_weapon(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Weapon'", (user_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#get all the equipped items with the item type "Badge"
async def get_equipped_badges(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Badge'", (user_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#get equipped weapon damage
async def get_equipped_weapon_damage(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Weapon'", (user_id,), fetch="all")
        if data is not None:
            return data[8]
        else:
            return None
        
#get equipped weapon name
async def get_equipped_weapon_name(user_id: int) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Weapon'", (user_id,), fetch="all")
        if data is not None:
            return data[3]
        else:
            return None

#get equipped weapon emoji
async def get_equipped_weapon_emoji(user_id: int) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Weapon'", (user_id,), fetch="all")
        if data is not None:
            return data[4]
        else:
            return None
        
#get equipped weapon ID
async def get_equipped_weapon_id(user_id: int) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Weapon'", (user_id,), fetch="all")
        if data is not None:
            return data[2]
        else:
            return None
        
#get equipped weapon crit chance
async def get_equipped_weapon_crit_chance(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Weapon'", (user_id,), fetch="all")
        if data is not None:
            return data[7]
        else:
            return None
        
#get equipped helmet
async def get_equipped_armor_helmet(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Armor' AND item_sub_type = 'Helmet'", (user_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None

#get equipped chestplate
async def get_equipped_armor_chestplate(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Armor' AND item_sub_type = 'Chestplate'", (user_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#get equipped leggings
async def get_equipped_armor_leggings(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Armor' AND item_sub_type = 'Leggings'", (user_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#get equipped boots
async def get_equipped_armor_boots(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Armor' AND item_sub_type = 'Boots'", (user_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#get equipped armor defense
async def get_equipped_armor_defense(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Armor'", (user_id,), fetch="all")
        if data is not None:
            return data[8]
        else:
            return None
        
#get all the equipped items with the item type "Armor" for a user
async def get_equipped_armor(user_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `inventory` WHERE user_id = ? AND isEquipped = 1 AND item_type = 'Armor'", (user_id,), fetch="all")
        if data is not None:
            return data
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
        
#check if the item ID is a chest
async def check_chest(item_id: str) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `chests` WHERE chest_id = ?", (item_id,), fetch="one")
        if data is not None:
            return 1
        else:
            return 0
        
#get the chest icon from the chest ID
async def get_chest_icon(chest_id: str) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `chests` WHERE chest_id = ?", (chest_id,), fetch="one")
        if data is not None:
            return data[2]
        else:
            return None

#get chest name
async def get_chest_name(chest_id: str) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `chests` WHERE chest_id = ?", (chest_id,), fetch="one")
        if data is not None:
            return data[1]
        else:
            return None
        
#get the chests chest_contents list from the chest ID
async def get_chest_contents(chest_id: str) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `chest_contents` WHERE chest_id = ?", (chest_id,), fetch="one")
        if data is not None:
            return data
        else:
            return None
        
#get all structures
async def get_structures() -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `structures`", fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#get the structure outcomes from the structure ID
async def get_structure_outcomes(structure_id: str) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `structure_outcomes` WHERE structure_id = ?", (structure_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#add a structure to the current structures table
async def add_current_structure(server_id: str, structure_id: str) -> None:
        db = DB()
        await db.execute(f"INSERT INTO `current_structures` (server_id, structure_id) VALUES (?, ?)", (server_id, structure_id))
        return None
    
#remove a structure from the current structures table
async def remove_current_structure(server_id: str) -> None:
        db = DB()
        await db.execute(f"DELETE FROM `current_structures` WHERE server_id = ?", (server_id))
        return None
    
#edit a structure in the current structures table
async def edit_current_structure(server_id: str, structure_id: str) -> None:
        db = DB()
        await db.execute(f"UPDATE `current_structures` SET structure_id = ? WHERE server_id = ?", (structure_id, server_id))
        return None
    
#get the current structure from the server ID
async def get_current_structure(server_id: str) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `current_structures` WHERE server_id = ?", (server_id,), fetch="one")
        if data is not None:
            return data
        else:
            return None
        
#add a monster to the current spawn table, first the monster_id and then the server_id
async def add_current_spawn(monster_id: str, server_id: int, monster_health: int) -> None:
        db = DB()
        await db.execute(f"INSERT INTO `spawns` (monster_id, server_id, monster_health) VALUES (?, ?, ?)", (monster_id, server_id, monster_health))
        return None
    
#remove the currently spawned monster's health
async def remove_spawned_monster_health(monster_id: str, server_id: int, damage: int) -> None:
    db = DB()
    data = await db.execute(f"SELECT * FROM `spawns` WHERE server_id = ? AND monster_id = ?", (server_id, monster_id,), fetch="one")
    if data is not None:
        await db.execute(f"UPDATE `spawns` SET `monster_health` = `monster_health` - ? WHERE server_id = ? AND monster_id = ?", (damage, server_id, monster_id))
        
        
#get the currently spawned monster's health
async def get_spawned_monster_health(monster_id: str, server_id: int) -> int:
    db = DB()
    data = await db.execute(f"SELECT * FROM `spawns` WHERE server_id = ? AND monster_id = ?", (server_id, monster_id,), fetch="one")
    if data is not None:
        return data[2]
    else:
        return None

    
#remove a monster from the current spawn table
async def remove_current_spawn(server_id: int) -> None:
        db = DB()
        await db.execute(f"DELETE FROM `spawns` WHERE server_id = ?", (server_id))
        return None
    
#get the current spawn from the server ID
async def get_current_spawn(server_id: int) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `spawns` WHERE server_id = ?", (server_id,), fetch="one")
        if data is not None:
            return data
        else:
            return None
    
#check if a certain monster is in the current spawn table
async def check_current_spawn(monster_id: str, server_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `spawns` WHERE monster_id = ? AND server_id = ?", (monster_id, server_id), fetch="one")
        if data is not None:
            return 1
        else:
            return 0
    
        
#add a user to a servers explorer log
async def add_explorer_log(server_id: str, user_id: int) -> None:
        db = DB()
        await db.execute(f"INSERT INTO `explorer_log` (server_id, user_id) VALUES (?, ?)", (server_id, user_id))
        return None

#remove a user from a servers explorer log
async def remove_explorer_log(server_id: str, user_id: int) -> None:
        db = DB()
        await db.execute(f"DELETE FROM `explorer_log` WHERE server_id = ? AND user_id = ?", (server_id, user_id))
        return None
    
#get the explorer log for a server
async def get_explorer_log(server_id: str) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `explorer_log` WHERE server_id = ?", (server_id,), fetch="all")
        if data is not None:
            return data
        else:
            return None
        
#reset the explorer log for a server
async def reset_explorer_log(server_id: str) -> None:
        db = DB()
        await db.execute(f"DELETE FROM `explorer_log` WHERE server_id = ?", (server_id,))
        return None
    
        
#get structure from structure ID
async def get_structure(structure_id: str) -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `structures` WHERE structure_id = ?", (structure_id,), fetch="one")
        if data is not None:
            return data
        else:
            return None
        
#get structure_name from structure ID
async def get_structure_name(structure_id: str) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `structures` WHERE structure_id = ?", (structure_id,), fetch="one")
        if data is not None:
            return data[1]
        else:
            return None

#get the structure structure_image from the structure ID
async def get_structure_image(structure_id: str) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `structures` WHERE structure_id = ?", (structure_id,), fetch="one")
        if data is not None:
            return data[2]
        else:
            return None
        
#get the structure structure_description from the structure ID
async def get_structure_description(structure_id: str) -> str:
        db = DB()
        data = await db.execute(f"SELECT * FROM `structures` WHERE structure_id = ?", (structure_id,), fetch="one")
        if data is not None:
            return data[3]
        else:
            return None
        
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
        
#set a users isBurning to 1
async def set_user_burning(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `users` SET `isBurning` = 1 WHERE user_id = ?", (user_id,))
            return 1
        else:
            return None
        
#set a users isBurning to 0
async def set_user_not_burning(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `users` SET `isBurning` = 0 WHERE user_id = ?", (user_id,))
            return 1
        else:
            return None

#check if a user is burning
async def check_user_burning(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            if data[4] == 1:
                return 1
            else:
                return None
        else:
            return None
        
#set a users isPoisoned to 1
async def set_user_poisoned(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `users` SET `isPoisoned` = 1 WHERE user_id = ?", (user_id,))
            return 1
        else:
            return None

#set a users isPoisoned to 0
async def set_user_not_poisoned(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `users` SET `isPoisoned` = 0 WHERE user_id = ?", (user_id,))
            return 1
        else:
            return None

#check if a user is poisoned
async def check_user_poisoned(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            if data[5] == 1:
                return 1
            else:
                return None
        else:
            return None
        
#make one for paralyzed
async def set_user_paralyzed(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `users` SET `isParalyzed` = 1 WHERE user_id = ?", (user_id,))
            return 1
        else:
            return None

#set a users isParalyzed to 0
async def set_user_not_paralyzed(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `users` SET `isParalyzed` = 0 WHERE user_id = ?", (user_id,))
            return 1
        else:
            return None
        
#check if a user is paralyzed
async def check_user_paralyzed(user_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `users` WHERE user_id = ?", (user_id,), fetch="one")
        if data is not None:
            if data[7] == 1:
                return 1
            else:
                return None
        else:
            return None
        
#do all of the above for enimies
async def set_enemy_burning(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `enemies` SET `isBurning` = 1 WHERE enemy_id = ?", (enemy_id,))
            return 1
        else:
            return None
        
#get all enemies
async def get_all_enemies() -> list:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies`", fetch="all")
        if data is not None:
            return data
        else:
            return None

async def set_enemy_not_burning(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `enemies` SET `isBurning` = 0 WHERE enemy_id = ?", (enemy_id,))
            return 1
        else:
            return None

async def check_enemy_burning(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            if data[4] == 1:
                return 1
            else:
                return None
        else:
            return None
    
async def set_enemy_poisoned(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `enemies` SET `isPoisoned` = 1 WHERE enemy_id = ?", (enemy_id,))
            return 1
        else:
            return None

async def set_enemy_not_poisoned(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `enemies` SET `isPoisoned` = 0 WHERE enemy_id = ?", (enemy_id,))
            return 1
        else:
            return None
        
async def check_enemy_poisoned(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            if data[5] == 1:
                return 1
            else:
                return None
        else:
            return None

async def set_enemy_paralyzed(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `enemies` SET `isParalyzed` = 1 WHERE enemy_id = ?", (enemy_id,))
            return 1
        else:
            return None

async def set_enemy_not_paralyzed(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            await db.execute(f"UPDATE `enemies` SET `isParalyzed` = 0 WHERE enemy_id = ?", (enemy_id,))
            return 1
        else:
            return None

async def check_enemy_paralyzed(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            if data[6] == 1:
                return 1
            else:
                return None
        else:
            return None
        
#get enemy crit chance
async def get_enemy_crit_chance(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            return data[3]
        else:
            return None
        
#get enemy element
async def get_enemy_element(enemy_id: int) -> int:
        db = DB()
        data = await db.execute(f"SELECT * FROM `enemies` WHERE enemy_id = ?", (enemy_id,), fetch="one")
        if data is not None:
            return data[2]
        else:
            return None

#make a request to the twitch api to get the twitch id of the streamer
async def get_twitch_id(streamer_channel: str) -> int:
    code = await get_twitchCode()

    headers = {
    'Authorization': f'Bearer {code}',
    'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5',
    }
    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    if streamer_channel.startswith("https://www.twitch.tv/"):
        streamer_channel = remove_prefix(streamer_channel, "https://www.twitch.tv/")
    elif streamer_channel.startswith("https://twitch.tv/"):
        streamer_channel = remove_prefix(streamer_channel, "https://twitch.tv/")
    else:
        streamer_channel = streamer_channel
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
    code = await get_twitchCode()

    headers = {
    'Authorization': f'Bearer {code}',
    'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5',
    }
    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    if streamer_channel.startswith("https://www.twitch.tv/"):
        streamer_channel = remove_prefix(streamer_channel, "https://www.twitch.tv/")
    elif streamer_channel.startswith("https://twitch.tv/"):
        streamer_channel = remove_prefix(streamer_channel, "https://twitch.tv/")
    else:
        streamer_channel = streamer_channel

    params = {
        'login': f'{streamer_channel}',
    }

    async with aiohttp.ClientSession() as session:
            async with session.get('https://api.twitch.tv/helix/users', params=params, headers=headers) as request:
                data = await request.json()
                print (data)
                broadcaster_type = data['data'][0]['broadcaster_type']
                print(broadcaster_type)
                return broadcaster_type

#update the isStreamer column in the user table to True
async def update_is_streamer(user_id: int) -> int:
    db = DB()
    await db.execute(f"UPDATE `users` SET `isStreamer` = 1 WHERE user_id = ?", (user_id,))
    return 1

#update the isStreamer column in the user table to False
async def update_is_not_streamer(user_id: int) -> int:
    db = DB()
    await db.execute(f"UPDATE `users` SET `isStreamer` = 0 WHERE user_id = ?", (user_id,))
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
        
#add an item to the streamer_items table, uses the streamersID from the streamer table and the item name
  #`streamer_prefix` varchar(20) NOT NULL,
  #`item_id` varchar(20) NOT NULL,
  #`item_name` varchar NOT NULL,
  #`item_emoji` varchar(255) NOT NULL,
  #`item_rarity` varchar(255) NOT NULL,

async def create_streamer_item(streamerPrefix: str, channel: str, itemName: str, itemEmoji: str) -> int:
    """
    This function will add an item to the streamer_items table.

    :param streamerPrefix: The ID of the streamer that the item should be added to.
    :param itemName: The name of the item that should be added.
    :param itemEmoji: The emoji of the item that should be added.
    :param itemRarity: The rarity of the item that should be added.
    """
    #create an item_id for the item that is being added by combining the streamerPrefix and the itemName
    item_id = str(streamerPrefix) + "_" + itemName
    #convert all spaces in the item name to underscores
    item_id = item_id.replace(" ", "_")
    #rarity = Streamer
    itemRarity = "Streamer"
    async with aiosqlite.connect("database/database.db") as db:
        #add the item to the database
        await db.execute("INSERT INTO `streamer_items` (streamer_prefix, channel, item_id, item_name, item_emoji, item_rarity) VALUES (?, ?, ?, ?, ?, ?)", (streamerPrefix, channel, item_id, itemName, itemEmoji, itemRarity))
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
        
#get all the streamer items owned by a user from the streamer_item_inventory table
  #`user_id` int(11) NOT NULL,
  #`channel` varchar(255) NOT NULL,
  #`streamer_item_id` varchar(255) NOT NULL,
  #`streamer_item_name` varchar(255) NOT NULL,
  #`streamer_item_emoji` varchar(255) NOT NULL,
  #`streamer_item_rarity` varchar(255) NOT NULL

async def view_streamer_item_inventory(user_id: int) -> list:
    """
    This function will view all streamer items owned by a user in the database.

    :return: A list of all streamer items in the database owned by a user.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_item_inventory WHERE user_id=?", (user_id,)) as cursor:
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
        
#view all the basic items that have "IsMineable" set to true
async def view_mineable_items() -> list:
    """
    This function will view all mineable basic items in the database.

    :return: A list of all mineable basic items in the database.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE isMineable = 1") as cursor:
            result = await cursor.fetchall()
            return result if result is not None else []
    
#view all the basic items that have "IsHuntable" set to true
async def view_huntable_items() -> list:
    """
    This function will view all huntable basic items in the database.

    :return: A list of all huntable basic items in the database.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE isHuntable = 1") as cursor:
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
        await db.execute("INSERT INTO users (user_id, money, health, isStreamer, isBurning, isPoisoned, isFrozen, isParalyzed, isBleeding, isDead, isInCombat, player_xp, player_level, quest_id, twitch_id, twitch_name, dodge_chance, crit_chance, damage_boost, health_boost, fire_resistance, poison_resistance, frost_resistance, paralysis_resistance, luck) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, 0, 100, isStreamer, False, False, False, False, False, False, False, 0, 1, "None", "None", "None", 0, 0, 0, 0, 0, 0, 0, 0, 0))
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
async def add_item_to_inventory(user_id: int, item_id: str, item_amount: int) -> int:
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
                #check if the item is a streamer item
                isStreamerItem = await check_streamer_item(item_id)
                print(isStreamerItem)
                isBasicItem = await check_basic_item(item_id)
                print(isBasicItem)
                isChest = await check_chest(item_id)
                print(isChest)
                #add the item to the inventory table
                if isBasicItem == 1:
                    async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
                        result = await cursor.fetchone()
                        if result is not None:
                            item_id = result[0]
                            item_name = result[1]
                            item_price = result[2]
                            item_emoji = result[3]
                            item_rarity = result[4]
                            item_type = result[5]
                            item_damage = result[6]
                            isUsable = result[7]
                            inShop = result[8]
                            isEquippable = result[9]
                            item_description = result[10]
                            item_element = result[11]
                            item_crit_chance = result[12]
                            item_projectile = result[13]
                            isEquipped = 0
                            #add the item to the inventory table
                            await db.execute("INSERT INTO inventory(user_id, item_id, item_name, item_price, item_emoji, item_rarity, item_amount, item_type, item_damage, isEquipped, item_element, item_crit_chance, item_projectile) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, item_id, item_name, item_price, item_emoji, item_rarity, item_amount, item_type, item_damage, isEquipped, item_element, item_crit_chance, item_projectile))
                            await db.commit()
                            return 1
                        else:
                            return 0
                #get all the data above from the basic items table by the items ID
                #get data from the chest table by the chest id
                if isChest == 1:
                    async with db.execute("SELECT * FROM chests WHERE chest_id=?", (item_id,)) as cursor:
                        result = await cursor.fetchone()
                        if result is not None:
                            #   chest_id int(11) NOT NULL,
                            #   chest_name varchar(255) NOT NULL,
                            #   chest_price varchar(255) NOT NULL,
                            #   chest_emoji varchar(255) NOT NULL,
                            #   chest_rarity varchar(255) NOT NULL,
                            #   chest_type varchar(255) NOT NULL,
                            #   chest_description varchar(255) NOT NULL,
                            #   key_id varchar(255) NOT NULL,
                            #   chest_contentsID varchar(255) NOT NULL,
                            
                            #get the data from the chest table
                            chest_id = result[0]
                            chest_name = result[1]
                            chest_price = result[2]
                            chest_emoji = result[3]
                            chest_rarity = result[4]
                            chest_type = result[5]
                            chest_description = result[6]
                            key_id = result[7]
                            chest_contentsID = result[8]
                            #add the chest to the inventory table, setting the values that are not in the chest table to 0
                            await db.execute("INSERT INTO inventory(user_id, item_id, item_name, item_price, item_emoji, item_rarity, item_amount, item_type, item_damage, isEquipped, item_element, item_crit_chance, item_projectile) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, chest_id, chest_name, chest_price, chest_emoji, chest_rarity, item_amount, chest_type, 0, 0, "None", 0, "None"))
                            await db.commit()
                            return 1
                        else:
                            return 0
                await db.commit()
                rows = await db.execute("SELECT COUNT(*) FROM inventory")
                async with rows as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result is not None else 0
                
#add a streamer item to the streamer_item_inventory table, if the the user already has the item, give them 5000 coins instead
  #`user_id` int(11) NOT NULL,
  #`channel` varchar(255) NOT NULL
  #`streamer_item_id` varchar(255) NOT NULL,
  #`streamer_item_name` varchar(255) NOT NULL,
  #`streamer_item_emoji` varchar(255) NOT NULL, 
  #`streamer_item_rarity` varchar(255) NOT NULL
  
async def add_streamer_item_to_user(user_id: int, streamer_item_id: str) -> int:
    """
    This function will add a streamer item to the streamer_item_inventory table.

    :param user_id: The ID of the user that the item should be added to.
    :param channel: The channel that the item should be added to.
    :param streamer_item_id: The ID of the item that should be added.
    :param streamer_item_name: The name of the item that should be added.
    :param streamer_item_emoji: The emoji of the item that should be added.
    :param streamer_item_rarity: The rarity of the item that should be added.
    """
    async with aiosqlite.connect("database/database.db") as db:
        #check if the item already exists in the streamer_item_inventory table
        async with db.execute("SELECT * FROM streamer_item_inventory WHERE user_id=? AND streamer_item_id=?", (user_id, streamer_item_id)) as cursor:
            result = await cursor.fetchone()
            if result is not None:
                #give the user 5000 coins
                await add_money(user_id, 5000)
                return 0
            else:
                #streamer item id is just the prefix + the item name
                channel = await get_streamer_channel_from_user_id(user_id)
                #get the streamer prefix from the streamer table
                prefix = await get_streamerPrefix_with_user_id(user_id)
                #get the streamer item name from the streamer items table
                streamer_item_name = await get_streamer_item_name(streamer_item_id)
                #get the streamer item emoji from the streamer items table
                streamer_item_emoji = await get_streamer_item_emote(streamer_item_id)
                #add the item to the streamer_item_inventory table
                await db.execute("INSERT INTO streamer_item_inventory(user_id, channel, streamer_item_id, streamer_item_name, streamer_item_emoji, streamer_item_rarity) VALUES (?, ?, ?, ?, ?, ?)", (user_id, channel, streamer_item_id, streamer_item_name, streamer_item_emoji, "Streamer"))
                await db.commit()
                return 1
  

#remove an item from the inventory table, uses the usersID from the users table and the item ID from the streamer_items table, if the item already exists in the inventory table, it will remove 1 from the item_amount
async def remove_item_from_inventory(user_id: int, item_id: str, amount: int) -> int:
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
                await db.execute("UPDATE inventory SET item_amount = item_amount - ? WHERE user_id=? AND item_id=?", (amount, user_id, item_id))
                await db.commit()
                #if the item_amount is 0, remove the item from the inventory table
                async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_id=?", (user_id, item_id)) as cursor:
                    result = await cursor.fetchone()
                    if result[6] <= 0:
                        await db.execute("DELETE FROM inventory WHERE user_id=? AND item_id=?", (user_id, item_id))
                        await db.commit()
                        return 1
                    else:
                        return 1
                return 1
            else:
                #if the item does not exist in the inventory table, return 0
                return 0
            
#get the amount of an item from a users inventory
async def get_item_amount_from_inventory(user_id: int, item_id: str) -> int:
    """
    This function will get the amount of an item from a users inventory.

    :param user_id: The ID of the user that the item should be gotten from.
    :param item_id: The ID of the item that should be gotten.
    """
    async with aiosqlite.connect("database/database.db") as db:
        #check if the item already exists in the inventory table
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_id=?", (user_id, item_id)) as cursor:
            result = await cursor.fetchone()
            if result is not None:
                #if the item already exists in the inventory table, return the item_amount
                return result[6]
            else:
                #if the item does not exist in the inventory table, return 0
                return 0
            
#get streamer channel from user id
async def get_streamer_channel_from_user_id(user_id: int) -> str:
    """
    This function will get the streamer channel from the streamer table.

    :param user_id: The ID of the user that the streamer channel should be gotten from.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0
            
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
        
#get streamer item sub type via its id
async def get_streamer_item_element(item_id: str) -> str:
    """
    This function will get the sub type of an item.

    :param item_id: The ID of the item that the sub type should be gotten from.
    :return: The sub type of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[9] if result is not None else 0
        
#get streamer item crit chance via its id
async def get_streamer_item_crit_chance(item_id: str) -> str:
    """
    This function will get the crit chance of an item.

    :param item_id: The ID of the item that the crit chance should be gotten from.
    :return: The crit chance of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[10] if result is not None else 0
        
#get streamer item damage via its id
async def get_streamer_item_damage(item_id: str) -> int:
    """
    This function will get the damage of an item.

    :param item_id: The ID of the item that the damage should be gotten from.
    :return: The damage of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[8] if result is not None else 0
        
#get if a streamer item is usable via its id
async def get_streamer_item_usable(item_id: str) -> bool:
    """
    This function will get if an item is usable.

    :param item_id: The ID of the item that the usable should be gotten from.
    :return: If the item is usable.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[12] if result is not None else False
        
#get if a streamer item is equipable via its id
async def get_streamer_item_equipable(item_id: str) -> bool:
    """
    This function will get if an item is equipable.

    :param item_id: The ID of the item that the equipable should be gotten from.
    :return: If the item is equipable.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM streamer_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[13] if result is not None else False
        
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
        
#get basic item sub type via its id
async def get_basic_item_element(item_id: str) -> str:
    """
    This function will get the sub type of an item.

    :param item_id: The ID of the item that the sub type should be gotten from.
    :return: The sub type of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[11] if result is not None else 0
        
#get basic items crit chance via its id
async def get_basic_item_crit_chance(item_id: str) -> str:
    """
    This function will get the crit chance of an item.

    :param item_id: The ID of the item that the crit chance should be gotten from.
    :return: The crit chance of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[12] if result is not None else 0
        
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
        
#get if a basic item is huntable via its id
async def get_basic_item_huntable(item_id: str) -> bool:
    """
    This function will get if a basic item is huntable.

    :param item_id: The ID of the item that should be checked.
    :return: True if the item is huntable, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[15] if result is not None else 0
        
#get an items hunt chance via its id
async def get_basic_item_hunt_chance(item_id: str) -> int:
    """
    This function will get the hunt chance of an item.

    :param item_id: The ID of the item that the hunt chance should be gotten from.
    :return: The hunt chance of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[16] if result is not None else 0
        
#get if a basic item is mineable via its id
async def get_basic_item_mineable(item_id: str) -> bool:
    """
    This function will get if a basic item is mineable.

    :param item_id: The ID of the item that should be checked.
    :return: True if the item is mineable, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[18] if result is not None else 0
        
#get an items mine chance via its id
async def get_basic_item_mine_chance(item_id: str) -> int:
    """
    This function will get the mine chance of an item.

    :param item_id: The ID of the item that the mine chance should be gotten from.
    :return: The mine chance of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[19] if result is not None else 0
        
#check if a basic item is usable
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
        
#get an items recipe by getting all the entries with the same item_id
async def get_item_recipe(item_id: str) -> list:
    """
    This function will get the recipe of an item.

    :param item_id: The ID of the item that the recipe should be gotten from.
    :return: The recipe of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM recipes WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchall()
            return result if result is not None else 0
        
#check the inventory of a user for any items with the item_type Armor and if they are equiped with the item_type Armor
async def is_armor_equipped(user_id: int) -> int:
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
async def is_weapon_equipped(user_id: int) -> int:
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
async def is_accessory_equipped(user_id: int) -> int:
    """
    This function will check if a user has an accessory equiped.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user has an accessory equiped, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_type=? AND isEquipped=?", (user_id, "Accessory", 1)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0
        
#check if an item sub_type is equiped
async def is_item_sub_type_equipped(user_id: int, item_sub_type: str) -> int:
    """
    This function will check if an item sub_type is equiped.

    :param user_id: The ID of the user that should be checked.
    :param item_sub_type: The sub_type of the item that should be checked.
    :return: True if the item sub_type is equiped, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_sub_type=? AND isEquipped=?", (user_id, item_sub_type, 1)) as cursor:
            result = await cursor.fetchone()
            return result[1] if result is not None else 0
        
#get basic item sub_type
async def get_basic_item_sub_type(item_id: str) -> str:
    """
    This function will get the sub_type of a basic item.

    :param item_id: The ID of the item that the sub_type should be gotten from.
    :return: The sub_type of the item.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM basic_items WHERE item_id=?", (item_id,)) as cursor:
            result = await cursor.fetchone()
            return result[21] if result is not None else 0

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
        
#check if an item is in the inventory table, if it is return 1, if not return 0
async def is_item_in_inventory(user_id: int, item_id: str) -> int:
    """
    This function will check if an item is in the inventory.

    :param user_id: The ID of the user that should be checked.
    :param item_id: The ID of the item that should be checked.
    :return: True if the item is in the inventory, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM inventory WHERE user_id=? AND item_id=?", (user_id, item_id)) as cursor:
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
        
        
#edit twitch creds
async def edit_twitchCreds(code: str) -> None:
    """
    This function will edit the twitch app code.

    :param code: The new code of the twitch app.
    """
    db = DB()
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("UPDATE twitch_creds SET code=?", (code,))
        await db.commit()
        
#get the code from the twitch table
async def get_twitchCode() -> str:
    """
    This function will get the twitch app code.

    :return: The twitch app code.
    """
    db = DB()
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM twitch_creds") as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0