import discord
import asqlite
import os
import csv

from functions.constants import DATA_PATH

async def br_exportplayers(interaction) -> None:
    """
    Exports all players in the battle royale into a CSV

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the call

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')

    await interaction.response.defer(ephemeral=True)

    #get all players from the db
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_players")
            all_players = await curs.fetchall()

    with open('player_export.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(all_players)

    await interaction.user.send(file=discord.File('player_export.csv'))
    await interaction.followup.send('CSV sent!',ephemeral=True)