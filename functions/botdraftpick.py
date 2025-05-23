# import csv
import asyncio
import os
import random

import asqlite
import discord

from classes.buttons import CardView
from functions.constants import DATA_PATH, COMMON, UNCOMMON, RARE, MYTHIC
from functions.stringfunctions import int_list_to_string, string_to_int_list
from functions.get_card_list_by_rarity import get_card_list_by_rarity


async def botpick(channel):
    """
    Chooses a card for an active draft

    Parameters
    ----------
    channel : discord.Channel
        The channel for the raceroom being drafted in

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'draftdata.db')

    async with asqlite.connect(path) as conn:
        # conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafts WHERE raceroom = ?", (channel.name,))
            this_draft = await curs.fetchone()

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND card_id IS NULL LIMIT 1", (this_draft['id'],))
            current_pick = await curs.fetchone()
            if current_pick is None:
                print('current pick is none')

    #get persona info
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE index_id = ?", (current_pick['drafter_id'],))
            current_drafter = await curs.fetchone()
            await curs.execute("SELECT * FROM personas WHERE id = ?", (current_drafter['persona'],))
            current_persona = await curs.fetchone()

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM cards""")
            card_data = await curs.fetchall()
            # remember: card_data is a list of Rows, not a list of lists

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            if this_draft['card_removal'] == 'on_pick':
                await curs.execute("SELECT card_id FROM picks WHERE draft_id = ? and card_id IS NOT NULL", (this_draft['id'],))
                rows = await curs.fetchall()
                cards_picked = [row[0] for row in rows]
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
                if len(cards_drawn) > 180:
                    pickable_cards = card_data
                else:
                    pickable_cards = [card for card in card_data if card['id'] not in cards_drawn]
            else:
                pickable_cards = card_data

    # Remove unused character_cards
    if this_draft['banned_cards'] is not None:
        char_cards_to_remove = await string_to_int_list(this_draft['banned_cards'])
        pickable_cards = [card for card in pickable_cards if card['id'] not in char_cards_to_remove]

    cards = []
    if current_pick['pick_options'] is not None:
        #this should never trigger unless there was a very strangely timed disconnect
        for y in await string_to_int_list(current_pick['pick_options']):
            # print(f'looking for card {y}')
            if y == 0:
                cards.append(
                    [0, 'Special', 'Special', '4', 'Calmness', 'Remove a previously selected card from this seed '
                                                               '(please indicate which card in chat)'])
            else:
                # print('adding a card')
                # print(card_data)
                cards.append([new_card for new_card in card_data if new_card[0] == y][0])
                # print(cards)
    else:
        # weights = ([i[3] for i in card_data])
        # has_drawn_removal = False
        '''pick_list = []
        while len(cards) < this_draft['cards_per_pick']:
            current_categories = [i[1] for i in cards]
            new_card = random.choices(pickable_cards, weights=([int(i[3]) for i in pickable_cards]))[0]
            # if has_drawn_removal == False and new_card[4] == '4' and random.random() < 0.1:
            '''
        '''if has_drawn_removal == False and random.random() < 0.05 and current_pick['pick_number'] > 1:
            new_card = [0, 'Special', 'Special', '4', 'Calmness',
                        'Remove a previously selected card from this seed']
            has_drawn_removal = True
            pick_list.append(new_card[0])'''


        cards_to_draw = this_draft['cards_per_pick']
        pick_list = []
        while len(cards) < cards_to_draw:
            current_categories = [i[1] for i in cards]
            if this_draft['rarity'] == 'double':
                new_card = random.choices(pickable_cards, weights=([int(i[3]) * 2 for i in pickable_cards]))[0]
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



            if len(current_categories) == 0:
                cards.append(new_card)
                pick_list.append(new_card[0])
            elif this_draft['categories'] == 'ignore':
                cards.append(new_card)
                pick_list.append(new_card[0])
            elif new_card[1] not in current_categories:
                cards.append(new_card)
                pick_list.append(new_card[0])

        pick_options_query = await int_list_to_string(pick_list)

        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""UPDATE picks SET pick_options = ? WHERE index_id = ?""",
                                   (pick_options_query, current_pick['index_id']))
    embed = []
    # button = []

    view = CardView(None) #this might not work, it's looking for an interaction here
    for x in cards:
        # print(f'Option {num+1}: {x}')
        if x[0] == 0:
            card_color = discord.Color.from_str('0x23272A')
        elif x[2] == 'Common':
            card_color = discord.Color.lighter_gray()
        elif x[2] == 'Uncommon':
            card_color = discord.Color.green()
        elif x[2] == 'Rare':
            card_color = discord.Color.blue()
        else:
            card_color = discord.Color.gold()
        card_embed = discord.Embed(title=x[4],
                                   color=card_color,
                                   description=x[5])
        # card_embed.set_footer(text='-flagstring stuff here?')
        card_embed.add_field(name='Category', value=x[1])
        card_embed.add_field(name='Rarity', value=x[2])
        embed.append(card_embed)

        #new_button = CardButton(label=x[4])
        #view.add_item(new_button)

    await channel.send(
        content=f"**{current_persona['name']} (Bot)** is choosing from one of these cards...",
        embeds=embed, view=view)

    # 1 second pause for effect
    await asyncio.sleep(1)

    # AI Picking logic here!
    # Step 0 - get the persona's favourites and diff skew
    fav_cards = await string_to_int_list(current_persona['fav_cards'])
    potential_picks = []
    final_pick = None

    # Step 1 - look for favourite char cards
    for x in cards:
        if (x['id'] <= 26 or 208 <= x['id'] <= 231) and x['id'] in fav_cards:
            print(f'{current_persona["name"]} found {x["name"]} in Step 1 and added to their picklist')
            potential_picks.append(x)

    if len(potential_picks) > 0:
        final_pick = random.choice(potential_picks)
        await channel.send(f'**{current_persona["name"]} (Bot):** {current_persona["fav_quote"]}')
        # 2 second pause for effect
        await asyncio.sleep(3)

    # Step 2 - if nothing yet, look for favourite non-char cards
    if final_pick is None:
        for x in cards:
            if 26 < x['id'] < 208 and x['id'] in fav_cards:
                print(f'{current_persona["name"]} found {x["name"]} in Step 2 and added to their picklist')
                potential_picks.append(x)

        if len(potential_picks) > 0:
            final_pick = random.choice(potential_picks)
            await channel.send(f'**{current_persona["name"]} (Bot):** {current_persona["fav_quote"]}')
            # 2 second pause for effect
            await asyncio.sleep(3)

    #Step 3 - if nothing yet, pick according to rarity bias and difficulty skew
    #yeti mode
    if final_pick is None:
        if current_persona['bias'] == 'random':
            final_pick =  random.choice(cards)

        else:
            # Define difficulty order based on persona's bias
            difficulty_order = {'hard': [2, 1, 0, -1, -2], 'medium': [0, -1, 1, -2, 2], 'easy': [-2, -1, 0, 1, 2]}[
                current_persona['bias']]

            # Sort the cards based on the persona's biases and shuffle cards with equal weight
            print(f"{current_persona['name']}'s rarity bias is {current_persona['rarity_bias']}")
            sorted_cards = sorted(cards, key=lambda card: (
                card['rarity'] if current_persona['rarity_bias'] == 1 else 0,
                difficulty_order.index(card['difficulty']),
                card['difficulty']
            ))

            print(f'{current_persona["name"]} has prioritized their picks in this order:')
            for x in sorted_cards:
                # 1 second pause for effect
                await asyncio.sleep(1)
                print(f'{x["name"]}, with rarity {x["rarity"]} and difficulty {x["difficulty"]}')
            # Select the first card with the highest priority (deterministic selection)
            final_pick = next(
                (card for card in sorted_cards if card['rarity'] == sorted_cards[0]['rarity']),
                None
            )

            # If there are multiple top-priority cards with the same difficulty, randomly choose one
            if final_pick:
                top_priority_cards_same_difficulty = [
                    card for card in sorted_cards if
                    card['rarity'] == sorted_cards[0]['rarity'] and card['difficulty'] == final_pick['difficulty']
                ]
                final_pick = random.choice(top_priority_cards_same_difficulty)

    #record the pick in the dB
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM cards WHERE name = ?""", (final_pick['name'],))
            chosen_card_data = await curs.fetchone()
    chosen_card_id = chosen_card_data['id']
    new_pick_data = (chosen_card_id, current_pick['index_id'])

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""UPDATE picks SET card_id = ?, isremoved = 0 WHERE index_id = ?""", new_pick_data)
            await conn.commit()

    #announce the pick in chat
    await channel.send(f'**{current_persona["name"]} (Bot)** has selected **{final_pick["name"]}**!')
    # 1 second pause for effect
    await asyncio.sleep(1)