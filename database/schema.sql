CREATE TABLE IF NOT EXISTS `blacklist` (
  `user_id` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `api_keys` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` varchar(20) NOT NULL,  -- Assuming you have a users table and want to link the API key to a specific user
    `api_key` VARCHAR(255) NOT NULL UNIQUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `last_used` TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS `streamer` (
  `streamer_prefix` varchar NOT NULL,
  `streamer_channel` varchar NOT NULL,
  `user_id` varchar NOT NULL,
  `twitch_id` varchar NOT NULL,
  `broadcaster_type` varchar NOT NULL,
  `discord_channel_id_live_announce` varchar,
  `discord_guild_id` varchar,
  `discord_channel_id_chat` varchar,
  `enable_live_chat` boolean,
  `discord_role_id_live_announce` varchar,
  `discord_announce_message` varchar
);

CREATE TABLE IF NOT EXISTS `streamer_mods` (
  `streamer_id` varchar NOT NULL,
  `streamer_channel` varchar NOT NULL,
  `mod_user_id` varchar NOT NULL,
  `twitch_id` varchar(255),
  `twitch_name` varchar(255),
  FOREIGN KEY (`streamer_id`) REFERENCES `streamer`(`user_id`)
);

CREATE TABLE IF NOT EXISTS `giveaways` (
  `giveaway_id` INT AUTO_INCREMENT PRIMARY KEY,
  `streamer_id` varchar(255) NOT NULL, -- the ID of the streamer who started the giveaway
  `prize` varchar(255) NOT NULL, -- the prize for the giveaway
  `start_time` DATETIME NOT NULL, -- the time when the giveaway started
  `end_time` DATETIME NOT NULL, -- the time when the giveaway should end
  `winner_id` varchar(255), -- the ID of the user who won the giveaway (NULL if the giveaway is still ongoing)
  FOREIGN KEY (`streamer_id`) REFERENCES `streamer`(`user_id`) -- assuming the streamers user_id is stored in the `streamer` table
);

CREATE TABLE IF NOT EXISTS `giveaway_entries` (
  `giveaway_id` INT NOT NULL,
  `user_id` varchar(255) NOT NULL,
  PRIMARY KEY (`giveaway_id`, `user_id`),
  FOREIGN KEY (`giveaway_id`) REFERENCES `giveaways`(`giveaway_id`)
);

CREATE TABLE IF NOT EXISTS `starboard` (
  `starboard_id` INT AUTO_INCREMENT PRIMARY KEY,
  `server_id` BIGINT NOT NULL,               -- The ID of the guild (server)
  `starboard_channel_id` BIGINT NOT NULL,   -- The ID of the channel where starred messages will be posted
  `star_threshold` INT DEFAULT 5,           -- The number of star reactions required for a message to be posted to the starboard
  `star_emoji` VARCHAR(255) DEFAULT '⭐',    -- The custom emoji ID or the default star emoji
  `is_enabled` BOOLEAN DEFAULT TRUE         -- Whether the starboard is enabled or not
);

CREATE TABLE IF NOT EXISTS `starred_messages` (
    `message_id` BIGINT PRIMARY KEY,
    `guild_id` BIGINT NOT NULL,
    `channel_id` BIGINT NOT NULL,
    `author_id` BIGINT NOT NULL,
    `star_count` INT DEFAULT 0,
    `starboard_entry_id` BIGINT,
    `message_link` TEXT,
    `message_content` TEXT,
    `attachment_url` TEXT
);

CREATE TABLE IF NOT EXISTS `paginated_embeds` (
    `starboard_message_id` BIGINT PRIMARY KEY,   -- The ID of the message in the starboard channel
    `current_index` INT NOT NULL,                -- The current index of the attachment being displayed
    `total_attachments` INT NOT NULL             -- Total number of attachments in the original message
);

CREATE TABLE IF NOT EXISTS `streamer_items` (
  `streamer_prefix` varchar(20) NOT NULL,
  `channel` varchar(20) NOT NULL,
  `item_id` varchar(20) NOT NULL,
  `item_name` varchar NOT NULL,
  `item_emoji` varchar(255) NOT NULL,
  `item_rarity` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `basic_items` (
  `item_id` varchar(255) PRIMARY KEY,
  `item_name` varchar(255) NOT NULL,
  `item_price` varchar(255) NOT NULL,
  `item_emoji` varchar(255) NOT NULL,
  `item_rarity` varchar(255) NOT NULL,
  `item_type` varchar(255) NOT NULL,
  `item_damage` int(11),
  `isUsable` boolean NOT NULL,
  `inShop` boolean NOT NULL,
  `isEquippable` boolean NOT NULL,
  `item_description` varchar(255) NOT NULL,
  `item_element` varchar(255),
  `item_crit_chance` int(11),
  `item_projectile` TEXT,  -- Added comma
  `recipe_id` varchar(255),
  `isHuntable` boolean,
  `item_hunt_chance` int(11),
  `isMineable` boolean,
  `item_mine_chance` int(11),
  `isFishable` boolean,
  `item_fish_chance` int(11),
  `item_effect` varchar(255),
  `quote_id` varchar(255),
  `item_sub_type` varchar(255),
  FOREIGN KEY (recipe_id) REFERENCES recipes(item_id),
  FOREIGN KEY (quote_id) REFERENCES item_quotes(item_id)
);

CREATE TABLE IF NOT EXISTS `inventory` (
  `user_id` varchar(20) NOT NULL,
  `item_id` varchar(255) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `item_price` varchar(255) NOT NULL,
  `item_emoji` varchar(255) NOT NULL,
  `item_rarity` varchar(255) NOT NULL,
  `item_amount` int(11) NOT NULL,
  `item_type` varchar(255) NOT NULL,
  `item_damage` int(11),
  `isEquipped` boolean NOT NULL,
  `item_element` varchar(255),
  `item_crit_chance` int(11),
  `item_projectile` TEXT,  -- Added comma
  `item_sub_type` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `item_quotes` (
  `item_id` varchar(255) NOT NULL,
  `quote` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `chests` (
  chest_id int(11) NOT NULL,
  chest_name varchar(255) NOT NULL,
  chest_price varchar(255) NOT NULL,
  chest_emoji varchar(255) NOT NULL,
  chest_rarity varchar(255) NOT NULL,
  chest_type varchar(255) NOT NULL,
  chest_description varchar(255) NOT NULL,
  key_id varchar(255) NOT NULL,
  chest_contentsID varchar(255) NOT NULL,
  FOREIGN KEY (key_id) REFERENCES basic_items(item_id)
  FOREIGN KEY (chest_contentsID) REFERENCES chest_contents(chest_id)
);

CREATE TABLE IF NOT EXISTS `chest_contents` (
  `chest_id` varchar(255) NOT NULL,
  `item_id` varchar(255) NOT NULL,
  `item_amount` int(11) NOT NULL,
  `drop_chance` int(11) NOT NULL
);

CREATE TABLE IF NOT EXISTS `structures` (
  `structure_id` varchar(255) NOT NULL,
  `structure_name` varchar(255) NOT NULL,
  `structure_image` varchar(255) NOT NULL,
  `structure_description` varchar(255) NOT NULL,
  `structure_outcomesID` varchar(255) NOT NULL,
  FOREIGN KEY (structure_outcomesID) REFERENCES structure_outcomes(structure_id)
);

CREATE TABLE IF NOT EXISTS `structure_outcomes`(
  `structure_id` varchar(255) NOT NULL,
  `structure_quote` varchar(255) NOT NULL,
  `structure_state` varchar(255) NOT NULL,
  `outcome_chance` int(11) NOT NULL,
  `outcome_type` varchar(255) NOT NULL,
  `outcome` varchar(255) NOT NULL,
  `outcome_amount` varchar(11) NOT NULL,
  `outcome_money` varchar(11) NOT NULL,
  `outcome_xp` varchar(11) NOT NULL,
  FOREIGN KEY (outcome) REFERENCES basic_items(item_id)
  FOREIGN KEY (outcome) REFERENCES chests(chest_id)
  FOREIGN KEY (outcome) REFERENCES enemies(enemy_id)
);

CREATE TABLE IF NOT EXISTS `current_structures`(
  `server_id` varchar(255) NOT NULL,
  `structure_id` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `spawns`(
  `monster_id` varchar(255) NOT NULL,
  `server_id` int(11) NOT NULL,
  `monster_health` int(11) NOT NULL,
  `first_damage_dealer` varchar(255),
  `second_damage_dealer` varchar(255),
  `third_damage_dealer` varchar(255),
  `first_damage` int(11),
  `second_damage` int(11),
  `third_damage` int(11),
  `first_damage_dealer_name` varchar(255),
  `second_damage_dealer_name` varchar(255),
  `third_damage_dealer_name` varchar(255)
);

CREATE TABLE IF NOT EXISTS `twitch_creds` (
  `code` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `explorer_log` (
  `user_id` int(11) NOT NULL,
  `server_id` int(11) NOT NULL
);

CREATE TABLE IF NOT EXISTS recipes (
  `item_id` VARCHAR(255) NOT NULL,
  `ingredient_id` VARCHAR(255) NOT NULL,
  `ingredient_amount` INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS `shop` (
  `item_id` varchar(255) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `item_price` varchar(255) NOT NULL,
  `item_emoji` varchar(255) NOT NULL,
  `item_rarity` varchar(255) NOT NULL,
  `item_type` varchar(255) NOT NULL,
  `item_damage` int(11) NOT NULL,
  `isUsable` boolean NOT NULL,
  `isEquippable` boolean NOT NULL,
  `item_amount` int(11) NOT NULL
);

CREATE TABLE IF NOT EXISTS `users` (
  `user_id` varchar(20) NOT NULL,
  `username` varchar(255) NOT NULL,
  `money` int(11) NOT NULL,
  `health` int(11) NOT NULL,
  `isStreamer` boolean NOT NULL,
  `isBurning` boolean NOT NULL,
  `isPoisoned` boolean NOT NULL,
  `isFrozen` boolean NOT NULL,
  `isParalyzed` boolean NOT NULL,
  `isBleeding` boolean NOT NULL,
  `isDead` boolean NOT NULL,
  `isInCombat` boolean NOT NULL,
  `player_xp` int(11) NOT NULL,
  `player_level` int(11) NOT NULL,
  `quest_id` varchar(255) NOT NULL,
  `twitch_id` varchar(255) NOT NULL,
  `twitch_name` varchar(255) NOT NULL,
  `dodge_chance` int(11) NOT NULL,
  `crit_chance` int(11) NOT NULL,
  `damage_boost` int(11) NOT NULL,
  `health_boost` int(11) NOT NULL,
  `fire_resistance` int(11) NOT NULL,
  `poison_resistance` int(11) NOT NULL,
  `frost_resistance` int(11) NOT NULL,
  `paralysis_resistance` int(11) NOT NULL,
  `luck` int(11) NOT NULL,
  `player_title` varchar(255) NOT NULL,
  `job_id` TEXT,
  `job_level` INTEGER,
  `job_xp` INTEGER,
  `shifts_worked` varchar(255),
  `last_worked` DATETIME,
  `last_daily` DATETIME,
  `last_weekly` DATETIME,
  `rob_locked` boolean NOT NULL,
  `percent_bonus` varchar(255),
  `streak` int(11),
  `time_of_death` DATETIME,
  `time_of_revival` DATETIME,
  `twitch_oauth_token` varchar(255),
  `twitch_refresh_token` varchar(255)
);

CREATE TABLE IF NOT EXISTS `bank`(
  `user_id` varchar(20) NOT NULL,
  `bank_balance` int(11) NOT NULL,
  `bank_capacity` int(11) NOT NULL
);

CREATE TABLE IF NOT EXISTS `stats`(
  `user_id` int(11) NOT NULL,
  `money_earned` int(11) NOT NULL,
  `money_spent` int(11) NOT NULL,
  `items_bought` int(11) NOT NULL,
  `items_sold` int(11) NOT NULL,
  `items_used` int(11) NOT NULL,
  `items_equipped` int(11) NOT NULL,
  `quests_completed` int(11) NOT NULL,
  `enemies_killed` int(11) NOT NULL,
  `users_killed` int(11) NOT NULL,
  `battles_fought` int(11) NOT NULL,
  `battles_won` int(11) NOT NULL,
  `streamer_items_collected` int(11) NOT NULL
);

CREATE TABLE IF NOT EXISTS `questProgress` (
  `user_id` varchar(20) NOT NULL,
  `quest_id` varchar(20) NOT NULL,
  `quest_progress` int(11) NOT NULL,
  `quest_completed` boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS `quests` (
  `quest_id` varchar(20) NOT NULL,
  `quest_name` varchar(255) NOT NULL,
  `quest_description` varchar(255) NOT NULL,
  `quest_xp_reward` int(11) NOT NULL,
  `quest_reward_type` varchar(255) NOT NULL,
  `quest_reward` varchar(255) NOT NULL,
  `quest_reward_amount` int(11) NOT NULL,
  `quest_level_required` int(11) NOT NULL,
  `quest_type` varchar(255) NOT NULL,
  `quest` varchar(255) NOT NULL,
  `onBoard` boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS `questBoard` (
  `quest_id` varchar(20) NOT NULL,
  `quest_name` varchar(255) NOT NULL,
  `quest_description` varchar(255) NOT NULL,
  `quest_xp_reward` int(11) NOT NULL,
  `quest_reward` varchar(255) NOT NULL,
  `quest_reward_amount` int(11) NOT NULL,
  `quest_level_required` int(11) NOT NULL,
  `quest_type` varchar(255) NOT NULL,
  `quest` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `enemies` (
  `enemy_id` varchar(20) NOT NULL,
  `enemy_name` varchar(255) NOT NULL,
  `enemy_health` int(11) NOT NULL,
  `enemy_damage` int(11) NOT NULL,
  `enemy_emoji` varchar(255) NOT NULL,
  `enemy_description` varchar(255) NOT NULL,
  `enemy_rarity` varchar(255) NOT NULL,
  `enemy_type` varchar(255) NOT NULL,
  `enemy_xp` int(11) NOT NULL,
  `enemy_money` int(11) NOT NULL,
  `enemy_crit_chance` int(11) NOT NULL,
  `enemy_drop_id` varchar(255) NOT NULL,
  `enemy_element` varchar(255) NOT NULL,
  `isFrozen` boolean NOT NULL,
  `isBurning` boolean NOT NULL,
  `isPoisoned` boolean NOT NULL,
  `isParalyzed` boolean NOT NULL,
  `quote_id` varchar(255) NOT NULL,
  FOREIGN KEY (quote_id) REFERENCES enemy_quotes(enemy_id)
  FOREIGN KEY (enemy_drop_id) REFERENCES enemy_drops(enemy_id)
);

CREATE TABLE IF NOT EXISTS `enemy_quotes` (
  `enemy_id` varchar(20) NOT NULL,
  `quote` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `enemy_drops` (
  `enemy_id` varchar(20) NOT NULL,
  `item_id` varchar(20) NOT NULL,
  `item_amount` int(11) NOT NULL,
  `item_drop_chance` int(11) NOT NULL
);

CREATE TABLE IF NOT EXISTS `leaderboard` (
    `category` VARCHAR(255) NOT NULL,  -- The category of the leaderboard (e.g., 'highest_level', 'most_money')
    `user_id` VARCHAR(20) NOT NULL,    -- The ID of the user
    `username` VARCHAR(255) NOT NULL,  -- The username of the user
    `value` INT NOT NULL,              -- The value for the leaderboard category (e.g., level or money)
    `rank` INT NOT NULL,               -- The rank of the user in the leaderboard
    PRIMARY KEY (`category`, `rank`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
);

CREATE TABLE IF NOT EXISTS `streamer_item_inventory` (
  `user_id` int(11) NOT NULL,
  `channel` varchar(255) NOT NULL,
  `streamer_item_id` varchar(255) NOT NULL,
  `streamer_item_name` varchar(255) NOT NULL,
  `streamer_item_emoji` varchar(255) NOT NULL,
  `streamer_item_rarity` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `pet_attributes` (
  `item_id` varchar(255) NOT NULL, -- pet ID, same as item_id in inventory when item_type is 'Pet'
  `user_id` varchar(20) NOT NULL, -- the user that owns the pet
  `pet_name` varchar(255) NOT NULL, -- the name of the pet
  `level` int(11) NOT NULL, -- the level of the pet
  `xp` int(11) NOT NULL, -- the experience of the pet
  `hunger_percent` decimal(3,2) NOT NULL, -- hunger level of the pet in percentage
  `cleanliness_percent` decimal(3,2) NOT NULL, -- cleanliness level of the pet in percentage
  `happiness_percent` decimal(3,2) NOT NULL, -- happiness level of the pet in percentage
  `death_time` DATETIME, -- death time of the pet
  `revival_time` DATETIME, -- revival time of the pet
  PRIMARY KEY (`item_id`, `user_id`),
  FOREIGN KEY (`item_id`, `user_id`) REFERENCES inventory(`item_id`, `user_id`)
);

CREATE TABLE IF NOT EXISTS `pet_items` (
  `item_id` varchar(255) NOT NULL, -- pet item ID
  `pet_id` varchar(255) NOT NULL, -- the pet that owns the item, same as item_id in pet_attributes
  `user_id` varchar(20) NOT NULL, -- the user that owns the pet item
  PRIMARY KEY (`item_id`, `pet_id`, `user_id`),
  FOREIGN KEY (`pet_id`, `user_id`) REFERENCES pet_attributes(`item_id`, `user_id`)
);

CREATE TABLE IF NOT EXISTS `timed_items` (
  `item_id` varchar(255) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `activated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` timestamp NOT NULL,
  `effect` varchar(255) NOT NULL,
  FOREIGN KEY (`item_id`, `user_id`) REFERENCES inventory(`item_id`, `user_id`)
);

CREATE TABLE IF NOT EXISTS `jobs` (
    `id` TEXT PRIMARY KEY,
    `name` TEXT,
    `description` TEXT,
    `job_icon` TEXT,
    `required_shifts` INTEGER,
    `base_pay` INTEGER,
    `pay_per_level` INTEGER,
    `cooldown` INTEGER,
    `cooldown_reduction_per_level` INTEGER
);

CREATE TABLE IF NOT EXISTS `minigames` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `job_id` TEXT,
    `type` TEXT,
    `prompt` TEXT,
    FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`)
);

CREATE TABLE IF NOT EXISTS `rewards` (
    `minigame_id` INTEGER,
    `reward_type` TEXT,
    `reward` TEXT,
    `chance` REAL,
    FOREIGN KEY (`minigame_id`) REFERENCES `minigames`(`id`)
);

CREATE TABLE IF NOT EXISTS `trivia` (
    `minigame_id` INTEGER,
    `question` TEXT,
    `options` TEXT,
    `answer` TEXT,
    FOREIGN KEY (`minigame_id`) REFERENCES `minigames`(`id`)
);

CREATE TABLE IF NOT EXISTS `order_game` (
    `minigame_id` INTEGER,
    `task` TEXT,
    `items` TEXT,
    `correct_order` TEXT,
    FOREIGN KEY (`minigame_id`) REFERENCES `minigames`(`id`)
);

CREATE TABLE IF NOT EXISTS `matching` (
    `minigame_id` INTEGER,
    `items` TEXT,
    `correct_matches` TEXT,
    FOREIGN KEY (`minigame_id`) REFERENCES `minigames`(`id`)
);

CREATE TABLE IF NOT EXISTS `retype` (
    `minigame_id` INTEGER,
    `phrase` TEXT,
    FOREIGN KEY (`minigame_id`) REFERENCES `minigames`(`id`)
);

CREATE TABLE IF NOT EXISTS `backwards` (
    `minigame_id` INTEGER,
    `word` TEXT,
    FOREIGN KEY (`minigame_id`) REFERENCES `minigames`(`id`)
);

CREATE TABLE IF NOT EXISTS `hangman` (
    `minigame_id` INTEGER,
    `sentence` TEXT,
    `answer` TEXT,
    FOREIGN KEY (`minigame_id`) REFERENCES `minigames`(`id`)
);

CREATE TABLE IF NOT EXISTS `anagram` (
    `minigame_id` INTEGER,
    `scrambled_word` TEXT,
    `solution` TEXT,
    FOREIGN KEY (`minigame_id`) REFERENCES `minigames`(`id`)
);

CREATE TABLE IF NOT EXISTS `jobboard` (
    `id` TEXT PRIMARY KEY,
    `name` TEXT NOT NULL,
    `job_icon` TEXT NOT NULL
);
