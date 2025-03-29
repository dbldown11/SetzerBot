# import csv
import random
import datetime

import asqlite
import os

import discord

from classes.buttons import CardButton, CardView
from classes.calmness import CalmnessView
from commands.createflags import createflags
from functions.stringfunctions import int_list_to_string,string_to_int_list
from functions.get_difficulty_rating import get_difficulty_rating
from functions.botdraftpick import botpick

from functions.constants import DATA_PATH


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
            data = await curs.fetchone()
            # remember: data is a Rows, not a list

    if data == None:
        emessage = f'No draft has been started for this raceroom.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    if data['date_started'] == None:
        emessage = f'The draft has not begun yet, please wait for the draft creator to start the draft.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    else:
        current_draft_id = data['id']
        if not data['date_finished'] == None:
            emessage = f'This draft has already finished.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafters WHERE draft_id = ? AND user_id = ?", (data['id'],interaction.user.id))
            current_drafter = await curs.fetchone()

    if current_drafter == None:
        emessage = f'You are not a member of this draft.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND card_id IS NULL LIMIT 1", (data['id'],))
            current_pick = await curs.fetchone()
            if current_pick == None:
                print('current pick is none')

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM cards""")
            card_data = await curs.fetchall()
            # remember: card_data is a list of Rows, not a list of lists
            #await curs.close()

    if current_pick['pick_number'] > 1:
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND pick_number = ?", (data['id'],current_pick['pick_number']-1))
                last_pick = await curs.fetchone()
        if last_pick['card_id'] == 0 and last_pick['removed_card'] == 0:
            emessage = f'Please wait until the previous drafter has chosen their Calmness target.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    if current_pick['drafter_id'] != current_drafter['index_id']:
        query = (current_pick['drafter_id'], data['id'])
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM drafters WHERE index_id = ? AND draft_id =?", query)
                new_current_drafter = await curs.fetchone()
        new_current_drafter_name = interaction.guild.get_member(new_current_drafter['user_id'])
        emessage = f"It's not your turn to pick! The current drafter is **{new_current_drafter_name.display_name}**"
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    cards = []
    if current_pick['pick_options'] is not None:
        for y in await string_to_int_list(current_pick['pick_options']):
            #print(f'looking for card {y}')
            if y == 0:
                cards.append([0, 'Special', 'Special', '4', 'Calmness', 'Remove a previously selected card from this seed '
                                                                  '(please indicate which card in chat)'])
            else:
                #print('adding a card')
                #print(card_data)
                cards.append([new_card for new_card in card_data if new_card[0] == y][0])
                #print(cards)
    else:
        weights = ([i[3] for i in card_data])
        has_drawn_removal = False
        pick_list = []
        while len(cards) < data['cards_per_pick']:
            current_categories = [i[1] for i in cards]
            new_card = random.choices(card_data, weights=([int(i[3]) for i in card_data]))[0]
            # if has_drawn_removal == False and new_card[4] == '4' and random.random() < 0.1:
            if has_drawn_removal == False and random.random() < 0.05 and current_pick['pick_number'] > 1:
                new_card = [0, 'Special', 'Special', '4', 'Calmness', 'Remove a previously selected card from this seed']
                has_drawn_removal = True
                pick_list.append(new_card[0])
            if len(current_categories) == 0:
                cards.append(new_card)
                pick_list.append(new_card[0])
            elif new_card[1] not in current_categories:
                cards.append(new_card)
                pick_list.append(new_card[0])

        pick_options_query = await int_list_to_string(pick_list)


        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""UPDATE picks SET pick_options = ? WHERE index_id = ?""",
                                   (pick_options_query,current_pick['index_id']))
    embed = []
    button = []
    
    view = CardView(interaction.user)
    for x in cards:
        #print(f'Option {num+1}: {x}')
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

        new_button = CardButton(label=x[4])
        view.add_item(new_button)

    await interaction.response.send_message(content=f"**{interaction.user.display_name}**, please select one of these cards:",
                                            embeds=embed, view=view)
    await view.wait()



    if view.chosencard is not None:
        #check if this is an attempted overwrite

        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND pick_number = ? LIMIT 1",
                                   (data['id'],current_pick['pick_number']))
                current_pick_redux = await curs.fetchone()
        #print(current_pick_redux['card_id'])
        if current_pick_redux['card_id'] is not None:
            await interaction.followup.send(content='A card has already been chosen for that pick.', ephemeral=True)
            return None

        await channel.send(f'**{interaction.user.display_name}** has selected **{view.chosencard}**!')
        if view.chosencard == 'Calmness':
            chosen_card_id = 0
            new_pick_data = (0, current_pick['index_id'])
            #grab all previous cards
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute("""SELECT * FROM picks WHERE draft_id = ? AND card_id IS NOT NULL AND isremoved = 0""",
                                       (data['id'],))
                    # card_list = [row['card_id'] for row in await curs.fetchall()]
                    all_picks = await curs.fetchall()
            card_list = [x['card_id'] for x in all_picks]
            view = CalmnessView(card_data,all_picks,interaction.user)

            await channel.send(content=None, view=view)
            await view.wait()
            if view.value is not None:
                #print(f'you got rid of {view.value}')
                #print(type(view.value))
                #print(all_picks)
                calmness_card_id = [x['card_id'] for x in all_picks if x['pick_number'] == view.value]
                #print(calmness_card_id)
                calmness_card_name = [x['name'] for x in card_data if x['id'] == calmness_card_id[0]]
                #print(calmness_card_name)
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        await curs.execute("""UPDATE picks SET isremoved = 1 WHERE pick_number = ? AND draft_id = ?""",
                                           (view.value,data['id']))
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
            await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND card_id IS NULL LIMIT 1", (data['id'],))
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
                    await curs.execute("SELECT * FROM picks WHERE draft_id = ? AND card_id IS NULL LIMIT 1", (data['id'],))
                    current_pick = await curs.fetchone()

                    if current_pick is not None:
                        async with asqlite.connect(path) as conn:
                            async with conn.cursor() as curs:
                                await curs.execute("SELECT * FROM drafters WHERE index_id = ?", (current_pick['drafter_id'],))
                                current_drafter = await curs.fetchone()

    if current_pick is not None:
        query = (current_pick['drafter_id'],data['id'])
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM drafters WHERE index_id = ? AND draft_id =?", query)
                current_drafter = await curs.fetchone()

    if current_pick == None:
        #fetch the cards in the draft
        #print(f'going to pull all the cards from draft_id {data["id"]}')
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""SELECT card_id FROM picks WHERE draft_id = ? AND isremoved = 0""", (data['id'],))
                #card_list = [row['card_id'] for row in await curs.fetchall()]
                all_picks = await curs.fetchall()
                card_list = [x['card_id'] for x in all_picks]
                #print(f'the card_list i pulled from the db is {card_list}')
        flagstring = await createflags(interaction,card_list)

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

        closing_message = f'The draft has ended!\n'
        closing_message += f'This flagset is estimated to be **{diff_rating}**.'
        await channel.send(closing_message)

        finish_query = (datetime.datetime.now(),flagstring, channel.name)
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""UPDATE drafts SET date_finished = ?, flagstring = ? WHERE raceroom = ?""", finish_query)
                await conn.commit()
        await channel.send(f'The flagstring for this draft is:\n```{flagstring}```')
        return None
    else:
        next_up = interaction.guild.get_member(current_drafter["user_id"])
        await channel.send(f'The next drafter is **{next_up.display_name}**!\n'
                           f'{next_up.mention}, please make your pick using the `/draftpick` command.')