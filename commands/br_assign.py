import discord
import asqlite
import os

from functions.constants import DATA_PATH

async def br_assign(interaction, br_table, users) -> None:
    """
    Assigns up to five players to a table for the Blackjack Battle Royale

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    br_table : str
        The name of the group the players are being added to

    users : list
        A list of strings with the name and identifier of the person to be added to the group

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')

    #get group info for the named group
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_groups WHERE name = ?",(br_table,))
            groupinfo = await curs.fetchone()

    if groupinfo is None:
        emessage = "No group exists with that name."
        await interaction.response.send_message(content=emessage,ephemeral=True)
        return None
    else:
        group_id = groupinfo['id']

    #get list of current group members
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_players WHERE group_id = ?",(group_id,))
            current_group_members = await curs.fetchall()

    if len(users) + len(current_group_members) > 5:
        emessage = f"Attempting to add {len(users)} would exceed the total capacity of the group."
        await interaction.response.send_message(content=emessage, ephemeral=True)
        return None

    #TODO Check if player is already in a group

    group_role = discord.utils.get(interaction.guild.roles, id=groupinfo['role_id'])

    #update the DB
    successful_adds = 0
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            for player_name in users:
                if player_name is not None:
                    username = player_name.split('#')[0]
                    user_discriminator = player_name.split('#')[1]
                    user_id = discord.utils.get(interaction.guild.members,name=username,discriminator=user_discriminator)
                    await user_id.add_roles(group_role)
                    await curs.execute("UPDATE br_players SET group_id = ? WHERE user_id = ?",(group_id,user_id.id))
                    successful_adds += 1

    #add them to private channel???

    await interaction.response.send_message(f'{successful_adds} users successfully added to {br_table}!',ephemeral=True)