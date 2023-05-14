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

async def br_startweek(interaction) -> None:
    """
    Generates a new week for the event

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'br_data.db')
    dotenv_path = os.path.join(os.path.dirname(os.getcwd()), '.env')
    load_dotenv(dotenv_path)

    API_KEY = os.getenv("RACEBOT_API_KEY")

    #determine the current week
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_group_weeks")
            br_group_weeks = await curs.fetchall()

    week_num = 1
    if len(br_group_weeks) > 0:
        for week in br_group_weeks:
            if week['week_num'] > week_num:
                week_num = week['week_num']
        week_num += 1
    print(f'Starting week #{week_num}')


    #get group info for all groups
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_groups")
            br_groups = await curs.fetchall()

    for group in br_groups:
        if group['name'] == 'Final Table':
            finals_group_id = group['id']
        if group['name'] == 'Lagomorph Lounge':
            lounge_group_id = group['id']

    #figure out if it's last week and if so, make finals group
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_players")
            br_players = await curs.fetchall()

    is_finals_already = False
    for player in br_players:
        if player['is_final_table'] == True:
            is_finals_already = True

    await interaction.response.defer()

    #determine if any non-finals/non-lounge group has > 1 person - if not, then it's time to start finals
    if is_finals_already == False:
        max_group_size = 0
        for group in br_groups:
            group_count = 0
            for player in br_players:
                if player['group_id'] == group['id'] and group['name'] != 'Final Table' and group['name'] != 'Lagomorph Lounge' and player['is_demoted'] == False:
                    group_count += 1
            if group_count > max_group_size:
                max_group_size = group_count
        #make a finals table if it's the end
        if max_group_size == 1:
            print('initializing finals')
            is_finals_already = True
            #get final table role
            for group in br_groups:
                if group['name'] == 'Final Table':
                    final_group_role_id = group['role_id']
                    final_group_channel = discord.utils.get(interaction.guild.text_channels, id=group['channel_id'])
            final_group_role = discord.utils.get(interaction.guild.roles, id=final_group_role_id)
            for player in br_players:
                if (player['is_demoted'] == True and player['is_lounge_winner'] == True) or (player['is_demoted'] == False and player['group_id'] in range(1,11)):
                    print(f'promoting {player["user_id"]}')
                    winner_group = player['group_id']
                    async with asqlite.connect(path) as conn:
                        async with conn.cursor() as curs:
                            await curs.execute("SELECT name FROM br_groups WHERE id = ?",
                                               (winner_group,))
                            winning_group_name = await curs.fetchone()
                    async with asqlite.connect(path) as conn:
                        async with conn.cursor() as curs:
                            await curs.execute("SELECT * FROM br_picks WHERE group_id = ? AND isremoved = 0 and card_id != 0",
                                               (winner_group,))
                            winner_group_picks = await curs.fetchall()
                    winner_cards = []
                    for pick in winner_group_picks:
                        winner_cards.append(pick['card_id'])
                    if len(winner_cards) > 25:
                        winner_cards = winner_cards[-25:]
                    winner_card_string = await int_list_to_string(winner_cards)
                    async with asqlite.connect(path) as conn:
                        async with conn.cursor() as curs:
                            print('updating table')
                            await curs.execute("UPDATE br_players SET group_id = ?, is_final_table = 1, group_cards = ? WHERE id = ?",
                                               (finals_group_id,winner_card_string,player['id']))
                    promoted_user = discord.utils.get(interaction.guild.members,id=player['user_id'])
                    await promoted_user.add_roles(final_group_role)
                    await final_group_channel.send(f'{promoted_user.mention}, has arrived at the final table from **{winning_group_name[0]}**!')


            print('A final table was made!')

    #Create weeks
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_groups")
            br_groups = await curs.fetchall()

    print('about to make weeks')

    for group in br_groups:
        if is_finals_already == False and group['name'] != 'Final Table':
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute("""INSERT INTO br_group_weeks (group_id, week_num, week_picks_started_date)
                    VALUES (?,?,?);""",(group['id'],week_num,datetime.datetime.now()))
        elif is_finals_already == True and group['name'] == 'Final Table':
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    await curs.execute("""INSERT INTO br_group_weeks (group_id, week_num, week_picks_started_date)
                    VALUES (?,?,?);""",(group['id'],week_num,datetime.datetime.now()))

    '''#get updated current weeks from the DB
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute("SELECT * FROM br_group_weeks WHERE week_num = ?",(week_num,))
            br_group_weeks = await curs.fetchall()'''

    #Generate a wave of picks for each group
    if is_finals_already == True:
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM br_players WHERE group_id = ?", (finals_group_id,))
                final_players = await curs.fetchall()
        #TODO as of 3/20, need to add raceroom functionality
        async with asqlite.connect(path) as conn:
            async with conn.cursor() as curs:
                await curs.execute("SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = ?",
                                   (group['id'], week_num - 1))
                last_week = await curs.fetchone()
        if last_week is None or last_week['raceroom'] is None:
            emessage = f'No raceroom is set for {group["name"]}, randomizing order instead.'
            print(emessage)
            random.shuffle(final_players)
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as curs:
                    for count, player in enumerate(final_players):
                        initial_picks = player['group_cards']
                        await curs.execute("SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = ?",(player['group_id'],week_num))
                        group_week = await curs.fetchone()
                        pick_data = (finals_group_id, player['id'], group_week['id'], count + 1, initial_picks, 0)
                        await curs.execute(
                            """INSERT INTO br_picks (group_id, player_id, week_id, pick_number, pick_options, removed_card) VALUES (?,?,?,?,?,?);""",
                            pick_data)
                        await curs.execute("UPDATE br_players SET group_cards = ? WHERE id = ?",(None,player['id']))
        else:
            # get race results
            url = "http://dr-bot.net/races"
            my_headers = {'Content-type': 'application/json', 'apikey': API_KEY}
            response = requests.get(url, headers=my_headers, params={"key": last_week['raceroom']})
            data = json.loads(response.text)
            # print(data)
            result_dicts = data['entrants']  # this is a list of dicts
            result_dicts_sorted = sorted(result_dicts, key=lambda x: x['placement'],
                                         reverse=True)  # sorted in descending order
            # random.shuffle(group_players)
            # print(result_dicts_sorted)

            for count, race_finish in enumerate(result_dicts_sorted):
                for player in final_players:
                    if str(race_finish['id']) == str(player['user_id']):
                        print(f'match on {race_finish["id"]}')
                        async with asqlite.connect(path) as conn:
                            async with conn.cursor() as curs:
                                await curs.execute(
                                    "SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = ?",
                                    (player['group_id'], week_num))
                                group_week = await curs.fetchone()
                                pick_data = (group['id'], player['id'], group_week['id'], count + 1, 0)
                                await curs.execute(
                                    """INSERT INTO br_picks (group_id, player_id, week_id, pick_number, removed_card) VALUES (?,?,?,?,?);""",
                                    pick_data)
    else:
        for group in br_groups:
            if group['name'] == 'Lagomorph Lounge':
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        await curs.execute("SELECT * FROM br_players WHERE is_recently_demoted = 1")
                        demoted_players = await curs.fetchall()
                random.shuffle(demoted_players)
                print(f'doing picks for demoted players, list is {demoted_players}')
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        for count, player in enumerate(demoted_players):
                            await curs.execute("SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = ?",
                                               (player['group_id'], week_num))
                            group_week = await curs.fetchone()
                            pick_data = (group['id'], player['id'], group_week['id'], count + 1, 0)
                            await curs.execute(
                                """INSERT INTO br_picks (group_id, player_id, week_id, pick_number, removed_card) VALUES (?,?,?,?,?);""",
                                pick_data)

                #reset recent demoted status for all
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as curs:
                        await curs.execute("""UPDATE br_players SET is_recently_demoted = 0""")
            else:
                if group['name'] != 'Final Table':
                    async with asqlite.connect(path) as conn:
                        async with conn.cursor() as curs:
                            await curs.execute("SELECT * FROM br_players WHERE group_id = ?", (group['id'],))
                            initial_group_players = await curs.fetchall()
                    #TODO Get last week's raceroom here
                    async with asqlite.connect(path) as conn:
                        async with conn.cursor() as curs:
                            await curs.execute("SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = ?",(group['id'],week_num-1))
                            last_week = await curs.fetchone()
                    if last_week is None or last_week['raceroom'] is None:
                        emessage = f'No raceroom is set for {group["name"]}, randomizing order instead.'
                        print(emessage)
                        random.shuffle(initial_group_players)
                        async with asqlite.connect(path) as conn:
                            async with conn.cursor() as curs:
                                for count, player in enumerate(initial_group_players):
                                    await curs.execute(
                                        "SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = ?",
                                        (player['group_id'], week_num))
                                    group_week = await curs.fetchone()
                                    pick_data = (group['id'], player['id'], group_week['id'], count + 1, 0)
                                    await curs.execute(
                                        """INSERT INTO br_picks (group_id, player_id, week_id, pick_number, removed_card) VALUES (?,?,?,?,?);""",
                                        pick_data)
                    else:
                        #get race results
                        url = "http://dr-bot.net/races"
                        my_headers = {'Content-type': 'application/json', 'apikey': API_KEY}
                        response = requests.get(url, headers=my_headers, params={"key": last_week['raceroom']})
                        data = json.loads(response.text)
                        #print(data)
                        result_dicts = data['entrants']  # this is a list of dicts
                        result_dicts_sorted = sorted(result_dicts, key=lambda x: x['placement'],reverse=True)  # sorted in descending order
                        #random.shuffle(group_players)
                        #print(result_dicts_sorted)

                        for count, race_finish in enumerate(result_dicts_sorted):
                            for player in initial_group_players:
                                if str(race_finish['id']) == str(player['user_id']):
                                    print(f'match on {race_finish["id"]}')
                                    async with asqlite.connect(path) as conn:
                                        async with conn.cursor() as curs:
                                            await curs.execute(
                                                "SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = ?",
                                                (player['group_id'], week_num))
                                            group_week = await curs.fetchone()
                                            pick_data = (group['id'], player['id'], group_week['id'], count, 0)
                                            await curs.execute(
                                                """INSERT INTO br_picks (group_id, player_id, week_id, pick_number, removed_card) VALUES (?,?,?,?,?);""",
                                                pick_data)

                    '''                 
                    async with asqlite.connect(path) as conn:
                        async with conn.cursor() as curs:
                            for count, player in enumerate(group_players):
                                await curs.execute("SELECT * FROM br_group_weeks WHERE group_id = ? AND week_num = ?",
                                                   (player['group_id'], week_num))
                                group_week = await curs.fetchone()
                                pick_data = (group['id'], player['id'], group_week['id'], count + 1, 0)
                                await curs.execute(
                                    """INSERT INTO br_picks (group_id, player_id, week_id, pick_number, removed_card) VALUES (?,?,?,?,?);""",
                                    pick_data)'''

    print(f'{week_num} has successfully been started!')

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as curs:
            await curs.execute('''SELECT br_players.user_id, br_groups.name, br_groups.channel_id FROM br_picks JOIN br_players 
            ON br_picks.player_id = br_players.id JOIN br_groups ON br_picks.group_id = br_groups.id JOIN 
            br_group_weeks ON br_picks.week_id = br_group_weeks.id WHERE br_picks.pick_number = 1 
            AND br_group_weeks.week_num = ?''',(week_num,))
            first_picks = await curs.fetchall()

    for pick in first_picks:
        group_channel = discord.utils.get(interaction.guild.text_channels,id=pick['channel_id'])
        pick_user = discord.utils.get(interaction.guild.members,id=pick['user_id'])
        await group_channel.send(f"""{pick_user.display_name} has the first pick this week for {pick['name']}.\n{pick_user.mention}, please make your pick using the `/br pick` command.""")

    await interaction.followup.send(f'Drafting for week {week_num} of the Blackjack Battle Royale has begun. Players, please head to your tables!')

