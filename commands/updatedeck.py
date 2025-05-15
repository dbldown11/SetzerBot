import csv
import asqlite
import os
import discord

from functions.db_init import db_init

from functions.constants import DATA_PATH

async def updatedeck(interaction, deck_csv):
    """
    Reloads the deck of cards from an uploaded file

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    deck_csv : discord.Attachment
        a csv containing all the cards available for drafting
        headings:
            id - integer (sequential id, non-repeating)
            category - text (one of Challenge, Commands, Enemies, Items, KT Reqs, KT Skip, Magic, Objectives, Party, Scaling, Stats)
            weighting - integer (1 = Mythic, 2 = Rare, 3 = Uncommon, 4 = Common)
            rarity - text (Mythic, Rare, Uncommon, Common
            name - text (unique card name)
            desc - text (description of the card's effects)

    Returns
    -------
    Nothing
    """
    if not deck_csv.filename.endswith('.csv'):
        emessage = f'Please attach a csv file.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    else:
        await deck_csv.save(deck_csv.filename)

    path = os.path.join(DATA_PATH, 'draftdata.db')
    print('ok starting function')
    #async with asqlite.connect(path) as conn:
        #async with conn.cursor() as cursor:
    # Create a table in the database to hold the CSV data
            #cursor.execute('''CREATE TABLE IF NOT EXISTS my_table (col1 TEXT, col2 TEXT, col3 TEXT)''')

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DROP TABLE cards")
            print('dropped table')

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "cards" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "category"	TEXT,
                "weighting"	TEXT,
                "rarity"	INTEGER,
                "name"	TEXT,
                "desc"	TEXT,
                "difficulty" INTEGER,
                "mutual_exclusive" TEXT,
                "character" INTEGER,
                "objectives" INTEGER
                );""")
            #print('made new table')
            #await conn.commit()
            #print('committed')
            #await conn.close()
            #print('closed')

    with open(deck_csv.filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        print('we in the csv now')
        # Skip the header row (if there is one)
        next(csv_reader, None)
        # Iterate over the remaining rows and insert them into the database
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as cursor:
                for csv_row in csv_reader:
                    #print(csv_row)
                    await cursor.execute("""INSERT INTO cards (id, category, weighting, rarity, name, desc, difficulty,
                    mutual_exclusive, character, objectives) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tuple(csv_row))

    # Commit the changes to the database and close the connection
                #await conn.commit()
                #await conn.close()

    os.remove(deck_csv.filename)

    await interaction.response.send_message('Deck updated!', ephemeral=True)