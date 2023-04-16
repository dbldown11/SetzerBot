import discord
import asqlite
import os

from functions.constants import DATA_PATH

async def br_showpicks(interaction) -> None:
    """
    Shows the current and future picks of a group in the current channel

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the call

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')
    channel = interaction.channel

    #get the current draft's info from the db
    # check if this raceroom already has a draft and if the draft has already started
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_groups WHERE channel_id = ?", (channel.id,))
            current_group = await curs.fetchone()


    #get all picks for this group from the db
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_picks WHERE group_id = ?", (current_group['id'],))
            all_picks = await curs.fetchall()

    #get all drafters for this draft from the db
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_players")
            drafters = await curs.fetchall()

    #get all card data
    card_data = []

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM br_cards""")
            card_data = await curs.fetchall()
            # remember: data is a list of Rows, not a list of lists
            await curs.close()

    info_string = ''
    await interaction.response.defer()
    count_pick = 0
    for pick in all_picks:
        count_pick += 1
        drafter_user_id = [x['user_id'] for x in drafters if x['id'] == pick['player_id']]
        print(drafter_user_id)
        drafter_name = interaction.guild.get_member(drafter_user_id[0])
        print(f'drafter_name is {drafter_name}')
        pick_number = pick['pick_number']
        if pick['card_id'] is not None:
            if pick['card_id'] == 0:
                if pick['removed_card'] is None or pick['removed_card'] == 0:
                    info_string += f'**Pick #{pick_number}** - {drafter_name.display_name} pick was skipped\n'
                else:
                    removed_card_id = [x['card_id'] for x in all_picks if x['pick_number'] == pick['removed_card']]
                    removed_card_name = [x['name'] for x in card_data if x['id'] == removed_card_id[0]]
                    info_string += f'**Pick #{pick_number}** - {drafter_name.display_name} selected **Calmness** and removed Pick #{pick["removed_card"]} ({removed_card_name[0]})\n'
            else:
                card_name = [x['name'] for x in card_data if x['id'] == pick['card_id']]
                card_desc = [x['desc'] for x in card_data if x['id'] == pick['card_id']]
                if pick['isremoved'] == 0:
                    info_string += f'**Pick #{pick_number}** - {drafter_name.display_name} selected **{card_name[0]}** *({card_desc[0]})*\n'
                else:
                    info_string += f'**Pick #{pick_number}** - ~~{drafter_name.display_name} selected **{card_name[0]}** *({card_desc[0]})*~~ :no_entry_sign: Removed by Calmness\n'
        else:
            info_string += f'**Pick #{pick_number}** - To be selected by {drafter_name.display_name}\n'
        if count_pick % 10 == 0:
            await interaction.followup.send(info_string)
            info_string = ''

    if info_string != '':
        await interaction.followup.send(info_string)
