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
  `item_type` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `basic_items` (
  `item_id` varchar(20) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `item_price` varchar(255) NOT NULL,
  `item_emoji` varchar(255) NOT NULL,
  `item_rarity` varchar(255) NOT NULL,
  `item_type` varchar(255) NOT NULL,
  `item_damage` int(11) NOT NULL,
  `isUsable` boolean NOT NULL,
  `inShop` boolean NOT NULL,
  `isEquippable` boolean NOT NULL,
  `item_description` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `shop` (
  `item_id` varchar(20) NOT NULL,
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
  `isStreamer` boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS `inventory` (
  `user_id` varchar(20) NOT NULL,
  `item_id` varchar(20) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `item_price` varchar(255) NOT NULL,
  `item_emoji` varchar(255) NOT NULL,
  `item_rarity` varchar(255) NOT NULL,
  `item_amount` int(11) NOT NULL,
  `item_type` varchar(255) NOT NULL,
  `item_damage` int(11) NOT NULL,
  `isEquipped` boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);