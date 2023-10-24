import discord

VERSION = "v.1.0 2023-03-24"

async def showhelp(interaction):
    """
    Shows the help text for SetzerBot

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the call

    Returns
    -------
    Nothing
    """
    help = """
```ansi
\u001b[0;40m\u001b[1;31mSetzerBot - %s
```
SetzerBot is a drafting bot for Final Fantasy VI: Worlds Collide! Drafters take turns choosing cards from a deck of over 130 different flagset adjustments to create new and unique flagsets.
    
The bot currently supports the following commands:
        `/help`
            Prints this help text
        `/deck`
            Sends a link to the current deck of draft cards
        `/newdraft`  
            Sets up a new draft in the current room. Currently, this only works in ff6wc race rooms (or specific mod-created channels).  
            The following options exist:  
             - drafters: the maximum number of drafters that can join this draft. Defaults to 4, minimum of 1, maximum of 25.  
             - picks: the total number of cards that will be drafted to create the seed. Defaults to 12, minimum of 3, maximum of 25.  
             - cards : the number of cards that each drafter will get to choose from with each pick. Defaults to 3, minimum of 1, maximum of 5.  
             - order: the order in which drafters will take turns choosing:  
              - 'round' will repeat through the same order (e.g. 1-2-3-4-1-2-3-4)  
              - 'snake' will reverse the draft order on even numbered rounds (e.g. 1-2-3-4-4-3-2-1)  
              - 'random' will choose a random drafter for each pick (e.g. 1-3-1-4-4-2-2-3)\n
        `/joindraft`  
            Joins a draft in the current channel.  
        `/startdraft`
            Begins a draft. Once a draft has started, no new players can join.
        `/canceldraft`
            Cancels a draft. This can't be undone!
        `/showpicks`
            Shows the order of draft picks, including who will draft each pick, and what cards were selected in any previous rounds.
        `/draftpick`
            Used by the current drafter to display their card options and allow them to make their pick.
    """ % (VERSION)

    adminhelp = """\n
    Admin-only commands:
        `/getraces`
            A command for administrators which shows the current races
        `!gethistory`
            Get the history of races, stored in db/races.txt
        `!killrace`
            Immediately closes a race room and its spoiler room. 
            This does not check to see if all racers are finished.
    """
    await interaction.response.send_message(help, ephemeral=True)