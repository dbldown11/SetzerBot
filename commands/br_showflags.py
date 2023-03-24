import discord
import asqlite
import os

from functions.constants import DATA_PATH, BR_ROLE

async def br_showflags(interaction,group_name) -> None:
    """
    Shows the flags for the named group

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the showflags call

    group_name : str
        The name of the group to be searched

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

    #check if week is over
    if current_week['week_picks_ended_date'] is None:
        emessage = f"**{current_group['name']}**'s players are still at the dealer's table making their picks for the week. Check back later!"
        await interaction.response.send_message(content=emessage,ephemeral=True)
        return None

    await interaction.response.send_message(f"The **{current_group['name']}** table's flagset for **Week {current_week['week_num']}** is:\n```{current_week['flagstring']}```",
                                            ephemeral=True)

