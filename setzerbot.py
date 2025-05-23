import os
import asqlite
import discord
from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv
from typing import Literal, Optional
from commands.drawcards import drawcards
from commands.newdraft import newdraft
from commands.joindraft import joindraft
from commands.addbotdrafter import addbotdrafter
from commands.startdraft import startdraft
from commands.canceldraft import canceldraft
from commands.draftpick import draftpick
from commands.showpicks import showpicks
from commands.updatedeck import updatedeck
from commands.updatepersonas import updatepersonas
from commands.showhelp import showhelp
from commands.showflags import showflags
from commands.draftoptions import draftoptions
from commands.showoptions import showoptions

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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
token = os.getenv('DISCORD_TOKEN')
guild_id = os.getenv('GUILD_ID')

'''class bot(discord.Client):
    def __int__(self):
        super().__init__(intents=intents)

    async def setup_hook(self) -> None:
        # await tree.sync()
        await db_init()
        await db_init_br()

    async def on_ready(self):
        #await tree.sync()

        print("My life is a chip in your pile! Ante up! ")'''
        
class SetzerBot(commands.Bot):
    def __int__(self):
        super().__init__(command_prefix='!',intents=intents)

    async def setup_hook(self) -> None:
        pass
        # await tree.sync(guild=discord.Object(id=GUILD_ID))
        await db_init()

    async def on_ready(self):
        # await tree.sync()

        print(f"My life is a chip in your pile! Ante up!\n")

        # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
        guild_count = 0

        # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
        guild_list = ""
        for guild in bot.guilds:
            # PRINT THE SERVER'S ID AND NAME.
            guild_list += (f"- {guild.id} (name: {guild.name})\n")

            # INCREMENTS THE GUILD COUNTER.
            guild_count = guild_count + 1

        print(f"Currently active on " + str(guild_count) + " Discord servers:\n")
        print(guild_list)

bot = SetzerBot(command_prefix='!', intents=intents)

# client = bot(intents=intents)

# tree = app_commands.CommandTree(client)

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Silently ignore commands that aren't for this bot
        return
    else:
        print(f'[ERROR] {error}')
        raise error

@bot.tree.command(name="showhelp", description="Instructions on how to use SetzerBot")
async def showhelpcommand(interaction: discord.Interaction):
    await showhelp(interaction)

@bot.tree.command(name="showdeck", description="Sends a link to the current deck of draft cards")
async def showdeckcommand(interaction: discord.Interaction):
    await interaction.response.send_message('Current SetzerBot draft deck: https://tinyurl.com/setzerdeck', ephemeral=True, suppress_embeds=True)

@bot.tree.command(name="newdraft", description="Set up a new draft")
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
@app_commands.describe(
    card_removal='Whether cards are removed from the deck after being picked or being drawn (default: never)'
)
@app_commands.describe(
    calmness='How often the Calmness card appears for drafters (default: uncommon)'
)
@app_commands.describe(
    rarity='How card rarity will be used to determine card drawing (default: normal)'
)
@app_commands.describe(
    categories='How card categories will be used to determine card drawing (default: normal)'
)
@app_commands.describe(
    mulligan='The style of mulligan available for drafters to use to re-draw unwanted hands (default: none)'
)
@app_commands.describe(
    character_cards='Which of the cards to choose starting characters will be in the deck (default: all)'
)
@app_commands.describe(
    bots='The number of automated bot drafters to be added to the draft (default: 0, min: 0, max: 14)'
)
#@app_commands.describe(
#    racename='The unique string for a WC raceroom (i.e. ff6wc-XXXXXX-async). Leave blank if not for an existing race.'
#)
async def newdraftcommand(interaction: discord.Interaction, drafters: app_commands.Range[int, 1, 25] = 4,
                          picks: app_commands.Range[int, 1, 25] = 12, cards: app_commands.Range[int, 2, 5] = 3,
                          order: Literal['round', 'snake', 'chaos'] = 'round',
                          card_removal: Literal['never', 'on_pick', 'on_draw', 'random'] = 'never',
                          calmness: Literal['uncommon', 'rare', 'every_pick', 'once_per_draft', 'none', 'random'] = 'uncommon',
                          rarity: Literal['normal', 'double', 'ignore', 'packs', 'random'] = 'normal',
                          categories: Literal['normal','ignore','random'] = 'normal',
                          mulligan: Literal['none', 'once_per_draft', 'paris', 'topdeck', 'random'] = 'none',
                          character_cards: Literal[
                              'all', 'one_per_character', 'vanilla', 'vanilla_plus_one', 'none'] = 'all',
                          bots: app_commands.Range[int, 0, 14] = 0):
    args = {'drafters': drafters, 'picks': picks, 'cards': cards, 'order': order, 'card_removal': card_removal,
            'calmness': calmness, 'rarity': rarity, 'categories': categories, 'mulligan': mulligan,
            'character_cards': character_cards, 'bots': bots}
    await newdraft(interaction, args)

@bot.tree.command(name="draftoptions", description="Update options for a new, unstarted draft.")
@app_commands.describe(
    picks='The number of cards that will be drafted in total (min: 3, max: 25)'
)
@app_commands.describe(
    cards='The number of cards presented as options for each pick (min: 1, max: 5)'
)
@app_commands.describe(
    order='The order in which drafters will draft each round '
)
@app_commands.describe(
    card_removal='Whether cards are removed from the deck after being picked or being drawn'
)
@app_commands.describe(
    calmness='How often the Calmness card appears for drafters'
)
@app_commands.describe(
    rarity='How card rarity will be used to determine card drawing'
)
@app_commands.describe(
    categories='How card categories will be used to determine card drawing'
)
@app_commands.describe(
    mulligan='The style of mulligan available for drafters to use to re-draw unwanted hands'
)
@app_commands.describe(
    character_cards='Which of the cards to choose starting characters will be in the deck'
)
#@app_commands.describe(
#    racename='The unique string for a WC raceroom (i.e. ff6wc-XXXXXX-async). Leave blank if not for an existing race.'
#)
async def draftoptionscommand(interaction: discord.Interaction,
                              picks: app_commands.Range[int, 1, 25] = None, cards: app_commands.Range[int, 2, 5] = None,
                              order: Literal['round', 'snake', 'chaos'] = None,
                              card_removal: Literal['never', 'on_pick', 'on_draw', 'random'] = None,
                              calmness: Literal['uncommon', 'rare', 'every_pick', 'once_per_draft', 'none', 'random'] = None,
                              rarity: Literal['normal', 'double', 'ignore', 'packs', 'random'] = None,
                              categories: Literal['normal','ignore','random'] = None,
                              mulligan: Literal['none', 'once_per_draft', 'paris', 'topdeck', 'random'] = None,
                              character_cards: Literal[
                                  'all', 'one_per_character', 'vanilla', 'vanilla_plus_one', 'none'] = None,
                              ):
    args = {'picks': picks, 'cards': cards, 'order': order, 'card_removal': card_removal,
            'calmness': calmness, 'rarity': rarity, 'categories': categories, 'mulligan': mulligan,
            'character_cards': character_cards}
    args = {k: v for k, v in args.items() if v is not None}
    await draftoptions(interaction, args)

@bot.tree.command(name="joindraft", description="Join an ongoing draft in the current raceroom")
async def joindraftcommand(interaction: discord.Interaction):
    await joindraft(interaction)

@bot.tree.command(name="addbotdrafter", description="Add a bot-operated AI drafter to the current draft")
async def addbotdraftercommand(interaction: discord.Interaction):
    await addbotdrafter(interaction)
    if not interaction.response.is_done():
        await interaction.delete_original_response()

@bot.tree.command(name="showoptions", description="Display the options that have been set for the current draft")
async def showoptionscommand(interaction: discord.Interaction):
    await showoptions(interaction)

@bot.tree.command(name="startdraft", description="Begin a draft in the current raceroom")
async def startdraftcommand(interaction: discord.Interaction):
    await startdraft(interaction)
  
@bot.tree.command(name="draftpick", description="Choose a card to modify the seed")
async def draftpickcommand(interaction: discord.Interaction):
    await draftpick(interaction)

@bot.tree.command(name="showpicks", description="View all of the previous and upcoming picks of the current draft")
async def showpickscommand(interaction: discord.Interaction):
    await showpicks(interaction)

@bot.tree.command(name="showflags", description="Display the flagstring for a completed draft in the current room")
async def showflagscommand(interaction: discord.Interaction):
    await showflags(interaction)

@bot.tree.command(name="updatedeck", description="(Admin Only) Update the deck used for regular drafts")
async def updatedeckcommand(interaction: discord.Interaction, deck_csv: discord.Attachment):
    if isAdmin(interaction.user):
        await updatedeck(interaction,deck_csv)
    else:
        await interaction.response.send_message('Sorry, but that command is restricted to SetzerBot admin users only.',ephemeral=True)

@bot.tree.command(name="updatepersonas", description="(Admin Only) Update the personas used for bot drafters")
async def updatepersonascommand(interaction: discord.Interaction, personas_csv: discord.Attachment):
    if isAdmin(interaction.user):
        await updatepersonas(interaction,personas_csv)
    else:
        await interaction.response.send_message('Sorry, but that command is restricted to SetzerBot admin users only.',ephemeral=True)

@bot.tree.command(name="canceldraft", description="Cancel the draft in the current raceroom")
async def canceldraftcommand(interaction: discord.Interaction):
    await canceldraft(interaction)

'''@bot.tree.command(name="importpicks", description="(Admin Only) Carry over draft picks from a previous draft.")
async def importpickscommand(interaction: discord.Interaction):
    if isAdmin(interaction.user):
        await interaction.response.send_message('This command is not yet implemented.', ephemeral=True)
    else:
        await interaction.response.send_message('This command is only usable by admins.', ephemeral=True)'''

##### HERE ARE THE BATTLE ROYALE COMMANDS #####
'''

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
'''

bot.run(token)
