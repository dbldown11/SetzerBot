import discord
import asqlite

class CalmnessSelect(discord.ui.Select):
    def __init__(self, all_cards, previous_cards):
        # all_cards and previous_cards are both lists of SQLite rows
        
        #TODO Add timeout!
        
        print(f'making a calmness select, all cards is {all_cards}, previous_cards is {previous_cards}')
        options = []
        for card in previous_cards:
            for cur_card in all_cards:
                if cur_card['id'] == card['card_id']:
                    options.append(discord.SelectOption(label=cur_card['name'],description= cur_card['desc'][:100], value = card['pick_number']))

        super().__init__(placeholder='Select the card to remove', min_values = 1, max_values = 1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.view.author == interaction.user:
            self.view.value = int(self.values[0])
            #print(f'I chose to remove pick number {self.values}')
            await interaction.response.send_message(f'**Pick #{self.values[0]}** has been affected by Calmness!')
            self.disabled = True
            self.view.stop()
        else:
            await interaction.response.send_message("You may not choose another player's Calmness option!")

class CalmnessView(discord.ui.View):
    def __init__(self, all_cards, previous_cards, author):
        super().__init__()
        self.author = author
        self.value = None
        
        self.add_item(CalmnessSelect(all_cards, previous_cards))
'''
class CalmnessModal(discord.ui)
    def __init__(self, previous_cards):
        self.add_item(CalmnessSelect(previous_cards))
        self.removed_card = None
'''
