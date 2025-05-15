# import csv
import random
import datetime

import asqlite
import os
import asyncio

import discord

from collections import namedtuple
from classes.buttons import CardButton, CardView
from classes.calmness import CalmnessView
from commands.createflags import createflags
from functions.stringfunctions import int_list_to_string,string_to_int_list
from functions.get_difficulty_rating import get_difficulty_rating
from functions.botdraftpick import botpick
from functions.create_calmness_card import create_calmness_card
from functions.get_card_list_by_rarity import get_card_list_by_rarity
from functions.last_card import last_card
from functions.remove_earliest_duplicates import remove_earliest_duplicates
from functions.remove_card import remove_card


from functions.constants import DATA_PATH, COMMON, UNCOMMON, RARE, MYTHIC


async def draftpick(interaction):
    """
    Chooses a card for an active draft

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
        emessage = f'The draft has not begun yet, please wait for the draft creator to start the draft.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    else:
        current_draft_id = this_draft['id']
        if not this_draft['date_finished'] == None:
            emessage = f'This draft has already finished.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ? AND user_id = ?", (this_draft['id'],interaction.user.id))
            current_drafter = await curs.fetchone()

    if current_drafter == None:
        emessage = f'You are not a member of this draft.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND card_id IS NULL LIMIT 1", (this_draft['id'],))
            current_pick = await curs.fetchone()
            if current_pick == None:
                None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM cards""")
            card_data = await curs.fetchall()
            # remember: card_data is a list of Rows, not a list of lists
            #await curs.close()

    if current_pick['pick_number'] > 1:
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND pick_number = ?", (this_draft['id'],current_pick['pick_number']-1))
                last_pick = await curs.fetchone()
        if last_pick['card_id'] == 0 and last_pick['removed_card'] == 0:
            emessage = f'Please wait until the previous drafter has chosen their Calmness target.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    if current_pick['drafter_id'] != current_drafter['index_id']:
        query = (current_pick['drafter_id'], this_draft['id'])
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM drafters WHERE index_id = ? AND draft_id = ?", query)
                new_current_drafter = await curs.fetchone()
        new_current_drafter_name = interaction.guild.get_member(new_current_drafter['user_id'])
        emessage = f"It's not your turn to pick! The current drafter is **{new_current_drafter_name.display_name}**"
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    cards = []

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT card_id FROM picks WHERE draft_id = ? and card_id IS NOT NULL",
                               (this_draft['id'],))
            rows = await curs.fetchall()
            cards_picked = [row[0] for row in rows]
            if this_draft['card_removal'] == 'on_pick':
                pickable_cards = [card for card in card_data if card['id'] not in cards_picked]
            elif this_draft['card_removal'] == 'on_draw':
                await curs.execute("SELECT pick_options FROM picks WHERE draft_id = ? AND pick_options IS NOT NULL",
                                   (this_draft['id'],))
                rows = await curs.fetchall()
                cards_drawn = [
                    int(card_id.strip())
                    for row in rows
                    for card_id in row[0].split(',')
                    if card_id.strip() != '0'
                ]
                removed_cards = list(set(cards_picked) | set(cards_drawn))

                if len(cards_drawn) > 180:
                    pickable_cards = card_data
                else:
                    pickable_cards = [card for card in card_data if card['id'] not in removed_cards]
            else:
                pickable_cards = card_data

    # Remove unused character_cards
    if this_draft['banned_cards'] is not None:
        char_cards_to_remove = await string_to_int_list(this_draft['banned_cards'])
        pickable_cards = [card for card in pickable_cards if card['id'] not in char_cards_to_remove]

    # Now filtered_cards contains all rows from pickable_cards except those whose id is in banned_cards

    # Get remaining Mulligans
    async with (asqlite.connect(path) as conn):
        async with conn.cursor() as curs:
            await curs.execute("SELECT COALESCE (mulligans, 0) FROM picks WHERE index_id = ?",
                               (current_pick['index_id']))
            row = await curs.fetchone()
            mulls_remaining = this_draft['cards_per_pick'] - (row[0] if row else 0)

    if this_draft['mulligan'] == 'paris':
        cards_to_draw = mulls_remaining
    else:
        cards_to_draw = this_draft['cards_per_pick']

    if current_pick['pick_options'] is not None:
        for y in await string_to_int_list(current_pick['pick_options']):
            if y == 0:
                cards.append(await create_calmness_card())
            else:
                cards.append([new_card for new_card in card_data if new_card[0] == y][0])
    else:
        #determine if there are any eligible Calmness targets
        calmness_eligible = True
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                query = ("SELECT COUNT(*) FROM picks WHERE draft_id = ? AND card_id IS NOT NULL"
                         " AND card_id != 0 AND isremoved != 1")
                params = (this_draft['id'],)
                await curs.execute(query, params)
                targets = await curs.fetchone()
                if targets[0] == 0:
                    calmness_eligible = False

        # weights = ([i[3] for i in card_data])
        # things necessary to send to a command:
        # this_draft, cards_to_draw, card_data, pickable_cards
        has_drawn_removal = False
        pick_list = []
        while len(cards) < cards_to_draw:
            current_categories = [i[1] for i in cards]
            if this_draft['rarity'] == 'double':
                new_card = random.choices(pickable_cards,weights=[2 ** (i[3] - 1) for i in pickable_cards])[0]
            elif this_draft['rarity'] == 'ignore':
                new_card = random.choice(pickable_cards)
            elif this_draft['rarity'] == 'packs':
                # pack logic here
                # build lists of pickable cards for each rarity, and if there are less than 5 left in the deck,
                # then grab from the full base list of cards instead
                # Get card lists for each rarity (using fallback if needed)
                common_cards = await get_card_list_by_rarity(COMMON, pickable_cards, card_data)
                uncommon_cards = await get_card_list_by_rarity(UNCOMMON, pickable_cards, card_data)
                rare_cards = await get_card_list_by_rarity(RARE, pickable_cards, card_data)
                mythic_cards = await get_card_list_by_rarity(MYTHIC, pickable_cards, card_data)

                if this_draft['cards_per_pick'] == 1:
                    new_card = random.choice(random.choices([common_cards, uncommon_cards, rare_cards, mythic_cards], weights=[40, 30, 20, 10])[0])
                elif this_draft['cards_per_pick'] == 2:
                    if len(pick_list) == 0:
                        new_card = random.choice(random.choices([common_cards, uncommon_cards], weights=[70, 30])[0])
                    elif len(pick_list) == 1:
                        new_card = random.choice(random.choices([uncommon_cards, rare_cards, mythic_cards], weights=[50, 35, 15])[0])
                elif this_draft['cards_per_pick'] == 3:
                    if len(pick_list) == 0:
                        new_card = random.choice(common_cards)
                    elif len(pick_list) == 1:
                        new_card = random.choice(random.choices([common_cards, uncommon_cards], weights=[50, 50])[0])
                    elif len(pick_list) == 2:
                        new_card = random.choice(random.choices([uncommon_cards, rare_cards, mythic_cards], weights=[20, 60, 20])[0])
                elif this_draft['cards_per_pick'] == 4:
                    if len(pick_list) <= 1:
                        new_card = random.choice(common_cards)
                    elif len(pick_list) == 2:
                        new_card = random.choice(uncommon_cards)
                    elif len(pick_list) == 3:
                        new_card = random.choice(random.choices([rare_cards, mythic_cards], weights=[75, 25])[0])
                elif this_draft['cards_per_pick'] == 5:
                    if len(pick_list) <= 1:
                        new_card = random.choice(common_cards)
                    elif len(pick_list) == 2:
                        new_card = random.choice(random.choices([common_cards, uncommon_cards], weights=[75, 25])[0])
                    elif len(pick_list) == 3:
                        new_card = random.choice(uncommon_cards)
                    elif len(pick_list) == 4:
                        new_card = random.choice(random.choices([rare_cards, mythic_cards], weights=[75, 25])[0])


            else:
                new_card = random.choices(pickable_cards, weights=([int(i[3]) for i in pickable_cards]))[0]

            # adjust calmness rate based on frequency selection
            if this_draft['calmness'] == 'rare':
                calmness_freq = 0.01
            elif this_draft['calmness'] == 'none':
                calmness_freq = 0
            else:
                calmness_freq = 0.05

            if has_drawn_removal == False and random.random() < calmness_freq and current_pick['pick_number'] > 1 and \
                    this_draft['calmness'] not in ['every_pick', 'once_per_draft'] and calmness_eligible:
                new_card = await create_calmness_card()
                has_drawn_removal = True
                pick_list.append(new_card[0])
            elif len(current_categories) == 0:
                cards.append(new_card)
                pick_list.append(new_card[0])
            elif this_draft['categories'] == 'ignore':
                cards.append(new_card)
                pick_list.append(new_card[0])
            elif new_card[1] not in current_categories:
                cards.append(new_card)
                pick_list.append(new_card[0])

        # add calmness as a "bonus card" if every_pick is picked
        if this_draft['calmness'] == 'every_pick' and current_pick['pick_number'] > 1 and calmness_eligible:
            new_card = await create_calmness_card()
            cards.append(new_card)
            pick_list.append(new_card[0])

        # add calmness as a "bonus card" if once_per_draft is picked
        if this_draft['calmness'] == 'once_per_draft' and current_pick['pick_number'] > 1 and calmness_eligible:
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    query = (this_draft['id'], current_drafter['index_id'])
                    await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND drafter_id = ? and card_id = 0", query)
                    calmnesses_used = await curs.fetchall()
            if not calmnesses_used:
                new_card = await create_calmness_card()
                cards.append(new_card)
                pick_list.append(new_card[0])

        pick_options_query = await int_list_to_string(pick_list)

        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""UPDATE picks SET pick_options = ? WHERE index_id = ?""",
                                   (pick_options_query,current_pick['index_id']))
    embed = []

    view = CardView(interaction.user)
    for card in cards:
        if card[0] == 0:
            card_color = discord.Color.from_str('0x23272A')
        elif card[2] == 'Common':
            card_color = discord.Color.lighter_gray()
        elif card[2] == 'Uncommon':
            card_color = discord.Color.green()
        elif card[2] == 'Rare':
            card_color = discord.Color.blue()
        else:
            card_color = discord.Color.gold()

        # Check if replacing a previous pick
        replacement_note = ''
        if card[7] is not None:
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    query = (f"SELECT * FROM picks WHERE card_id IN ({card[7]}) AND draft_id = "
                             f"{this_draft['id']} AND isremoved = 0 ORDER BY pick_number DESC LIMIT 1")
                    await curs.execute(query)
                    replaced_pick = await curs.fetchone()

                    if replaced_pick is not None:
                        await curs.execute("SELECT * FROM cards WHERE id = ?",(replaced_pick['card_id'],))
                        replaced_card = await curs.fetchone()
                        if replaced_pick['card_id'] == card[0]:
                            replacement_note = f"\n\n**NOTE:** *This card\'s effect is already active (Pick #{replaced_pick['pick_number']})*"
                        else:
                            replacement_note = f'\n\n**NOTE:** *Will replace the effect of {replaced_card["name"]} (Pick #{replaced_pick["pick_number"]})*'
                    elif replaced_pick is None and card[8] > 0:  #if character card
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

                        if len(party_cards) >= party_size and len(party_cards) > 0:
                            replaced_card_id = party_cards[-party_size]

                            await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND isremoved = 0 AND "
                                "card_id = ? ORDER BY pick_number DESC LIMIT 1",
                                (this_draft['id'],replaced_card_id))
                            replaced_pick = await curs.fetchone()
                            await curs.execute("SELECT * FROM cards WHERE id = ?", (replaced_pick['card_id'],))
                            replaced_card = await curs.fetchone()
                            replacement_note = f'\n\n**NOTE:** *Will replace the effect of {replaced_card["name"]} (Pick #{replaced_pick["pick_number"]})*'
                    '''else:
                        if card['character'] == 1:
                            #figure out how many characters are
                            async with asqlite.connect(path) as conn:
                                async with conn.cursor() as curs:
                                    query = (f"SELECT * FROM picks WHERE card_id IN (27, 28) AND draft_id = ? AND isremoved = 0 "
                                             f"ORDER BY pick_number DESC LIMIT 1",(this_draft['id'],))
                                    await curs.execute(query)
                                    party_size_card = await curs.fetchone()
            
                            party_size = 3
                            if party_size_card:
                                if party_size_card['card_id'] == 27:
                                    party_size = 2
                                elif party_size_card['card_id'] == 28:
                                    party_size = 4
            
                            # build a list of all party member cards
                            print(f'The cards in this draft are: {cards}')
                            party_cards = []
                            for num in cards_picked:
                                if 1 <= num <= 26:
                                    party_cards.append(num)
                                if 208 <= num <= 231:
                                    party_cards.append(num)
                            print(f'The party-related cards in this draft are: {party_cards}')
            
                            # go through the list of party member cards and remove the older of any conflicting multiples
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
            
                            # drop the earliest drafted cards with conflicts if we have too many party cards
                            if len(party_cards) > party_size:
                                party_cards = party_cards[(len(party_cards) - party_size):]
            
                            #ignore if the current card is a duplicate of one of these cards
                            if card['id'] not in party_cards:'''

        card_text = card[5] + replacement_note
        card_embed = discord.Embed(title=card[4],
                                   color=card_color,
                                   description=card_text)
        # card_embed.set_footer(text='-flagstring stuff here?')
        card_embed.add_field(name='Category', value=card[1])
        card_embed.add_field(name='Rarity', value=card[2])
        embed.append(card_embed)

        new_button = CardButton(label=card[4])
        view.add_item(new_button)

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            query = (this_draft['id'], current_drafter['index_id'])
            await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND drafter_id = ? and mulligans > 0",
                               query)  #grab how many mulligans used by this drafter
            mulls_this_draft = len(await curs.fetchall())

    if this_draft['mulligan'] == 'topdeck' or (this_draft['mulligan'] == 'paris' and mulls_remaining == 2):
        mulligan_button = CardButton(label="Random Card")
        view.add_item(mulligan_button)
    elif this_draft['mulligan'] == 'paris' and mulls_remaining > 2:
        mulligan_button = CardButton(label=f"Draw {mulls_remaining-1} New Cards")
        view.add_item(mulligan_button)
    elif this_draft['mulligan'] == 'once_per_draft' and mulls_this_draft == 0:
        mulligan_button = CardButton(label=f"Draw {mulls_remaining} New Cards")
        view.add_item(mulligan_button)

    await interaction.response.send_message(
        content=f"Pick #{current_pick['pick_number']} of {this_draft['total_picks']}: "
                f"**{interaction.user.display_name}**, please select one of these cards:",
        embeds=embed, view=view)
    await view.wait()

    if view.chosencard is not None:
        #check if this is an attempted overwrite
        chosen_card_name = view.chosencard
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND pick_number = ? LIMIT 1",
                                   (this_draft['id'],current_pick['pick_number']))
                current_pick_redux = await curs.fetchone()
        if current_pick_redux['card_id'] is not None:
            await interaction.followup.send(content='A card has already been chosen for that pick.', ephemeral=True)
            return None

        # resolve mulligans
        if view.chosencard.startswith('Draw') and view.chosencard.endswith('New Cards'):
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute(
                        "UPDATE picks SET pick_options = NULL, mulligans = COALESCE(mulligans, 0) + 1 WHERE index_id = ?",
                        (current_pick['index_id'],)
                    )
            # adjust mulligan display count for paris
            if this_draft['mulligan'] == 'paris':
                mulls_remaining -= 1
            await interaction.followup.send(f'**{interaction.user.display_name}** has chosen to **mulligan**.\n'
                                            f'These cards have been shuffled back into the deck, and {mulls_remaining} new cards will be drawn.')
            await channel.send(f'**{interaction.user.display_name}**, please make your pick using the `/draftpick` command.')
            return None
            # MULLIGAN PARIS HERE
        elif view.chosencard == 'Random Card':
            new_card = random.choices(pickable_cards, weights=([int(i[3]) for i in pickable_cards]))[0]
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute("""SELECT * FROM cards WHERE name = ?""",(new_card['name'],))
                    chosen_card_data = await curs.fetchone()
                    await curs.execute(
                        "UPDATE picks SET mulligans = COALESCE(mulligans, 0) + 1 WHERE index_id = ?",
                        (current_pick['index_id'],)
                    )
            new_pick_data = (new_card['id'], current_pick['index_id'])
            await channel.send(
                f'For Pick #{current_pick["pick_number"]}, **{interaction.user.display_name}** is drawing a random '
                f'card from the top of the deck!')
            await asyncio.sleep(1)
            chosen_card_name = new_card['name']

            await channel.send(f'For Pick #{current_pick["pick_number"]}, **{interaction.user.display_name}** '
                               f'has selected **{chosen_card_name}**!')
        else:
            await channel.send(f'For Pick #{current_pick["pick_number"]}, **{interaction.user.display_name}** '
                               f'has selected **{chosen_card_name}**!')

            if view.chosencard == 'Calmness':
                chosen_card_id = 0
                new_pick_data = (0, current_pick['index_id'])
                #grab all previous cards
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        await curs.execute("""SELECT * FROM picks WHERE draft_id = ? AND card_id IS NOT NULL AND isremoved = 0""",
                                           (this_draft['id'],))
                        # card_list = [row['card_id'] for row in await curs.fetchall()]
                        all_picks = await curs.fetchall()
                        # await curs.execute()
                card_list = [x['card_id'] for x in all_picks]
                view = CalmnessView(card_data,all_picks,interaction.user)

                await channel.send(content=None, view=view)
                await view.wait()
                if view.value is not None:
                    calmness_card_id = [x['card_id'] for x in all_picks if x['pick_number'] == view.value]
                    calmness_card_name = [x['name'] for x in card_data if x['id'] == calmness_card_id[0]]
                    async with asqlite.connect(path) as conn:
                        async with conn.cursor() as curs:
                            await curs.execute("""UPDATE picks SET isremoved = 1 WHERE pick_number = ? AND draft_id = ?""",
                                               (view.value,this_draft['id']))
                            await conn.commit()
                    remove_query = (view.value, current_pick['index_id'])
                    async with asqlite.connect(path) as conn:
                        async with conn.cursor() as curs:
                            await curs.execute("""UPDATE picks SET removed_card = ? WHERE index_id = ?""",
                                               remove_query)
                            await conn.commit()
                    await channel.send(f'**{calmness_card_name[0]}** has been removed from the drafted cards.')
            else:
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        await curs.execute("""SELECT * FROM cards WHERE name = ?""",(view.chosencard,))
                        chosen_card_data = await curs.fetchone()
                chosen_card_id = chosen_card_data['id']
                new_pick_data = (chosen_card_id, current_pick['index_id'])

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""UPDATE picks SET card_id = ?, isremoved = 0 WHERE index_id = ?""", new_pick_data)
            await conn.commit()

    #announce the next drafter
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND card_id IS NULL LIMIT 1", (this_draft['id'],))
            current_pick = await curs.fetchone()

    if current_pick is not None:
    #see if they're a bot
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM drafters WHERE index_id = ?", (current_pick['drafter_id'],))
                current_drafter = await curs.fetchone()

        while (current_drafter['persona'] is not None) and (current_pick is not None):
            await botpick(channel)
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND card_id IS NULL LIMIT 1", (this_draft['id'],))
                    current_pick = await curs.fetchone()

                    if current_pick is not None:
                        async with asqlite.connect(path) as conn:
                            async with conn.cursor() as curs:
                                await curs.execute("SELECT * FROM drafters WHERE index_id = ?", (current_pick['drafter_id'],))
                                current_drafter = await curs.fetchone()

    if current_pick is not None:
        query = (current_pick['drafter_id'],this_draft['id'])
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM drafters WHERE index_id = ? AND draft_id =?", query)
                current_drafter = await curs.fetchone()

    if current_pick == None:
        #fetch the cards in the draft
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""SELECT card_id FROM picks WHERE draft_id = ? AND isremoved = 0""", (this_draft['id'],))
                #card_list = [row['card_id'] for row in await curs.fetchall()]
                all_picks = await curs.fetchall()
                card_list = [x['card_id'] for x in all_picks]
        flagstring = await createflags(interaction,card_list)

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

        closing_message = f'The draft has ended!\n'
        closing_message += f'This flagset is estimated to be **{diff_rating}**.'
        await channel.send(closing_message)

        finish_query = (datetime.datetime.now(),flagstring, channel.name)
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""UPDATE drafts SET date_finished = ?, flagstring = ? WHERE raceroom = ?""", finish_query)
                await conn.commit()
        await channel.send(f'The flagstring for this draft is:\n```{flagstring}```')
        return False
    else:
        next_up = interaction.guild.get_member(current_drafter["user_id"])
        await channel.send(f'The next drafter is **{next_up.display_name}**!\n'
                           f'{next_up.mention}, please make your pick using the `/draftpick` command.')
        return False