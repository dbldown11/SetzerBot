import discord
import asqlite
import os

from functions.constants import DATA_PATH
from functions.isAdmin import isAdmin

async def canceldraft(interaction) -> dict:
    """
    Cancels a draft in the channel the command is called in

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'draftdata.db')

    channel = interaction.channel

    #check if this raceroom already has a draft and if the draft has already started
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafts WHERE raceroom = ?",(channel.name,))
            data = await curs.fetchone()
            # remember: data is a Rows, not a list

    if data == None:
        emessage = f'No draft has been started for this raceroom - use the `/newdraft` command to start a draft first.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    else:
        if interaction.user.id != data['creator_id'] or not isAdmin(interaction.user):
            emessage = f'Only the draft creator can cancel the draft.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    #delete the draft
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM drafts WHERE raceroom = ?",(channel.name,))

    await interaction.response.send_message(
        f'The draft has been cancelled. Please use `/newdraft` if you would like to create a new one in this room.',
        ephemeral=True)