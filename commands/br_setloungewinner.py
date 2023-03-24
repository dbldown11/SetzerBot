import discord
import asqlite
import os

from functions.constants import DATA_PATH

async def br_setloungewinner(interaction, user) -> None:
    """
    Sets the named user as the winner of the Lagomorph Lounge

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    user : discord.User
        A list of strings with the name and identifier of the person to be added to the group

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')

    #see if player is in BR and if they aren't already demoted
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_players WHERE user_id = ?",(user.id,))
            br_player = await curs.fetchone()

    if br_player is None:
        emessage = "That player is not entered into the Blackjack Battle Royale."
        await interaction.response.send_message(content=emessage,ephemeral=True)
        return None

    if br_player['is_demoted'] == False:
        emessage = "That player is not in the Lagomorph Lounge."
        await interaction.response.send_message(content=emessage,ephemeral=True)
        return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("UPDATE br_players SET is_lounge_winner = 0")
            await curs.execute("UPDATE br_players SET is_lounge_winner = 1 WHERE user_id = ?",(user.id))

    await interaction.response.send_message(content=f"{user.display_name} is now set as the Lagomorph Lounge winner!",ephemeral=True)