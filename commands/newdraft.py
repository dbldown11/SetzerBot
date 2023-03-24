import discord
import asqlite
import os

from functions.constants import DATA_PATH

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
            'order': 'round'}

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'draftdata.db')

    channel = interaction.channel
    if not channel.name.startswith('ff6wc-') and not channel.name.startswith('ff6wcdraft-'):
        emessage = f'Drafts can only be created in a raceroom.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #check if this raceroom already has a draft
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM drafts WHERE raceroom = ?",(channel.name,))
            data = await curs.fetchone()
            # remember: data is a list of Rows, not a list of lists
            if not data == None:
                draft_creator = interaction.guild.get_member(data[2])
                emessage = f'Unable to start a new draft as a draft has already been created for this raceroom by {draft_creator}'
                await interaction.response.send_message(emessage, ephemeral=True)
                return None

    print(f'Creating a new race with {args}')

    #create the draft
    data = (interaction.guild.id, interaction.user.id, args['drafters'], args['picks'], args['cards'], args['order'], interaction.channel.name)
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("""INSERT INTO drafts (guild_id, creator_id, max_drafters, total_picks, cards_per_pick, 
            draft_order, raceroom) VALUES (?, ?, ?, ?, ?, ?, ?);""", data)
            await conn.commit()

    await interaction.response.send_message(f'A draft has been set up for this race by {interaction.user.display_name}! Up to {args["drafters"]} players can join. Use `/joindraft` to join the draft.')
    return