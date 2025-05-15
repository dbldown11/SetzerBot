import discord
import asqlite
import os

from functions.constants import DATA_PATH
from functions.get_difficulty_rating import get_difficulty_rating
from functions.last_card import last_card
from functions.remove_earliest_duplicates import remove_earliest_duplicates
from functions.remove_card import remove_card

async def showpicks(interaction) -> None:
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
            this_draft = await curs.fetchone()
            # remember: data is a Rows, not a list

    if this_draft == None:
        emessage = f'No draft has been started for this raceroom.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    if this_draft['date_started'] == None:
        emessage = f'The draft has not begun yet, picks will not be generated until the draft begins.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #get all picks for this draft from the db
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM picks WHERE draft_id = ?", (this_draft['id'],))
            all_picks = await curs.fetchall()

    #get all drafters for this draft from the db
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ?", (this_draft['id'],))
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
        new_page = False
        drafter_user_id = [x['user_id'] for x in drafters if x['index_id'] == pick['drafter_id']]
        if drafter_user_id[0] is None:
            persona_id = [x['persona'] for x in drafters if x['index_id'] == pick['drafter_id']]
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute("""SELECT name FROM personas WHERE id = ?""",(persona_id[0],))
                    drafter_row = await curs.fetchone()
                    drafter_name = drafter_row[0] + " (Bot)"
                    await curs.close()
        else:
            drafter_member = interaction.guild.get_member(drafter_user_id[0])
            drafter_name = drafter_member.display_name
        pick_number = pick['pick_number']
        if pick['card_id'] is not None:
            if pick['card_id'] == 0:
                removed_card_id = [x['card_id'] for x in all_picks if x['pick_number'] == pick['removed_card']]
                removed_card_name = [x['name'] for x in card_data if x['id'] == removed_card_id[0]]
                info_string += f'**Pick #{pick_number}** - {drafter_name} selected **Calmness** and removed Pick #{pick["removed_card"]} ({removed_card_name[0]})\n'
            else:
                card_id = [x['id'] for x in card_data if x['id'] == pick['card_id']]
                card_name = [x['name'] for x in card_data if x['id'] == pick['card_id']]
                card_desc = [x['desc'] for x in card_data if x['id'] == pick['card_id']]
                card_exclusives = [x['mutual_exclusive'] for x in card_data if x['id'] == pick['card_id']]

                #build the dict/list/whatever of character cards and their potential replacements
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        await curs.execute("SELECT * FROM picks WHERE card_id IS NOT 0 AND card_id IS NOT NULL "
                                           "AND isremoved = 0 AND draft_id = ? ORDER BY pick_number ASC",
                                           (this_draft['id']))
                        rows = await curs.fetchall()

                party_cards = [row[3] for row in sorted(rows, key=lambda r: r[4])]

                party_size_card = await last_card(party_cards, 27, 28)
                if party_size_card == 27:
                    party_size = 2
                elif party_size_card == 28:
                    party_size = 4
                else:
                    party_size = 3

                party_cards = [card for card in party_cards if (1 <= card <= 26) or (208 <= card <= 231)]

                if len(party_cards) > 1:
                    for cardnum in range(1, 13):
                        variants = [cardnum, cardnum + 14, cardnum + 207, cardnum + 219]
                        present = [v for v in variants if v in party_cards]

                        if len(present) > 1:
                            # Ask which of the present ones was added last
                            last = await last_card(party_cards, *present)
                            # Remove all others
                            for v in present:
                                if v != last:
                                    party_cards = remove_card(party_cards, v)

                # remove the earliest of any duplicate cards
                party_cards = remove_earliest_duplicates(party_cards)

                replaced_card_ids = []

                if len(party_cards) >= party_size and len(party_cards) > 0:
                    replaced_card_ids = party_cards[: -party_size]

                    '''await curs.execute(
                        "SELECT * FROM picks WHERE draft_id = ? AND isremoved = 0 AND "
                        "card_id = ? ORDER BY pick_number DESC LIMIT 1",
                        (this_draft['id'], replaced_card_id))'''

                #find if it was superceded
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        query = (f"SELECT * FROM picks WHERE card_id IN ({(','.join(card_exclusives))}) AND draft_id = {this_draft['id']} "
                            f"AND isremoved = 0 AND pick_number > {pick_number} ORDER BY pick_number ASC LIMIT 1")
                        await curs.execute(query)
                        replacing_pick = await curs.fetchone()

                        if pick['isremoved'] > 0:
                            info_string += f'**Pick #{pick_number}** - :no_entry_sign: Removed by Calmness :no_entry_sign: ~~{drafter_name} selected **{card_name[0]}** *({card_desc[0]})*~~\n'
                        elif replacing_pick is not None:
                            await curs.execute("SELECT * FROM cards WHERE id = ?", (replacing_pick['card_id'],))
                            replaced_card = await curs.fetchone()
                            info_string += f'**Pick #{pick_number}** - :x: Replaced by Pick #{replacing_pick["pick_number"]} ({replaced_card["name"]}) :x: ~~{drafter_name} selected **{card_name[0]}** *({card_desc[0]})*~~\n'
                        elif pick['card_id'] in replaced_card_ids:
                            info_string += f'**Pick #{pick_number}** - :x: Replaced by later character card picks :x: ~~{drafter_name} selected **{card_name[0]}** *({card_desc[0]})*~~\n'
                        else:
                            info_string += f'**Pick #{pick_number}** - {drafter_name} selected **{card_name[0]}** *({card_desc[0]})*\n'
        else:
            info_string += f'**Pick #{pick_number}** - To be selected by {drafter_name}\n'
        if len(info_string) > 1600:
            await interaction.followup.send(info_string)
            info_string = ''

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT DISTINCT cards.name, cards.difficulty FROM cards INNER JOIN picks ON cards.id = picks.card_id 
                WHERE picks.draft_id = ? AND cards.difficulty IS NOT NULL AND 
                picks.isremoved != 1 AND picks.card_id != 0""", (this_draft['id'],))
            difficulty_picks = await curs.fetchall()
    if difficulty_picks is not None:
        difficulty_list = [row[1] for row in difficulty_picks]
        difficulty = sum(difficulty_list)
    else:
        difficulty = 0

    diff_rating = await get_difficulty_rating(difficulty)
    info_string += f'\nBased on the picks made above, this flagset is currently estimated to be **{diff_rating}**.'

    await interaction.followup.send(info_string)
