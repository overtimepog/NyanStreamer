CREATE TABLE IF NOT EXISTS `blacklist` (
  `user_id` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `streamer` (
  `streamer_prefix` varchar NOT NULL,
  `streamer_channel` varchar NOT NULL,
  `user_id` varchar NOT NULL,
  `twitch_id` varchar NOT NULL,
  `broadcaster_type` varchar NOT NULL
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
  `item_damage` int(11) NOT NULL,
  `isUsable` boolean NOT NULL,
  `inShop` boolean NOT NULL,
  `isEquippable` boolean NOT NULL,
  `item_description` varchar(255) NOT NULL,
  `item_element` varchar(255) NOT NULL,
  `item_crit_chance` int(11) NOT NULL,
  `item_projectile` varchar(255),
  `recipe_id` varchar(255),
  `isHuntable` boolean,
  `item_hunt_chance` int(11),
  `item_effect` varchar(255) NOT NULL,
  `isMineable` boolean,
  `item_mine_chance` int(11),
  `quote_id` varchar(255),
  `item_sub_type` varchar(255) NOT NULL,
  FOREIGN KEY (recipe_id) REFERENCES recipes(item_id)
  FOREIGN KEY (quote_id) REFERENCES item_quotes(item_id)
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
  `luck` int(11) NOT NULL
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

CREATE TABLE IF NOT EXISTS `inventory` (
  `user_id` varchar(20) NOT NULL,
  `item_id` varchar(255) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `item_price` varchar(255) NOT NULL,
  `item_emoji` varchar(255) NOT NULL,
  `item_rarity` varchar(255) NOT NULL,
  `item_amount` int(11) NOT NULL,
  `item_type` varchar(255) NOT NULL,
  `item_damage` int(11) NOT NULL,
  `isEquipped` boolean NOT NULL,
  `item_element` varchar(255) NOT NULL,
  `item_crit_chance` int(11) NOT NULL,
  `item_projectile` varchar(255)
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
  FOREIGN KEY (`item_id`, `user_id`) REFERENCES inventory(`item_id`, `user_id`)
);
