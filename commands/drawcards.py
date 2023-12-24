#import csv
import random
import sqlite3

import asqlite
import os

import discord

from classes.buttons import CardButton, CardView

from functions.constants import DATA_PATH

async def drawcards(interaction):

    '''
    with open('data.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    path = os.path.join(DATA_PATH, 'draftdata.db')
    conn = asqlite.connect(path)
    conn.row_factory = asqlite.Row
    curs = conn.cursor()
    curs.execute("""SELECT * FROM cards""")
    rows = curs.fetchall()
    curs.close()
    '''
    #load cards from the db
    data = []

    path = os.path.join(DATA_PATH, 'draftdata.db')
    async with asqlite.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("""SELECT * FROM cards""")
            data = await curs.fetchall()
            # remember: data is a list of Rows, not a list of lists
            await curs.close()

    weights = ([i[3] for i in data])
    cards = []
    has_drawn_removal = False
    while len(cards) < 3:
        current_categories = [i[1] for i in cards]
        new_card = random.choices(data, weights = ([int(i[3]) for i in data]))[0]
        #if has_drawn_removal == False and new_card[4] == '4' and random.random() < 0.1:
        if has_drawn_removal == False and random.random() < 0.05:
            new_card = [0,'Special','Special','4','Calmness','Remove a previously selected card from this seed '
                                                           '(please indicate which card in chat)']
            has_drawn_removal = True
        if len(current_categories) == 0:
            cards.append(new_card)
        elif new_card[1] not in current_categories:
            cards.append(new_card)

    #build the card selection view
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
        card_embed = discord.Embed(title = x[4],
                                   color = card_color,
                                   description = x[5])
        #card_embed.set_footer(text='-flagstring stuff here?')
        card_embed.add_field(name='Category', value=x[1])
        card_embed.add_field(name='Rarity', value=x[2])
        embed.append(card_embed)

        new_button = CardButton(label=x[4])
        view.add_item(new_button)

    await interaction.response.send_message(content=f"**{interaction.user.display_name}**, please select one of these cards:",
                                            embeds = embed, view=view)
    await view.wait()
    print(view.chosencard)