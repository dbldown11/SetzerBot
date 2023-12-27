import asqlite
import os

from functions.constants import DATA_PATH

async def db_init():
    path = os.path.join(DATA_PATH, 'draftdata.db')
    if not os.path.exists(DATA_PATH):
        try:
            os.makedirs(DATA_PATH)
            print(f"Created db directories: {DATA_PATH}. This should only happen on SetzerBot's first run!")
        except Exception as e:
            emessage = f"Unable to create directory {DATA_PATH}"
            raise Exception(emessage)
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            ### this builds the db if it doesn't exist
            # create cards table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "cards" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "category"	TEXT,
                "weighting"	TEXT,
                "rarity"	INTEGER,
                "name"	TEXT,
                "desc"	TEXT,
                "difficulty" INTEGER
                );""")

            # create drafters table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "drafters" (
                "index_id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "draft_id" INTEGER,
                "user_id"	INTEGER,
                "isready"	INTEGER,
                "pick_order"	INTEGER,
                "picks_made"	INTEGER,
                "persona"       INTEGER
                );""")

            # create drafts table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "drafts" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "guild_id"	INTEGER,
                "creator_id"	INTEGER,
                "date_started"	TEXT,
                "date_finished"	TEXT,
                "max_drafters" INTEGER,
                "total_picks"	INTEGER,
                "cards_per_pick"	INTEGER,
                "draft_order"	TEXT,
                "flagstring"	TEXT,
                "raceroom" TEXT
                );""")

            # create picks table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "picks" (
                "index_id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "draft_id"	INTEGER,
                "drafter_id" INTEGER,
                "card_id"	INTEGER,
                "pick_number"	INTEGER,
                "pick_options"  TEXT,
                "removed_card"	INTEGER,
                "isremoved"	INTEGER
                );""")

            await cursor.execute("""CREATE TABLE IF NOT EXISTS "personas" (
                "index_id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "name"	TEXT,
                "bias" TEXT,
                "rarity_bias" INTEGER,
                "fav_cards"	TEXT,
                "fav_quote" TEXT
                );""")

            await conn.commit()

async def db_init_br():
    path = os.path.join(DATA_PATH, 'br_data.db')
    if not os.path.exists(DATA_PATH):
        try:
            os.makedirs(DATA_PATH)
            print(f"Created db directories: {DATA_PATH}. This should only happen on SetzerBot's first run!")
        except Exception as e:
            emessage = f"Unable to create directory {DATA_PATH}"
            raise Exception(emessage)
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            ### this builds the db if it doesn't exist
            # create cards table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "br_cards" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "category"	TEXT,
                "weighting"	TEXT,
                "rarity"	INTEGER,
                "name"	TEXT,
                "desc"	TEXT,
                "difficulty" INTEGER
                );""")

            # create drafters table -> player_id, user_id, *group_id, demoted, recently_demoted, final_table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "br_players" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "user_id" INTEGER,
                "username" TEXT,
                "group_id"	INTEGER,
                "is_demoted"	INTEGER,
                "is_recently_demoted"	INTEGER,
                "is_final_table"	INTEGER,
                "group_cards" TEXT,
                "is_lounge_winner" INTEGER,
                "date_joined" TEXT
                );""")

            # create drafts table -> group_id, group_guild, group_name, group_channel (or group_thread)
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "br_groups" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "guild_id"	INTEGER,
                "name"	TEXT,
                "channel_id"	INTEGER,
                "role_id" INTEGER
                );""")

            # create picks table -> group_week_id, *group_id, week_num, week_picks_started_date, week_picks_ended_date, flagstring
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "br_group_weeks" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "group_id"	INTEGER,
                "week_num"	INTEGER,
                "week_picks_started_date"	TEXT,
                "week_picks_ended_date"	TEXT,
                "flagstring" TEXT,
                "raceroom" TEXT
                );""")

            # create picks -> group_pick_id, *group_id, *player_id, pick_number, removed_card, isremoved
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "br_picks" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "group_id"	INTEGER,
                "player_id" INTEGER,
                "week_id" INTEGER,
                "card_id" INTEGER,
                "pick_number"	INTEGER,
                "pick_options"  TEXT,
                "removed_card"	INTEGER,
                "isremoved"	INTEGER
                );""")

            await conn.commit()