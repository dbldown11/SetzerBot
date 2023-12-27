import discord
import asqlite
import os

from commands.addbotdrafter import addbotdrafter
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
            'order': 'round'
            'bots' : 0}

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'draftdata.db')

    channel = interaction.channel
    if channel.type == discord.ChannelType.private:
        channel_name = 'DM'
    elif not channel.name.startswith('ff6wc-') and not channel.name.startswith('ff6wcdraft-'):
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

    #do checks on AI drafters
    if args["bots"] > (args["drafters"] - 1):
        emessage = f'Too many bot drafters selected to create draft; drafts require at least one human drafter.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    #create the draft
    if channel.type == discord.ChannelType.private:
        guild_id = None
    else:
        guild_id = interaction.guild.id
    data = (guild_id, interaction.user.id, args['drafters'], args['picks'], args['cards'], args['order'], channel_name)
    async with asqlite.connect(path) as conn:
        #conn.row_factory = sqlite3.Row
        async with conn.cursor() as curs:
            await curs.execute("""INSERT INTO drafts (guild_id, creator_id, max_drafters, total_picks, cards_per_pick, 
            draft_order, raceroom) VALUES (?, ?, ?, ?, ?, ?, ?);""", data)
            await conn.commit()

    bots_added = 0
    while bots_added < args["bots"]:
        await addbotdrafter(interaction)
        bots_added += 1

    await interaction.response.send_message(f'A draft has been set up for this race by {interaction.user.display_name}! Up to {args["drafters"]-args["bots"]} players can join. Use `/joindraft` to join the draft.')
    return