import discord
import asqlite
import os
import datetime

from functions.constants import DATA_PATH, BR_ROLE

async def br_join(interaction) -> None:
    """
    Registers the current user for the Blackjack Battle Royale

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')

    #check if this player is already registered
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_players WHERE user_id = ?",(interaction.user.id,))
            data = await curs.fetchone()
            # remember: data is a Row, not a list

    if data is not None:
        await interaction.response.send_message('You are already registered for the Blackjack Battle Royale!', ephemeral=True)
        return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_group_weeks WHERE week_num = (SELECT MAX(week_num) FROM br_group_weeks)")
            group_weeks = await curs.fetchall()

    if group_weeks is not None:
        await interaction.response.send_message('Sorry, the event has already begun!', ephemeral=True)
        return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("INSERT INTO br_players (user_id, username, is_demoted, is_recently_demoted, is_final_table, is_lounge_winner,date_joined) VALUES (?,?,0,0,0,0,?)",
                               (interaction.user.id,interaction.user.name,datetime.datetime.now()))

    await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id=BR_ROLE))
    await interaction.response.send_message('You have signed up for the Blackjack Battle Royale!', ephemeral=True)