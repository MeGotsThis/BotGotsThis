CREATE TABLE auto_join (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    priority INT NOT NULL DEFAULT 0,
    useEvent BOOL NOT NULL DEFAULT 0
);

CREATE TABLE oauth_tokens (
    broadcaster VARCHAR NOT NULL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE
);

CREATE TABLE custom_commands (
    broadcaster VARCHAR NOT NULL,
    permission VARCHAR NOT NULL,
    command VARCHAR NOT NULL,
    commandDisplay VARCHAR,
    fullText VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, permission, command)
);

CREATE INDEX command_broadcaster ON custom_commands (broadcaster, command);

CREATE TABLE chat_features (
    broadcaster VARCHAR NOT NULL,
    feature VARCHAR NOT NULL,
    PRIMARY KEY (broadcaster, feature)
);

CREATE TABLE game_abbreviations (
    abbreviation VARCHAR NOT NULL PRIMARY KEY,
    twitchGame VARCHAR NOT NULL
);

INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('aoe2hd', 'Age of Empires II: HD Edition');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmngreen', 'Pokémon Green');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnredblue', 'Pokémon Red/Blue');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnrb', 'Pokémon Red/Blue');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnyellow', 'Pokémon Yellow: Special Pikachu Edition');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmny', 'Pokémon Yellow: Special Pikachu Edition');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmngoldsilver', 'Pokémon Gold/Silver');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmngs', 'Pokémon Gold/Silver');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmncrystal', 'Pokémon Crystal');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnrubysapphire', 'Pokémon Ruby/Sapphire');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnrs', 'Pokémon Ruby/Sapphire');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnemerald', 'Pokémon Emerald');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmne', 'Pokémon Emerald');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnfrlg', 'Pokémon FireRed/LeafGreen');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmndp', 'Pokémon Diamond/Pearl');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnplat', 'Pokémon Platinum');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnhgss', 'Pokémon HeartGold/SoulSilver');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnblackwhite', 'Pokémon Black/White');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnbw', 'Pokémon Black/White');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnblackwhite2', 'Pokémon Black/White Version 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnb2w2', 'Pokémon Black/White Version 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnxy', 'Pokémon X/Y');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnoras', 'Pokémon Omega Ruby/Alpha Sapphire');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pokemontcg', 'Pokémon Trading Card Game');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnstadium', 'Pokémon Stadium');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnstadium2', 'Pokémon Stadium 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pokemoncol', 'Pokémon Colosseum');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pokemonxd', 'Pokémon XD: Gale of Darkness');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pokemonbr', 'Pokémon Battle Revolution');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnsnap', 'Pokémon Snap');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('hypikachu', 'Hey You, Pikachu!');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnchannel', 'Pokémon Channel');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pokemate', 'Pokémate');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnbattrio', 'Pokémon Battrio');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mpkmnr', 'My Pokémon Ranch');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnconquest', 'Pokémon Conquest');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pknt', 'Pokkén Tournament');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmndash', 'Pokémate');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('ppc', 'Pokémon Puzzle Challenge');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('ppl', 'Pokémon Puzzle League');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmntrozei', 'Pokémon Trozei!');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnbt', 'Pokémon Battle Trozei');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pmdredblue', 'Pokémon Mystery Dungeon: Blue/Red Rescue Team');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pmdeodt', 'Pokémon Mystery Dungeon: Explorers of Darkness/Time');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pmdeos', 'Pokémon Mystery Dungeon: Explorers of Sky');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pmdgti', 'Pokémon Mystery Dungeon: Gates to Infinity');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnpinball', 'Pokémon Pinball');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnpbrs', 'Pokémon Pinball: Ruby & Sapphire');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnrumble', 'Pokémon Rumble');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnrumbleblast', 'Pokémon Rumble Blast');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnrumbleu', 'Pokémon Rumble U');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnranger', 'Pokémon Ranger');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnrangersoa', 'Pokémon Ranger: Shadows of Almia');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pkmnrangergs', 'Pokémon Ranger: Guardian Signs');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pokeparkwii', 'PokéPark Wii: Pikachu''s Adventure');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('pokepark2', 'PokéPark 2: Wonders Beyond');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm1', 'Mega Man');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm2', 'Mega Man 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm3', 'Mega Man 3');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm3rr', 'Mega Man 3: The Robots are Revolting');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm4', 'Mega Man 4');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm5', 'Mega Man 5');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm6', 'Mega Man 6');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm7', 'Mega Man 7');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm8', 'Mega Man 8: Anniversary Edition');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm9', 'Mega Man 9');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm10', 'Mega Man 10');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmww', 'Mega Man: The Wily Wars');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmac', 'Mega Man Anniversary Collection');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('rmf', 'Mega Man & Bass');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmb', 'Mega Man & Bass');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('rmfmknc', 'Rockman & Forte: Mirai kara no Chousensha');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm1gb', 'Mega Man: Dr Wily''s Revenge');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm2gb', 'Mega Man II');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm3gb', 'Mega Man III');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm4gb', 'Mega Man IV');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm5gb', 'Mega Man V');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx', 'Mega Man X');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx2', 'Mega Man X2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx3', 'Mega Man X3');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx4', 'Mega Man X4');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx5', 'Mega Man X5');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx6', 'Mega Man X6');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx7', 'Mega Man X7');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx8', 'Mega Man X8');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmxc', 'Mega Man X Collection');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmxgb', 'Mega Man Xtreme');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmx2gb', 'Mega Man Xtreme 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmxcm', 'Mega Man X: Command Mission');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmz', 'Mega Man Zero');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmz2', 'Mega Man Zero 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmz3', 'Mega Man Zero 3');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmz4', 'Mega Man Zero 4');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmzc', 'Mega Man Zero Collection');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmzx', 'Mega Man ZX');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmzxa', 'Mega Man ZX Advent');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbn1', 'Mega Man Battle Network');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbn2', 'Mega Man Battle Network 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbn3', 'Mega Man Battle Network 3');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbn4', 'Mega Man Battle Network 4');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbn4.5', 'Rockman EXE 4.5 Real Operation');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbn5', 'Mega Man Battle Network 5');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbn5ds', 'Mega Man Battle Network 5: Double Team DS');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbn6', 'Mega Man Battle Network 6');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmsf1', 'Mega Man Star Force');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmsf2', 'Mega Man Star Force 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmsf3', 'Mega Man Star Force 3');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbcc', 'Mega Man Battle Chip Challenge');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('rmeoss', 'Rockman EXE Operate Shooting Star');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmbncx', 'Mega Man Battle Network Chrono X');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mmtpb', 'Mega Man: The Power Battle');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm2tbf', 'Mega Man 2: The Power Fighters');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('rmbf', 'Rockman Battle & Fighters');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mm64', 'Mega Man 64');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mml', 'Mega Man Legends');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('mml2', 'Mega Man Legends 2');
INSERT INTO game_abbreviations (abbreviation, twitchGame) VALUES ('rmbc', 'Rockman Battle & Chase');
