import random
import datetime

import asqlite
import os

import discord

from classes.buttons import CardButton, CardView
from classes.calmness import CalmnessView
from commands.createflags import createflags
from functions.stringfunctions import int_list_to_string,string_to_int_list

from functions.constants import DATA_PATH


async def br_pick(interaction):
    """
    Chooses a card for the current BR group

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')
    channel = interaction.channel

    #get players, check if this person is one of them
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_players WHERE user_id = ?", (interaction.user.id))
            current_user = await curs.fetchone()

    if current_user is None:
        emessage = f'You are not a participant in the Blackjack Battle Royale.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #confirm if this is the right channel
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_groups WHERE id = ?",(current_user['group_id'],))
            current_group = await curs.fetchone()

    group_channel = discord.utils.get(interaction.guild.text_channels,id=current_group['channel_id'])
    if interaction.channel != group_channel:
        emessage = f'You are not a member of this group, please return to your own table.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #get most recent week
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_group_weeks WHERE week_num = (SELECT MAX(week_num) FROM br_group_weeks)")
            current_weeks = await curs.fetchall()

    if len(current_weeks) == 0:
        emessage = f'The event has not yet started.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    for week in current_weeks:
        if week['group_id'] == current_user['group_id']:
            current_group_week = week

    if current_weeks is None:
        print('your group doesn''t have a week???')
        return None

    #get this user's group's current pick
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM br_picks WHERE week_id = ? AND group_id = ? AND card_id IS NULL LIMIT 1""",
                               (current_group_week['id'],current_user['group_id']))
            current_pick = await curs.fetchone()

    if current_pick is None:
        emessage = f'There are no picks remaining for this group this week.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    if current_pick['pick_number'] > 1:
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM br_picks WHERE group_id = ? AND week_id = ? and pick_number = ?",
                                   (current_group_week['id'],current_group_week['week_id'],current_pick['pick_number']-1))
                last_pick = await curs.fetchone()
        if last_pick['card_id'] == 0 and last_pick['removed_card'] == 0:
            emessage = f'Please wait until the previous drafter has chosen their Calmness target.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    #current_drafter = interaction.guild.get_member(current_pick['user_id'])
    if current_pick['player_id'] != current_user['id']:
        emessage = f'It''s not your turn to pick a card.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    if current_pick['card_id'] is not None:
        emessage = f'A card has already been picked.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #load the cards into the data list
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM br_cards""")
            card_data = await curs.fetchall()

    ######### THIS IS ALL COPY PASTE FROM THE NORMAL DRAFT STUFF ##########

    cards = []
    if current_pick['pick_options'] is not None:
        for y in await string_to_int_list(current_pick['pick_options']):
            if y == 0:
                cards.append([0, 'Special', 'Special', '4', 'Calmness', 'Remove a previously selected card from this seed '
                                                                        '(please indicate which card in chat)'])
            else:
                # print(card_data)
                cards.append([new_card for new_card in card_data if new_card[0] == y][0])
                #print(cards)
    else:

        has_drawn_removal = False
        pick_list = []
        #TODO May need to update this next level for final group selection
        while len(cards) < 3:
            current_categories = [i[1] for i in cards]
            new_card = random.choices(card_data, weights=([int(i[3]) for i in card_data]))[0]
            # if has_drawn_removal == False and new_card[4] == '4' and random.random() < 0.1:
            if has_drawn_removal == False and random.random() < 0.05 and len(cards) > 0:
                new_card = [0, 'Special', 'Special', '4', 'Calmness', 'Remove a previously selected card from this seed']
                has_drawn_removal = True
                pick_list.append(new_card[0])
            elif len(current_categories) == 0:
                cards.append(new_card)
                pick_list.append(new_card[0])
            elif new_card[1] not in current_categories:
                cards.append(new_card)
                pick_list.append(new_card[0])

        pick_options_list = await int_list_to_string(pick_list)

        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""UPDATE br_picks SET pick_options = ? WHERE id = ?""",
                                   (pick_options_list, current_pick['id']))
    embed = []
    button = []
    if len(cards) > 10:
        await interaction.response.defer()
        view = CardView(interaction.user)
        for count, x in enumerate(cards,start=1):
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

            new_button = CardButton(label=x[4])
            view.add_item(new_button)
            if count % 10 == 0:
                await interaction.followup.send(content=f'You have brought the following cards from your table:',embeds=embed)
                embed = []

        if embed != []:
            await interaction.followup.send(content=None, embeds=embed)

        await interaction.followup.send(
            content=f"**{interaction.user.name}**, please select one of these cards:",
            embeds=embed, view=view)
        await view.wait()
    else:
        view = CardView(interaction.user)
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

            new_button = CardButton(label=x[4])
            view.add_item(new_button)

        await interaction.response.send_message(content=f"**{interaction.user.name}**, please select one of these cards:",
                                                embeds=embed, view=view)
        await view.wait()

    if view.chosencard is not None:
        # check if this is an attempted overwrite

        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM br_picks WHERE group_id = ? AND week_id = ? AND pick_number = ? LIMIT 1",
                                   (current_user['group_id'], current_pick['week_id'], current_pick['pick_number']))
                current_pick_redux = await curs.fetchone()
        print(f'current pick redux: {current_pick_redux["card_id"]}')
        if current_pick_redux['card_id'] is not None:
            await interaction.followup.send(content='A card has already been chosen for that pick.', ephemeral=True)
            return None

        await channel.send(f'**{interaction.user.name}** has selected **{view.chosencard}**!')
        if view.chosencard == 'Calmness':
            chosen_card_id = 0
            new_pick_data = (0, current_pick['id'])
            # grab all previous cards
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute(
                        """SELECT * FROM br_picks WHERE group_id = ? AND card_id IS NOT NULL AND isremoved = 0""",
                        (current_user['group_id'],))
                    # card_list = [row['card_id'] for row in await curs.fetchall()]
                    all_picks = await curs.fetchall()
            card_list = [x['card_id'] for x in all_picks]
            view = CalmnessView(card_data, all_picks, interaction.user)

            await channel.send(content=None, view=view)
            await view.wait()
            if view.value is not None:
                print(f'you got rid of {view.value}')
                print(type(view.value))
                print(all_picks)
                calmness_card_id = [x['card_id'] for x in all_picks if x['pick_number'] == view.value]
                print(calmness_card_id)
                calmness_card_name = [x['name'] for x in card_data if x['id'] == calmness_card_id[0]]
                print(calmness_card_name)
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        await curs.execute("""UPDATE br_picks SET isremoved = 1 WHERE pick_number = ? AND group_id = ?""",
                                           (view.value, current_user['group_id']))
                        await conn.commit()
                remove_query = (view.value, current_pick['id'])
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        await curs.execute("""UPDATE picks SET removed_card = ? WHERE index_id = ?""",
                                           remove_query)
                        await conn.commit()
                await channel.send(f'**{calmness_card_name[0]}** has been removed from the drafted cards.')
        else:
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute("""SELECT * FROM br_cards WHERE name = ?""", (view.chosencard,))
                    chosen_card_data = await curs.fetchone()
            chosen_card_id = chosen_card_data['id']
            new_pick_data = (chosen_card_id, current_pick['id'])

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            #print(f'writing this to br_picks for card_id where id is this: {new_pick_data}')
            await curs.execute("""UPDATE br_picks SET card_id = ?, isremoved = 0 WHERE id = ?""", new_pick_data)
            await conn.commit()

    # announce the next drafter
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_picks WHERE week_id = ? AND card_id IS NULL LIMIT 1", (current_group_week['id'],))
            current_pick = await curs.fetchone()
            #print(current_pick)

    if current_pick is not None:
        query = (current_pick['player_id'], current_group['id'])
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM br_players WHERE id = ? AND group_id =?", query)
                current_drafter = await curs.fetchone()
    if current_pick == None:
        await channel.send(f'Picks for this week have been completed!')

        # fetch the cards in the draft
        #print(f'going to pull all the cards from group {data["id"]}')
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""SELECT card_id FROM br_picks WHERE group_id = ? AND isremoved = 0""", (current_group['id'],))
                # card_list = [row['card_id'] for row in await curs.fetchall()]
                all_picks = await curs.fetchall()
                card_list = [x['card_id'] for x in all_picks]

        flagstring = await createflags(interaction, card_list)
        finish_query = (datetime.datetime.now(), flagstring, current_group['id'], current_group_week['week_num'])
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""UPDATE br_group_weeks SET week_picks_ended_date = ?, flagstring = ? WHERE group_id =? AND week_num = ?""",
                                   finish_query)
                await conn.commit()
        await channel.send(f"Here's the flagstring for this group:\n```{flagstring}```")
        return None
    else:
        next_up = interaction.guild.get_member(current_drafter["user_id"])
        await channel.send(f'The next drafter is **{next_up.display_name}**!\n'
                           f'{next_up.mention}, please make your pick using the `/br pick` command.')