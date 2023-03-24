import discord
import asqlite
import os

from functions.constants import DATA_PATH
from functions.get_difficulty_rating import get_difficulty_rating

async def showpicks(interaction) -> dict:
    """
    Shows the current and future picks of a draft in the current channel

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
    #get the current draft's info from the db
    # check if this raceroom already has a draft and if the draft has already started
    async with asqlite.connect(path) as conn:
        # conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafts WHERE raceroom = ?", (channel.name,))
            data = await curs.fetchone()
            # remember: data is a Rows, not a list

    if data == None:
        emessage = f'No draft has been started for this raceroom.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    if data['date_started'] == None:
        emessage = f'The draft has not begun yet, picks will not be generated until the draft begins.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #get all picks for this draft from the db
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM picks WHERE draft_id = ?", (data['id'],))
            all_picks = await curs.fetchall()

    #get all drafters for this draft from the db
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ?", (data['id'],))
            drafters = await curs.fetchall()

    #get all card data
    card_data = []

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM cards""")
            card_data = await curs.fetchall()
            # remember: data is a list of Rows, not a list of lists
            await curs.close()

    info_string = ''
    await interaction.response.defer()
    count_pick = 0
    for pick in all_picks:
        count_pick += 1
        drafter_user_id = [x['user_id'] for x in drafters if x['index_id'] == pick['drafter_id']]
        drafter_name = interaction.guild.get_member(drafter_user_id[0])
        pick_number = pick['pick_number']
        if pick['card_id'] is not None:
            if pick['card_id'] == 0:
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

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT DISTINCT cards.name, cards.difficulty FROM cards INNER JOIN picks ON cards.id = picks.card_id 
                WHERE picks.draft_id = ? AND cards.difficulty IS NOT NULL AND 
                picks.isremoved != 1 AND picks.card_id != 0""", (data['id'],))
            difficulty_picks = await curs.fetchall()
    if difficulty_picks is not None:
        difficulty_list = [row[1] for row in difficulty_picks]
        difficulty = sum(difficulty_list)
    else:
        difficulty = 0

    diff_rating = await get_difficulty_rating(difficulty)
    info_string += f'\nBased on the picks made above, this flagset is currently estimated to be **{diff_rating}**.'

    await interaction.followup.send(info_string)
