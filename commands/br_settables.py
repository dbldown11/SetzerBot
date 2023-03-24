import discord
import asqlite
import os
import random
import datetime
import json
import requests

from functions.stringfunctions import int_list_to_string,string_to_int_list

from functions.constants import DATA_PATH, BR_ROLE

from dotenv import load_dotenv

async def br_settables(interaction, player_count) -> None:
    """
    Generates a new week for the event

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    player_count : int
        The number of players who participated in the opening round

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')

    table_names = ['Alexandr','Carbunkl','Palidor','Starlet','Ragnarok','Odin','Bahamut','Fenrir','Maduin','Tritoch',
                   'Siren','Phoenix','Kirin','Unicorn']
    event_category = discord.utils.get(interaction.guild.categories,name='Blackjack Battle Royale')

    await interaction.response.defer(ephemeral=True)

    if event_category is None:
        emessage = f'There is no category called "Blackjack Battle Royale", please make one before running this command.'
        await interaction.response.send_message(content=emessage,ephemeral=True)
        return None

    for x in range(player_count // 5):
        #Make a role
        table_role = await interaction.guild.create_role(name=table_names[x],reason='Table role for Blackjack Battle Royale')
        #Make a channel
        table_channel = await interaction.guild.create_text_channel(name=table_names[x],category=event_category)
        #Make a DB group
        group_query = (interaction.guild.id,table_names[x],table_channel.id,table_role.id)
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""INSERT INTO br_groups (guild_id,name,channel_id,role_id)
                VALUES (?,?,?,?);""", group_query)

    additional_tables = ['Lagomorph Lounge','Final Table']
    for x in additional_tables:
        #Make a role
        table_role = await interaction.guild.create_role(name=x,reason='Table role for Blackjack Battle Royale')
        #Make a channel
        table_channel = await interaction.guild.create_text_channel(name=x,category=event_category)
        #Make a DB group
        group_query = (interaction.guild.id,x,table_channel.id,table_role.id)
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("""INSERT INTO br_groups (guild_id,name,channel_id,role_id)
                VALUES (?,?,?,?);""", group_query)

    await interaction.followup.send('Tables created!',ephemeral=True)