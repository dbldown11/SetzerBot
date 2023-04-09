import os
import asqlite
import discord
from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv
from typing import Literal
from commands.drawcards import drawcards
from commands.newdraft import newdraft
from commands.joindraft import joindraft
from commands.startdraft import startdraft
from commands.canceldraft import canceldraft
from commands.draftpick import draftpick
from commands.showpicks import showpicks
from commands.updatedeck import updatedeck
from commands.showhelp import showhelp

from commands.br_join import br_join
from commands.br_assign import br_assign
from commands.br_demote import br_demote
from commands.br_startweek import br_startweek
from commands.br_pick import br_pick
from commands.br_showflags import br_showflags
from commands.br_setraceroom import br_setraceroom
from commands.br_skippick import br_skippick
from commands.br_showpicks import br_showpicks
from commands.br_settables import br_settables
from commands.br_exportplayers import br_exportplayers
from commands.br_setloungewinner import br_setloungewinner
from commands.br_updatedeck import br_updatedeck

from functions.db_init import db_init, db_init_br
from functions.isAdmin import isAdmin

from functions.constants import ADMINS
from functions.constants import DATA_PATH
from functions.constants import BR_ROLE

load_dotenv()

intents =  discord.Intents.default()
intents.message_content = True
intents.members = True
token = os.getenv('DISCORD_TOKEN')

class bot(discord.Client):
    def __int__(self):
        super().__init__(intents=intents)

    async def setup_hook(self) -> None:
        await tree.sync()
        await db_init()
        await db_init_br()

    async def on_ready(self):
        # await tree.sync(guild=discord.Object(id=guild_id))

        print("My life is a chip in your pile! Ante up! ")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = bot(intents=intents)

tree = app_commands.CommandTree(client)

@tree.command(name="help", description="Instructions on how to use SetzerBot")
async def showhelpcommand(interaction: discord.Interaction):
    await showhelp(interaction)

@tree.command(name="newdraft", description="Set up a new draft")
@app_commands.describe(
    drafters='The maximum number of players who will be drafting (default: 4, min: 1, max: 25)')
@app_commands.describe(
    picks='The number of cards that will be drafted in total (default: 12, min: 3, max: 25)'
)
@app_commands.describe(
    cards='The number of cards presented as options for each pick (default: 3, min: 1, max: 5)'
)
@app_commands.describe(
    order='The order in which drafters will draft each round (default: round)'
)
#@app_commands.describe(
#    racename='The unique string for a WC raceroom (i.e. ff6wc-XXXXXX-async). Leave blank if not for an existing race.'
#)
async def newdraftcommand(interaction: discord.Interaction, drafters: app_commands.Range[int, 1, 25] = 4,
                          picks: app_commands.Range[int, 1, 25] = 12, cards: app_commands.Range[int, 1, 5] = 3,
                          order: Literal['round','snake','random'] = 'round'):
    args = {'drafters': drafters, 'picks': picks, 'cards': cards, 'order': order}
    await newdraft(interaction, args)

@tree.command(name="joindraft", description="Join an ongoing draft in the current raceroom")
async def joindraftcommand(interaction: discord.Interaction):
    await joindraft(interaction)

@tree.command(name="startdraft", description="Begin a draft in the current raceroom")
async def startdraftcommand(interaction: discord.Interaction):
    await startdraft(interaction)
  
@tree.command(name="draftpick", description="Choose a card to modify the seed")
async def draftpickcommand(interaction: discord.Interaction):
    await draftpick(interaction)

@tree.command(name="showpicks", description="View all of the previous and upcoming picks of the current draft")
async def showpickscommand(interaction: discord.Interaction):
    await showpicks(interaction)

@tree.command(name="updatedeck", description="(Admin Only) Update the deck used for regular drafts")
async def updatedeckcommand(interaction: discord.Interaction, deck_csv: discord.Attachment):
    if isAdmin(interaction.user):
        await updatedeck(interaction,deck_csv)
    else:
        await interaction.response.send_message('Sorry, but that command is restricted to SetzerBot admin users only.',ephemeral=True)

@tree.command(name="canceldraft", description="Cancel the draft in the current raceroom")
async def canceldraftcommand(interaction: discord.Interaction):
    await canceldraft(interaction)

@tree.command(name="importpicks", description="(Admin Only) Carry over draft picks from a previous draft.")
async def importpickscommand(interaction: discord.Interaction):
    if isAdmin(interaction.user):
        await interaction.response.send_message('This command is not yet implemented.', ephemeral=True)
    else:
        await interaction.response.send_message('This command is only usable by admins.', ephemeral=True)

##### HERE ARE THE BATTLE ROYALE COMMANDS #####

# Setseed group of commands
br_group = app_commands.Group(name='br',
                                   description='Bot commands for the Blackjack Battle Royale event')


@br_group.command(name='join',
                       description='Join the Blackjack Battle Royale event!')
async def br_join_command(interaction: discord.Interaction):
    await br_join(interaction)

@br_group.command(name='assign',
                       description='(Admin Only) Assigns up to five players to a BBR table.')
async def br_assign_command(interaction: discord.Interaction, br_table: str, user1: str = None, user2: str = None,
                            user3: str = None,user4: str = None,user5: str = None):
    if isAdmin(interaction.user):
        await br_assign(interaction, br_table = br_table, users = [user1,user2,user3,user4,user5])
    else:
        await interaction.response.send_message('This command is only usable by event admins.', ephemeral=True)

@br_assign_command.autocomplete('br_table')
async def openrace_command_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    path = os.path.join(DATA_PATH, 'br_data.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT name FROM br_groups")
            data = await curs.fetchall()
    groups = [str(grp[0]) for grp in data]
    return [
               app_commands.Choice(name=group, value=group)
               for group in groups if current.lower() in group.lower()
           ][:25]

@br_assign_command.autocomplete('user1')
@br_assign_command.autocomplete('user2')
@br_assign_command.autocomplete('user3')
@br_assign_command.autocomplete('user4')
@br_assign_command.autocomplete('user5')
async def assign_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    br_role = discord.utils.get(interaction.guild.roles, id=BR_ROLE)
    members = br_role.members
    member_names = [f"{member.name}#{member.discriminator}" for member in members]
    # Return the list of member strings
    #groups = [str(grp[0]) for grp in data]
    return [
               app_commands.Choice(name=membername, value=membername)
               for membername in member_names if current.lower() in membername.lower()
           ][:25]

@br_group.command(name='demote',
                       description='(Admin Only) Flags a player as demoted to the Lagomorph Lounge')
async def br_demote_command(interaction: discord.Interaction, demoted_user: str = None):
    user_name = demoted_user.split('#')[0]
    user_discriminator = demoted_user.split('#')[1]
    user_object = discord.utils.get(interaction.guild.members, name=user_name, discriminator=user_discriminator)
    if isAdmin(interaction.user):
        if user_object is not None:
            await br_demote(interaction, user = user_object)
        else:
            await interaction.response.send_message('No user found with that name.',ephemeral=True)
    else:
        await interaction.response.send_message('This command is only usable by event admins.', ephemeral=True)

@br_group.command(name='setloungewinner', description='(Admin only) Set the winner of the lagomorph lounge')
async def br_setloungewinner_command(interaction: discord.Interaction, winning_user: str = None):
    user_name = winning_user.split('#')[0]
    user_discriminator = winning_user.split('#')[1]
    user_object = discord.utils.get(interaction.guild.members, name=user_name, discriminator=user_discriminator)
    if isAdmin(interaction.user):
        await br_setloungewinner(interaction, user = user_object)
    else:
        await interaction.response.send_message('This command is only usable by event admins.', ephemeral=True)

@br_demote_command.autocomplete('demoted_user')
@br_setloungewinner_command.autocomplete('winning_user')
async def demote_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    br_role = discord.utils.get(interaction.guild.roles, id=BR_ROLE)
    members = br_role.members
    member_names = [f"{member.name}#{member.discriminator}" for member in members]
    # Return the list of member strings
    #groups = [str(grp[0]) for grp in data]
    return [
               app_commands.Choice(name=membername, value=membername)
               for membername in member_names if current.lower() in membername.lower()
           ][:25]

@br_group.command(name='startweek',
                       description='Starts a new Blackjack Battle Royale event week')
async def br_startweek_command(interaction: discord.Interaction):
    if isAdmin(interaction.user):
        await br_startweek(interaction)
    else:
        await interaction.response.send_message('This command is only usable by event admins.', ephemeral=True)

@br_group.command(name='pick',
                       description='Choose a card to modify the Battle Royale group''s seed')
async def br_pick_command(interaction: discord.Interaction):
    await br_pick(interaction)

@br_group.command(name='showflags',
                       description='Show the flags for this Battle Royale group.')
async def br_showflags_command(interaction: discord.Interaction,br_table: str):
    await br_showflags(interaction, br_table)

@br_group.command(name='setraceroom',
                       description='(Admin Only) Set the raceroom for this table for the current week.')
async def br_setraceroom_command(interaction: discord.Interaction,br_table: str,raceroom_name: str):
    if isAdmin(interaction.user):
        await br_setraceroom(interaction, br_table,raceroom_name)
    else:
        await interaction.response.send_message('This command is only usable by event admins.', ephemeral=True)

@br_group.command(name='skippick',
                       description='(Admin Only) Skips the pick for the current player in a given group.')
async def br_skippick_command(interaction: discord.Interaction,br_table: str):
    if isAdmin(interaction.user):
        await br_skippick(interaction, br_table)
    else:
        await interaction.response.send_message('This command is only usable by event admins.', ephemeral=True)

@br_group.command(name='showpicks', description='When used in a group''s channel, shows the group''s previous and current picks.')
async def br_showpicks_command(interaction: discord.Interaction):
    await br_showpicks(interaction)

@br_group.command(name='settables', description='(Admin only) Create the tables for the Blackjack Battle Royale event.')
async def br_settables_command(interaction: discord.Interaction,player_num: int):
    if isAdmin(interaction.user):
        await br_settables(interaction,player_num)
    else:
        await interaction.response.send_message('This command is only usable by event admins.', ephemeral=True)

@br_group.command(name='exportplayers', description='(Admin only) Export a CSV of all entrants')
async def br_exportplayers_command(interaction: discord.Interaction):
    if isAdmin(interaction.user):
        await br_exportplayers(interaction)
    else:
        await interaction.response.send_message('This command is only usable by event admins.', ephemeral=True)

@br_showflags_command.autocomplete('br_table')
@br_setraceroom_command.autocomplete('br_table')
@br_skippick_command.autocomplete('br_table')
async def br_table_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    path = os.path.join(DATA_PATH, 'br_data.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT name FROM br_groups")
            data = await curs.fetchall()
    groups = [str(grp[0]) for grp in data]
    return [
               app_commands.Choice(name=group, value=group)
               for group in groups if current.lower() in group.lower()
           ][:25]

@br_setraceroom_command.autocomplete('raceroom_name')
async def raceroom_name_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    racing_category = discord.utils.get(interaction.guild.categories, name='Racing')
    sync_racing_category = discord.utils.get(interaction.guild.categories, name='Sync Racing')
    channels = []
    for channel in racing_category.channels + sync_racing_category.channels:
        if isinstance(channel, discord.TextChannel) and channel.name.startswith('ff6wc') and not channel.name.endswith(
                'spoiler'):
            channels.append(channel.name)
    return [
               app_commands.Choice(name=channel, value=channel)
               for channel in channels if current.lower() in channel.lower()
           ][:25]

@br_group.command(name="updatedeck", description="(Admin Only) Update the deck used for the Blackjack Battle Royale")
async def updatedeckcommand(interaction: discord.Interaction, deck_csv: discord.Attachment):
    if isAdmin(interaction.user):
        await br_updatedeck(interaction,deck_csv)
    else:
        await interaction.response.send_message('Sorry, but that command is restricted to SetzerBot admin users only.',ephemeral=True)

# Adds the setseed commands to the command tree
tree.add_command(br_group)



client.run(token)

#TODO Make specific support for Blackjack Battle Royale
#Limit to one pick per week (reset picks at X time/day)
#Resolve pick conflicts
#Command to show current active cards

#TODO Start an event draft session
# Args: flagstring, picks
# Take a flagstring as input (the starting set) - check that it's valid
# Starts a new draft session - players need to /joindraft?

#TODO Import/export a draft string
#Long encrypted(?) string that summarizes what cards were picked in what order

#TODO Ghost drafters if someone wants to solo draft with others
#TODO Extra options for newdraft: nocalmness, alwayscalmness, norarity, exclude categories, random exclude
#TODO User-created draft order

#TODO Mulligans (discard choices for choices -1, random topdeck)

'''
command
/br help
-> shows all the commands for players (and the admin commands for admins)

/br join - DONE
-> adds player to the players list, gives them the BR role

/br assign (args) [admin] DONE
-> adds the five players chosen to the given group, gives them roles

/br remove ??
-> removes a player from the chosen group (pre-start only)

/brdemote X [admin] DONE
-> sets demoted and recently_demoted to true for a group member

/br pick DONE

/br makegroups ?

/br undemote ??

/br newweek

/br startweek [admin] DONE-ish
-> opens draft picks for the new week

/br groupstatus [admin]
-> returns how many people still need to pick in the current group

/br allgroupstatus [admin]
-> returns how many people still need to pick in all groups

/br addcards (args) [admin]
-> adds the cards selected to the group's picks (player_id = null)

/br removeplayer (player)
-> removes a player from their current group

/br showflags DONE
-> shows the most recent completed week's flagstring for a group (the player's group if none provided, error if none and player not in a group)
'''