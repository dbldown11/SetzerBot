import csv
import asqlite
import os
import discord

from functions.db_init import db_init

from functions.constants import DATA_PATH

async def updatepersonas(interaction, personas_csv):
    """
    Reloads the AI personas for AI drafters from an uploaded file

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    personas_csv : discord.Attachment
        a csv containing all the cards available for drafting
        headings:
            id - integer (sequential id, non-repeating)
            name - text (the proper caps name of the AI persona, i.e. 'Terra')
            bias - text (the descriptor of the drafter's difficulty bias: 'easy','medium','hard')
            fav_cards - text (a comma separated list of cards the ai will prefer to choose where possible)

    Returns
    -------
    Nothing
    """
    
    if not personas_csv.filename.endswith('.csv'):
        emessage = f'Please attach a csv file.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    else:
        await personas_csv.save(personas_csv.filename)

    path = os.path.join(DATA_PATH, 'draftdata.db')
    print('ok starting function')
    #async with asqlite.connect(path) as conn:
        #async with conn.cursor() as cursor:
    # Create a table in the database to hold the CSV data
            #cursor.execute('''CREATE TABLE IF NOT EXISTS my_table (col1 TEXT, col2 TEXT, col3 TEXT)''')

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DROP TABLE personas")
            print('dropped table')

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""CREATE TABLE IF NOT EXISTS "personas" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "name"	TEXT,
                "bias" TEXT,
                "rarity_bias" INTEGER,
                "fav_cards"	TEXT,
                "fav_quote" TEXT
                );""")

    with open(personas_csv.filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        print('we in the csv now')
        # Skip the header row (if there is one)
        next(csv_reader, None)
        # Iterate over the remaining rows and insert them into the database
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as cursor:
                for csv_row in csv_reader:
                    #print(csv_row)
                    await cursor.execute("""INSERT INTO personas (id, name, bias, rarity_bias, fav_cards, fav_quote) 
                    VALUES (?, ?, ?, ?, ?, ?)""", tuple(csv_row))

    # Commit the changes to the database and close the connection
                #await conn.commit()
                #await conn.close()

    os.remove(personas_csv.filename)

    await interaction.response.send_message('Personas updated!', ephemeral=True)