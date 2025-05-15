import discord
import asqlite
import os
import random
from itertools import chain

from commands.addbotdrafter import addbotdrafter
from functions.constants import DATA_PATH
from functions.stringfunctions import int_list_to_string

async def draftoptions(interaction, args):
    """
    Changes one or more parameters for a new, unstarted draft based in the channel the command is called in

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    args : dict
        A dictionary containing the args for the draft
        ex: {'arg':'argvalue'}
        default values:
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

    # check if this raceroom already has a draft and if the draft has already started
    async with asqlite.connect(path) as conn:
        # conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafts WHERE raceroom = ?", (channel.name,))
            this_draft = await curs.fetchone()
            # remember: data is a Rows, not a list

    if this_draft == None:
        emessage = f'No draft has been started for this raceroom - use the `/newdraft` command to start a draft first.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    else:
        if not this_draft['date_started'] == None:
            emessage = (f'This draft has already started, options can no longer be adjusted. '
                        f'Use the `/canceldraft` if you would like to restart and set new options.')
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

        if str(interaction.user.id) != str(this_draft['creator_id']):
            emessage = f'Only the draft creator can edit the draft options.'
            await interaction.response.send_message(emessage, ephemeral=True)
            return None

    #populate as needed
    picks = args.get('picks',this_draft['total_picks'])
    cards = args.get('cards',this_draft['cards_per_pick'])
    order = args.get('order',this_draft['draft_order'])
    card_removal = args.get('card_removal',this_draft['card_removal'])
    calmness = args.get('calmness',this_draft['calmness'])
    rarity = args.get('rarity',this_draft['rarity'])
    categories = args.get('categories',this_draft['categories'])
    mulligan = args.get('mulligan',this_draft['mulligan'])
    character_cards = args.get('character_cards',this_draft['character_cards'])

    # determine which character_cards to remove
    # list 0 will always be vanilla
    character_card_sets = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
        [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
        [208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219],
        [220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231]
    ]
    banned_cards = []

    if character_cards == 'vanilla':
        banned_cards = [card for sublist in character_card_sets[1:] for card in sublist]
    elif character_cards == 'vanilla_plus_one':
        # Choose one random list to skip (from index 1 onward)
        skipped_index = random.randrange(1, len(character_card_sets))

        # Include the first list, and all others except the randomly skipped one
        banned_cards = list(chain.from_iterable(
            sublist for i, sublist in enumerate(character_card_sets) if i == 0 or i != skipped_index
        ))
    elif character_cards == 'one_per_character':
        for i in range(14):
            ith_elements = [lst[i] for lst in character_card_sets if i < len(lst)]

            if len(ith_elements) > 1:
                to_exclude = random.choice(ith_elements)
                ith_elements.remove(to_exclude)

            banned_cards.extend(ith_elements)
    elif character_cards == 'none':
        banned_cards = sum(character_card_sets, [])

    #randomly choose any random args
    if card_removal == 'random':
        card_removal = random.choice(['never', 'on_pick', 'on_draw'])
    if calmness == 'random':
        calmness = random.choice(['uncommon', 'rare', 'every_pick', 'once_per_draft', 'none'])
    if rarity == 'random':
        rarity = random.choice(['default', 'ignore', 'double', 'packs'])
    if categories == 'random':
        categories = random.choice(['default', 'ignore'])
    if mulligan == 'random':
        mulligan = random.choice(['none', 'one_per_draft', 'paris', 'topdeck'])
    if character_cards == 'random':
        character_cards = random.choice(['all', 'one_per_character', 'vanilla', 'vanilla_plus_one'])

    banned_cards = await int_list_to_string(banned_cards)
    if len(banned_cards) == 0:
        banned_cards = None

    data = (picks,cards,order,card_removal,calmness,rarity,categories,mulligan,character_cards,banned_cards,this_draft['id'])
    async with asqlite.connect(path) as conn:
        # conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute(
                """UPDATE drafts SET total_picks = ?, cards_per_pick = ?, draft_order = ?, card_removal = ?, 
                calmness = ?, rarity = ?, categories = ?, mulligan = ?, character_cards = ?, banned_cards = ? 
                WHERE id = ?""",
                data)
            await conn.commit()

    pretty_names = {
        'picks': 'Total picks',
        'cards': 'Cards per Pick',
        'order': 'Draft Order',
        'card_removal': 'Card Removal',
        'calmness': 'Calmness Frequency',
        'rarity': 'Card Rarity Mode',
        'categories': 'Card Categories',
        'mulligan': 'Mulligan Style',
        'character_cards': 'Character Card Sets',
    }

    if args:
        messages = [f"**{pretty_names.get(k, k.title())}** has been set to **{v}**" for k, v in args.items()]
        await interaction.response.send_message("\n".join(messages))
    else:
        await interaction.response.send_message("No draft options changed.", ephemeral=True)