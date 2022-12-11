CREATE TABLE IF NOT EXISTS `blacklist` (
  `user_id` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `streamer` (
  `streamer_id` varchar NOT NULL,
  `streamer_channel` varchar NOT NULL,
  `user_id` varchar NOT NULL
);

CREATE TABLE IF NOT EXISTS `streamer_items` (
  `streamer_id` varchar(20) NOT NULL,
  `item_id` varchar(20) NOT NULL,
  `item_name` varchar NOT NULL,
  `item_price` varchar(255) NOT NULL,
  `item_emoji` varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);