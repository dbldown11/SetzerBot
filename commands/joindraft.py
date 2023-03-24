import discord
import asqlite
import os

from functions.constants import DATA_PATH

async def joindraft(interaction) -> dict:
    """
    Joins a draft in the channel the command is called in

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
        current_draft_id = data[0]
        if not data[3] == None:
            emessage = f'Unable to join a draft that has already started.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None
        #TODO check if max players already here

    #check if this player already joined this draft, or if the draft is full
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ?",(current_draft_id,))
            drafter_data = await curs.fetchall()
            # remember: drafter_data is a list of Rows, not a list of lists

    if len(drafter_data) >= data[5]:
        emessage = f'Unable to join, the draft already has the maximum number of drafters ({data[5]})'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    for drafter in drafter_data:
        if drafter[2] == interaction.user.id:
            emessage = f'You have already joined this draft!'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    #user has passed their checks and is now added to the draft
    new_drafter_data = (current_draft_id,interaction.user.id,False,0)
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("""INSERT INTO drafters (draft_id, user_id, isready, picks_made) VALUES (?, ?, ?, ?);""", new_drafter_data)
            await conn.commit()

    await interaction.response.send_message(f'{interaction.user.display_name} has joined the draft. There are now {len(drafter_data)+1} players in this draft.')
    #TODO add a diff message if the draft is full
    if len(drafter_data)+1 >= data['max_drafters']:
        await channel.send('The draft for this race room is now full! The draft will begin when the draft creator uses the `/startdraft` command.')