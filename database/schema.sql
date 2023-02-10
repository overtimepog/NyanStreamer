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
  `item_id` varchar(20) NOT NULL,
  `item_name` varchar NOT NULL,
  `item_price` varchar(255) NOT NULL,
  `item_emoji` varchar(255) NOT NULL,
  `item_rarity` varchar(255) NOT NULL,
  `twitch_id` varchar(255) NOT NULL,
  `item_type` varchar(255) NOT NULL,
  `item_damage` int(11) NOT NULL,
  `item_element` varchar(255) NOT NULL,
  `item_crit_chance` int(11) NOT NULL,
  `item_effect` varchar(255) NOT NULL,
  `isUsable` boolean NOT NULL,
  `isEquippable` boolean NOT NULL
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
  `item_projectile` varchar(255) NOT NULL,
  `recipe_id` varchar(255) NOT NULL,
  `isHuntable` boolean NOT NULL,
  `item_hunt_chance` int(11) NOT NULL,
  `item_effect` varchar(255) NOT NULL,
  `isMineable` boolean NOT NULL,
  `item_mine_chance` int(11) NOT NULL,
  `quote_id` varchar(255) NOT NULL,
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
  `structure_outcomes` varchar(255) NOT NULL,
  FOREIGN KEY (structure_outcomes) REFERENCES structure_outcomes(structure_id)
);

CREATE TABLE IF NOT EXISTS `structure_outcomes`(
  `structure_id` varchar(255) NOT NULL,
  `structure_quote` varchar(255) NOT NULL,
  `structure_state` varchar(255) NOT NULL,
  `outcome_chance` int(11) NOT NULL,
  `outcome_item` varchar(255) NOT NULL,
  `outcome_item_amount` int(11) NOT NULL,
  `outcome_money` int(11) NOT NULL,
  `outcome_xp` int(11) NOT NULL,
  FOREIGN KEY (outcome_item) REFERENCES basic_items(item_id)
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
  `battles_won` int(11) NOT NULL
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
  `item_projectile` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);