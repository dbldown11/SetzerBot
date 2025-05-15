import discord
import asqlite
import os

from functions.constants import DATA_PATH
from functions.get_difficulty_rating import get_difficulty_rating

async def showoptions(interaction) -> None:
    """
    Shows the parameters of the current draft

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the function call

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

    if this_draft == None:
        emessage = f'No draft has been started for this raceroom - use the `/newdraft` command to start a draft first.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    pretty_names = {
        'max_drafters': 'Maximum number of drafters',
        'total_picks': 'Total picks',
        'cards_per_pick': 'Cards per Pick',
        'draft_order': 'Draft Order',
        'card_removal': 'Card Removal',
        'calmness': 'Calmness Frequency',
        'rarity': 'Card Rarity Mode',
        'categories': 'Card Categories',
        'mulligan': 'Mulligan Style',
        'character_cards': 'Character Card Sets',
    }

    draft_list = dict(this_draft)
    messages = [
        f"**{pretty_names.get(k, k.title())}**: {draft_list[k]}"
        for k in pretty_names if k in draft_list
    ]
    message_content = 'The options for this draft are:\n\n' + "\n".join(messages)

    if interaction.response.is_done():
        await channel.send(message_content)
    else:
        await interaction.response.send_message(message_content)