import discord
import asqlite
import os
import random

from functions.constants import DATA_PATH

async def addbotdrafter(interaction) -> dict:
    """
    Adds an AI drafter to a draft in the channel the command is called in

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
    if channel.type == discord.ChannelType.private:
        channel_name = 'DM'
    #check if this raceroom already has a draft and if the draft has already started and has not finished
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafts WHERE raceroom = ? AND date_finished IS NULL",(channel.name,))
            this_draft = await curs.fetchone()
            # remember: data is a Rows, not a list

    if this_draft == None:
        emessage = f'No draft has been created for this raceroom - use the `/newdraft` command to set up a draft first.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    else:
        current_draft_id = this_draft['id']
        if not this_draft[3] == None:
            emessage = f'Unable to add an AI drafter to a draft in progress.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    if str(interaction.user.id) != str(this_draft['creator_id']):
        emessage = f'Only the draft creator can add bots to a draft.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #check if this draft is full
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ?",(current_draft_id,))
            drafter_data = await curs.fetchall()
            # remember: drafter_data is a list of Rows, not a list of lists

    if len(drafter_data) >= this_draft[5]:
        emessage = f'Unable to add AI drafter, the draft already has the maximum number of drafters ({this_draft[5]})'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #get a list of AI personas are already in the draft
    current_personas = []
    for x in drafter_data:
        if x['persona'] is not None:
            current_personas.append(x['persona'])

    #check if we're looking at an all AI draft and prevent it
    if len(current_personas) >= this_draft['max_drafters']-1:
        emessage = f'Unable to add AI drafter, the draft already has the maximum number of AI drafters ({this_draft[5]-1})'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #check if all AI personas are already in the draft - this should not actually ever happen but better safe than sorry
    if set(current_personas) == set(range(14)):
        emessage = f'Unable to add AI drafters, all possible AI personas are already in this draft.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #get a random persona that is not already in the draft
    random_persona = random.randint(0, 13)
    while random_persona in current_personas:
        random_persona = random.randint(0, 13)


    #get the persona requested
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM personas WHERE id = ?",(random_persona,))
            persona_drafter_data = await curs.fetchone()


    #checks are passed and AI is now added to the draft
    new_drafter_data = (current_draft_id,None,True,0,random_persona)
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("""INSERT INTO drafters (draft_id, user_id, isready, picks_made, persona) VALUES (?, ?, ?, ?, ?);""", new_drafter_data)
            await conn.commit()

    if interaction.response.is_done():
        await channel.send(f'{persona_drafter_data["name"]} (AI) has joined the draft. There are now {len(drafter_data)+1} drafters.')
    else:
        await interaction.response.send_message(f'{persona_drafter_data["name"]} (AI) has joined the draft. There are now {len(drafter_data)+1} drafters.')

    if len(drafter_data)+1 >= this_draft['max_drafters']:
        await channel.send('The draft for this race room is now full! The draft will begin when the draft creator uses the `/startdraft` command.')