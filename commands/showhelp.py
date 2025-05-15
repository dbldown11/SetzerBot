import discord

VERSION = "v.1.3 2025-04-09"

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
SetzerBot is a drafting bot for Final Fantasy VI: Worlds Collide! Drafters take turns choosing cards from a deck of over 230 different flagset adjustments to create new and unique flagsets.
    
User guide: https://docs.google.com/document/d/1DB3QMfXten3jVlX3K45XFp9S7IxkRI5iW2j-UMuZ_Mk/edit?usp=sharing""" % (VERSION)

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

