import discord
import asqlite
import os

from functions.constants import DATA_PATH

async def showflags(interaction) -> None:
    """
    Shows the flags of a completed draft in the current raceroom

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
    # get the current draft's info from the db
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

    if this_draft['date_finished'] == None:
        emessage = f'The draft has not been completed yet.'
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    await interaction.response.send_message(f'The flagstring for this draft is:\n```{this_draft["flagstring"]}```')