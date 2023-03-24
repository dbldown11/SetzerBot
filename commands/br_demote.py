import discord
import asqlite
import os
import random

from functions.constants import DATA_PATH

async def br_demote(interaction, user) -> None:
    """
    Flags a character as demoted to the lagomorph lounge

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

    if br_player['is_demoted'] == True:
        emessage = "That player has already been demoted."
        await interaction.response.send_message(content=emessage,ephemeral=True)
        return None

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute('SELECT * FROM br_groups WHERE name = "Lagomorph Lounge"')
            lounge_group = await curs.fetchone()

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("UPDATE br_players SET group_id = ?, is_demoted = 1, is_recently_demoted = 1, is_final_table = 0 WHERE user_id = ?", (lounge_group['id'],user.id))

    lounge_role = discord.utils.get(interaction.guild.roles, id=lounge_group['role_id'])
    await user.add_roles(lounge_role)

    demoted_verbs = ["demoted", "escorted", "taken", "ushered","bumped down", "shown", "brought down", "directed"]

    fun_messages = ["Let's see if their luck can turn around!", "A new underdog story starts here!",
                    "Don't call it a comeback...", "Redemption awaits!", "If at first you don't succeed...",
                    "Hopefully the dealers over there treat you more kindly!", "Lady Luck was especially fickle this time...",
                    "(The *Mysidian Rabbit Room* is for a different randomizer, don't get them confused.)",
                    "On the bright side, they're now cured of Blind, Poison, and Sleep!",
                    "Mugu - and I can't stress this enough - mugu.", "I'm already drinking a Megalixir in their honor!",
                    "Don't tease the slot machine rabbit, kids!", "Well, son of a submariner, I had a side bet on them.",
                    "Half the airship crew had them winning their group in the crew gambling pool, too!",
                    "The end comes... beyond the Lagomorph Lounge.",
                    "Could be worse, I last time people had to go to some wind monster's fighting pit."]

    if br_player['is_final_table']:
        demotion_message = f'{user.display_name} has been eliminated from the Final Table!'
    else:
        demotion_message = f'{user.display_name} has been {random.choice(demoted_verbs)} to the Lagomorph Lounge. '
        demotion_message += random.choice(fun_messages)

    await interaction.response.send_message(demotion_message)