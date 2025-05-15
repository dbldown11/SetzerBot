import discord
import asqlite
import os
import random
from itertools import chain

from commands.addbotdrafter import addbotdrafter
from commands.showoptions import showoptions
from functions.constants import DATA_PATH
from functions.stringfunctions import int_list_to_string

async def newdraft(interaction, args) -> dict:
    """
    Creates a new draft based in the channel the command is called in

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    args : dict
        A dictionary containing the args for the draft
        ex: {'arg':'argvalue'}
        default values:
            'drafters': 4
            'picks': 10
            'cards' : 3
            'order': 'round'
            'card_removal': 'never'
            'calmness': 'uncommon'
            'bots' : 0}

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'draftdata.db')

    channel = interaction.channel
    if channel.type == discord.ChannelType.private:
        channel_name = 'DM'
    elif not channel.name.startswith(('ff6wc-', 'ff6wcdraft-', 'draft-')):
        emessage = f'Drafts can only be created in a raceroom.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    else:
        channel_name = channel.name

    #check if this raceroom already has a draft
    #TODO if DM, check if a solodraft is also ongoing
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafts WHERE raceroom = ?",(channel_name,))
            data = await curs.fetchone()
            # remember: data is a list of Rows, not a list of lists
            if not data == None:
                draft_creator = interaction.guild.get_member(data[2])
                emessage = f'Unable to start a new draft as a draft has already been created for this raceroom by {draft_creator}'
                await interaction.response.send_message(emessage, ephemeral=True)
                return None

    print(f'Creating a new race with {args}')

    #randomly choose any random args
    if args["card_removal"] == 'random':
        args['card_removal'] = random.choice(['never','on_pick','on_draw'])
    if args['calmness'] == 'random':
        args['calmness'] = random.choice(['uncommon','rare','every_pick','once_per_draft','none'])
    if args['rarity'] == 'random':
        args['rarity'] = random.choice(['default','ignore','double','packs'])
    if args['categories'] == 'random':
        args['categories'] = random.choice(['default','ignore'])
    if args['mulligan'] == 'random':
        args['mulligan'] = random.choice(['none','one_per_draft','paris','topdeck'])
    if args['character_cards'] == 'random':
        args['character_cards'] = random.choice(['all','one_per_character','vanilla','vanilla_plus_one'])

    #do checks on AI drafters
    if args["bots"] > (args["drafters"] - 1):
        emessage = f'Too many bot drafters selected to create draft; drafts require at least one human drafter.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #determine which character_cards to remove
    # list 0 will always be vanilla
    character_card_sets = [
        [1,2,3,4,5,6,7,8,9,10,11,12,13,14],
        [15,16,17,18,19,20,21,22,23,24,25,26],
        [208,209,210,211,212,213,214,215,216,217,218,219],
        [220,221,222,223,224,225,226,227,228,229,230,231]
    ]
    banned_cards = []

    if args['character_cards'] == 'vanilla':
        banned_cards = [card for sublist in character_card_sets[1:] for card in sublist]
    elif args['character_cards'] == 'vanilla_plus_one':
        # Choose one random list to skip (from index 1 onward)
        skipped_index = random.randrange(1, len(character_card_sets))

        # Include the first list, and all others except the randomly skipped one
        banned_cards = list(chain.from_iterable(
            sublist for i, sublist in enumerate(character_card_sets) if i == 0 or i != skipped_index
        ))
    elif args['character_cards'] == 'one_per_character':
        for i in range(14):
            ith_elements = [lst[i] for lst in character_card_sets if i < len(lst)]

            if len(ith_elements) > 1:
                to_exclude = random.choice(ith_elements)
                ith_elements.remove(to_exclude)

            banned_cards.extend(ith_elements)
    elif args['character_cards'] == 'none':
        banned_cards = sum(character_card_sets, [])

    banned_cards = await int_list_to_string(banned_cards)
    if len(banned_cards) == 0:
        banned_cards = None
    #create the draft
    if channel.type == discord.ChannelType.private:
        guild_id = None
    else:
        guild_id = interaction.guild.id
    data = (guild_id, interaction.user.id, args['drafters'], args['picks'], args['cards'], args['order'],
            args['card_removal'], args['calmness'], args['rarity'], args['categories'], args['mulligan'],
            args['character_cards'], channel_name, banned_cards)
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("""INSERT INTO drafts (guild_id, creator_id, max_drafters, total_picks, cards_per_pick, 
            draft_order, card_removal, calmness, rarity, categories, mulligan, character_cards, raceroom, banned_cards) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                               data)
            await conn.commit()

    await interaction.response.send_message(
            f'A draft has been set up for this race by {interaction.user.display_name}! '
            f'Up to {args["drafters"]-args["bots"]} players can join. '
            f'Use `/joindraft` to join the draft.')

    await showoptions(interaction)

    bots_added = 0
    while bots_added < args["bots"]:
        await addbotdrafter(interaction)
        bots_added += 1

    return