from discord.ext import commands

import discord

class CardButton(discord.ui.Button):
    def __init__(self, label: str):
        super().__init__(label=label)
        self.style = discord.ButtonStyle.primary

    async def callback(self,interaction: discord.Interaction):
        if self.view.author == interaction.user:
            for x in self.view.children:
                #print(f'trying to disable {x.id}, its a type {type(x.id)}')
                x.disabled = True
            await interaction.response.edit_message(view=self.view)
            self.view.chosencard = self.label
            self.view.stop()
        else:
            await interaction.response.send_message("You aren't allowed to choose someone else's cards!")
            self.view.chosencard = None
            #self.view.stop()

class CardView(discord.ui.View):
    def __init__(self,author):
        super().__init__()
        self.author = author
        self.chosencard = None
        self.timeout = None

    #async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        #return interaction.user == self.author