import discord
import asqlite
import os
import datetime
import random

from classes.confirm import Confirm

from functions.constants import DATA_PATH

async def startdraft(interaction) -> dict:
    """
    Starts a draft in the channel the command is called in

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
        if not data['date_started'] == None:
            emessage = f'This draft has already started.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

        if str(interaction.user.id) != str(data['creator_id']):
            emessage = f'Only the draft creator can start the draft.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    #check if the draft is below max capacity and get a confirmation
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ?",(current_draft_id,))
            drafter_data = await curs.fetchall()
            # remember: drafter_data is a list of Rows, not a list of lists

    if len(drafter_data) <= 0:
        emessage = f'No drafters have joined this draft yet.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    if len(drafter_data) < data[5]:
        view = Confirm()
        await interaction.response.send_message(f'Only {len(drafter_data)} drafters have joined out of a possible {data[5]}, are you sure you want to start?', view=view, ephemeral=True)
        await view.wait()
        if view.value is None:
            await interaction.edit_original_response(content='Request timed out, draft has not been started.',view=None)
        elif view.value:
            await interaction.edit_original_response(content='Starting draft...', view=None)
        else:
            await interaction.edit_original_response(content='Draft start has been cancelled.',view=None)
            return None

    #create draft order
    random.shuffle(drafter_data)
    pick_num = 1
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            for drafter in drafter_data:
                update_data = (pick_num,drafter['draft_id'],drafter['index_id'])
                await cursor.execute("UPDATE drafters SET pick_order = ? WHERE draft_id = ? AND index_id = ?",update_data)
                pick_num += 1

    #generate pick list
    #get list of drafters
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ?",(current_draft_id,))
            drafter_data = await curs.fetchall()
            # remember: drafter_data is a list of Rows, not a list of lists

    #sort the list in draft order
    ordered_list = sorted(drafter_data, key = lambda x: int(x['pick_order']))

    #create the list of picks
    pick_list = []
    pick_num = 1
    if data['draft_order'] == 'round':
        while pick_num <= data['total_picks']:
            pick_list.append(ordered_list[pick_num % len(ordered_list) - 1])
            pick_num += 1
    elif data['draft_order'] == 'snake':
        while pick_num <= data['total_picks']:
            if ((pick_num-1)//len(ordered_list)) % 2 == 0:
                pick_list.append(ordered_list[-pick_num % len(ordered_list)])
                pick_num += 1
            else:
                pick_list.append(ordered_list[pick_num % len(ordered_list) - 1])
                pick_num += 1
    elif data['draft_order'] == 'random':
        while pick_num <= data['total_picks']:
            pick_list.append(ordered_list[random.randint(0,len(ordered_list)-1)])
            pick_num += 1

    #add these picks to the DB
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            for count, pick in enumerate(pick_list):
                pick_data = (data['id'],pick['index_id'],count+1,0)
                await curs.execute("""INSERT INTO picks (draft_id, drafter_id, pick_number, removed_card) VALUES (?, ?, ?,?);""", pick_data)
                await conn.commit()

    #debug - show me the pick order
    #for x in pick_list:
    #    drafting_member = interaction.guild.get_member(x['user_id'])
    #    print(drafting_member)
    #print(pick_list)

    #start the draft
    start_data=(datetime.datetime.now(),channel.name)
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE drafts SET date_started = ? WHERE raceroom = ?",start_data)
            await conn.commit()

    #clean up and announce the deed is done
    if interaction.response.is_done():
        await interaction.edit_original_response(content=f'Draft started at {discord.utils.format_dt(datetime.datetime.now())}!', view=None)
    else:
        await interaction.response.send_message(f'Draft started at {discord.utils.format_dt(datetime.datetime.now())}!')

    await channel.send(f'The draft has started! There will be {data["total_picks"]} picks made - please use the `/showpicks` command to see the draft order.')

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ? AND pick_num = 1", (data['id'],))
            current_drafter = await curs.fetchone()
    next_up = interaction.guild.get_member(current_drafter["user_id"])
    await channel.send(f'The first drafter is **{next_up.display_name}**!\n'
                       f'{next_up.mention}, please make your pick using the `/draftpick` command.')