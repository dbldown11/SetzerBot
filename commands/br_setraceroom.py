import discord
import asqlite
import os

from functions.constants import DATA_PATH, BR_ROLE

async def br_setraceroom(interaction,group_name,raceroom_name) -> None:
    """
    Sets the raceroom for the named group

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the showflags call

    group_name : str
        The name of the group to be searched

    raceroom_name : str
        The name of the race room for the group's current week

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')

    #get group info for all groups
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_groups")
            br_groups = await curs.fetchall()

    #current_group = [group for group in br_groups if group['name'] == group_name]
    current_group = None
    for group in br_groups:
        if group['name'] == group_name:
            current_group = group

    if current_group is None:
        emessage = f"There is no Blackjack Battle Royale table called {group_name}."
        await interaction.response.send_message(content=emessage,ephemeral=True)
        return None

    #get the group's current week
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = (SELECT MAX(week_num) FROM br_group_weeks)",current_group['id'])
            current_week = await curs.fetchone()

    #set raceroom
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("UPDATE br_group_weeks SET raceroom = ? WHERE id = ?",
                               (raceroom_name,current_week['id']))
            await conn.commit()

    await interaction.response.send_message(f'Raceroom for {current_group["name"]} week #{current_week["week_num"]} set to {raceroom_name}',ephemeral=True)