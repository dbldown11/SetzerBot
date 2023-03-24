import discord
import asqlite
import os
import datetime

from functions.constants import DATA_PATH, BR_ROLE

from classes.buttons import CardButton, CardView
from classes.calmness import CalmnessView
from commands.createflags import createflags
from functions.stringfunctions import int_list_to_string,string_to_int_list

from functions.constants import DATA_PATH

async def br_skippick(interaction,group_name) -> None:
    """
    Skip the current player's pick at a BR table

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the call

    group_name : str
        The name of the group to be skipped

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')

    #get group info for all groups
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_groups")
            br_groups = await curs.fetchall()

    #current_group = [group for group in br_groups if group['name'] == group_name]
    current_group = None
    for group in br_groups:
        if group['name'] == group_name:
            current_group = group

    if current_group is None:
        emessage = f"There is no Blackjack Battle Royale table called {group_name}."
        await interaction.response.send_message(content=emessage,ephemeral=True)
        return None

    #get most recent week
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = (SELECT MAX(week_num) FROM br_group_weeks)",
                               (current_group['id'],))
            current_group_week = await curs.fetchone()

    #get this user's group's current pick
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM br_picks WHERE week_id = ? AND group_id = ? AND card_id IS NULL LIMIT 1""",
                               (current_group_week['id'],current_group['id']))
            current_pick = await curs.fetchone()

    if current_pick['card_id'] is not None:
        emessage = f'A card has already been picked.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            #print(f'writing this to br_picks for card_id where id is this: {new_pick_data}')
            await curs.execute("""UPDATE br_picks SET card_id = 0, isremoved = 0 WHERE id = ?""", (current_pick['id']))
            await conn.commit()

    await interaction.response.send_message('Pick successfully skipped. The group''s channel has been notified.', ephemeral=True)

    # announce the next drafter
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_picks WHERE week_id = ? AND card_id IS NULL LIMIT 1",
                               (current_group_week['id'],))
            current_pick = await curs.fetchone()
            # print(current_pick)

    channel = discord.utils.get(interaction.guild.text_channels, id=current_group['channel_id'])
    if current_pick is not None:
        query = (current_pick['player_id'], current_group['id'])
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM br_players WHERE id = ? AND group_id =?", query)
                current_drafter = await curs.fetchone()
    if current_pick == None:
        await channel.send(f'Picks for this week have been completed!')

        # fetch the cards in the draft
        # print(f'going to pull all the cards from group {data["id"]}')
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""SELECT card_id FROM br_picks WHERE group_id = ? AND isremoved = 0""",
                                   (current_group['id'],))
                # card_list = [row['card_id'] for row in await curs.fetchall()]
                all_picks = await curs.fetchall()
                card_list = [x['card_id'] for x in all_picks]
                print(f'the card_list i pulled from the db is {card_list}')
        flagstring = await createflags(interaction, card_list)
        finish_query = (datetime.datetime.now(), flagstring, current_group['id'], current_group_week['week_num'])
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute(
                    """UPDATE br_group_weeks SET week_picks_ended_date = ?, flagstring = ? WHERE group_id =? AND week_num = ?""",
                    finish_query)
                await conn.commit()
        await channel.send(f"The flagset for this table week is now:\n```{flagstring}```")
        return None
    else:
        next_up = interaction.guild.get_member(current_drafter["user_id"])
        await channel.send(f'The next drafter is **{next_up.display_name}**!\n'
                           f'{next_up.mention}, please make your pick using the `/br pick` command.')