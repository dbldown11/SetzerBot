import discord
import random
from functions.last_card import last_card
from functions.remove_card import remove_card
from functions.remove_earliest_duplicates import remove_earliest_duplicates


async def createflags(interaction, cards) -> str:
    """
    Generate a flagset for an completed draft

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that started the command

    cards : list
        A list of integers corresponding to card numbers of cards drafted (in order drafted)

    Returns
    -------
    A str containing an FF6 WC flagstring
    """
    obj_count = 0
    obj_prefix = ['oa', 'ob', 'oc', 'od', 'oe', 'of', 'og', 'oh', 'oi', 'oj', 'ok', 'ol', 'om', 'on', 'oo', 'op', 'oq',
                  'or', 'os', 'ot',
                  'ou', 'ov', 'ow', 'ox', 'oy', 'oz']

    # -----GAME-----
    # SETTINGS
    if 131 in cards:
        mode = "-open"
    else:
        mode = "-cg"

    # slog = random.choices(['', ' -sl'], weights=([1, 0]), k=1)[0]
    slog = ''
    settings = ''.join([mode, slog])

    # KEFKA'S TOWER & STATUE SKIP
    ktcard = await last_card(cards, 50, 51, 52, 53, 137, 138, 139)
    ktchars = 6
    ktespers = 9
    ktdragons = 0
    ktbosses = 0
    if ktcard == 50:
        ktchars = 8
        ktespers = 12
        kt = '.'.join(
            [' -' + obj_prefix[obj_count] + ' 2.2.2.2', str(ktchars), str(ktchars), '4', str(ktespers), str(ktespers)])
        obj_count += 1
    elif ktcard == 51:
        ktchars = 5
        ktespers = 8
        kt = '.'.join(
            [' -' + obj_prefix[obj_count] + ' 2.2.2.2', str(ktchars), str(ktchars), '4', str(ktespers), str(ktespers)])
        obj_count += 1
    elif ktcard == 52:
        ktdragons = 4
        kt = '.'.join(
            [' -' + obj_prefix[obj_count] + ' 2.3.3.2', str(ktchars), str(ktchars), '4', str(ktespers), str(ktespers),
             '6',
             str(ktdragons), str(ktdragons)])
        obj_count += 1
    elif ktcard == 53:
        ktbosses = 16
        kt = '.'.join(
            [' -' + obj_prefix[obj_count] + ' 2.3.3.2', str(ktchars), str(ktchars), '4', str(ktespers), str(ktespers),
             '8',
             str(ktbosses), str(ktbosses)])
        obj_count += 1
    elif ktcard == 137:
        ktchars = 7
        ktespers = 10
        kt = '.'.join(
            [' -' + obj_prefix[obj_count] + ' 2.2.2.2', str(ktchars), str(ktchars), '4', str(ktespers), str(ktespers)])
        obj_count += 1
    elif ktcard == 138:
        ktespers = 10
        kt = '.'.join([' -' + obj_prefix[obj_count] + ' 2.1.1.4', str(ktespers), str(ktespers)])
        obj_count += 1
    elif ktcard == 139:
        kt = '.'.join([' -' + obj_prefix[obj_count] + ' 2.1.1.10.18.18'])
        obj_count += 1
    else:
        kt = '.'.join(
            [' -' + obj_prefix[obj_count] + ' 2.2.2.2', str(ktchars), str(ktchars), '4', str(ktespers), str(ktespers)])
        obj_count += 1

    skipcard = await last_card(cards, 54, 55, 56, 57, 58, 59)
    if skipcard == 54:
        kt += '.'.join(
            [' -' + obj_prefix[obj_count] + ' 3.1.1.2', str(ktchars + 3), str(ktchars + 3), '4', str(ktespers + 3),
             str(ktespers + 3)])
        obj_count += 1
    elif skipcard == 55:
        kt += '.'.join([' -' + obj_prefix[obj_count] + ' 3.1.1.2', str(ktchars + 3), str(ktchars + 3)])
        obj_count += 1
    elif skipcard == 56:
        kt += '.'.join([' -' + obj_prefix[obj_count] + ' 3.1.1.4', str(ktespers + 3), str(ktespers + 3)])
        obj_count += 1
    elif skipcard == 57:
        kt += '.'.join([' -' + obj_prefix[obj_count] + ' 3.1.1.8.12.12'])
        obj_count += 1
    elif skipcard == 58:
        kt += '.'.join([' -' + obj_prefix[obj_count] + ' 3.1.1.10', str(ktespers + ktchars + ktdragons + 5),
                        str(ktespers + ktchars + ktdragons + 5)])
        obj_count += 1
    elif skipcard == 59:
        kt += '.'.join([' -' + obj_prefix[obj_count] + ' 3.3.3.3.r.5.r.7.r.11.r.9.r'])
        obj_count += 1

    # Objective Cards
    objectives = ''
    if 90 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 62.2.2.11.44.7.4.5.26'])
        obj_count += 1
    if 91 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 61.2.2.11.19.11.55.12.9'])
        obj_count += 1
    if 92 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 59.1.1.11.31'])
        obj_count += 1
    if 93 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 59.1.1.11.19'])
        obj_count += 1
    if 94 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 30.8.8.1.1.11.8'])
        obj_count += 1
    if 95 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 30.8.8.1.1.11.31'])
        obj_count += 1
    if 96 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 28.24.24.1.1.11.14'])
        obj_count += 1
    if 97 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 28.24.24.1.1.11.40'])
        obj_count += 1
    if 98 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 26.8.8.1.1.11.26'])
        obj_count += 1
    if 99 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 26.8.8.1.1.11.19'])
        obj_count += 1
    if 100 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 37.1.1.11.48'])
        obj_count += 1
    if 101 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 38.1.1.6.2.2'])
        obj_count += 1
    if 102 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 36.1.1.6.2.2'])
        obj_count += 1
    if 103 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 40.1.1.12.4'])
        obj_count += 1
    if 104 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 58.1.1.12.5'])
        obj_count += 1
    if 105 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 58.1.1.12.2'])
        obj_count += 1
    if 106 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 39.1.1.11.26'])
        obj_count += 1
    if 107 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 45.20.20.1.1.12.9'])
        obj_count += 1
    if 108 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 46.20.20.1.1.12.9'])
        obj_count += 1
    if 109 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 48.20.20.1.1.12.9'])
        obj_count += 1
    if 110 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 45.20.20.1.1.6.4.4'])
        obj_count += 1
    if 111 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 46.20.20.1.1.6.4.4'])
        obj_count += 1
    if 112 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 48.20.20.1.1.6.4.4'])
        obj_count += 1
    if 143 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 59.1.1.10.12.12'])
        obj_count += 1
    if 146 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 45.10.10.1.1.12.9'])
        obj_count += 1
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 48.10.10.1.1.12.9'])
        obj_count += 1
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 46.10.10.1.1.12.9'])
        obj_count += 1

    # Boss/Enemy/Dragon Level Boosts
    if 36 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 22.10.10.0.0'])
        obj_count += 1
    if 39 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 23.10.10.0.0'])
        obj_count += 1
    if 42 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 21.10.10.0.0'])
        obj_count += 1

    # Challenge Objectives
    if 118 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 11.0.0'])
        obj_count += 1
    if 119 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 6.0.0'])
        obj_count += 1
    if 120 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 15.0.0'])
        obj_count += 1
    if 121 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 5.0.0'])
        obj_count += 1
    if 122 in cards:
        objectives += '.'.join([' -' + obj_prefix[obj_count] + ' 12.0.0'])
        obj_count += 1

    game = ''.join([settings, kt, objectives])

    # -----PARTY-----
    # party builder
    # determine the starting party size (cards 27/28)
    party_size_card = await last_card(cards, 27, 28)
    if party_size_card == 27:
        party_size = 2
    elif party_size_card == 28:
        party_size = 4
    else:
        party_size = 3

    # build a list of all party member cards
    print(f'the cards in this draft are {cards}')
    party_cards = []
    for num in cards:
        if 1 <= num <= 26:
            party_cards.append(num)
    print(f'the party-related cards in this one are {party_cards}')

    # go through the list of party member cards and remove the older of any conflicting multiples
    if len(party_cards) > 1:
        for cardnum in range(1, 13):
            if cardnum in party_cards and (cardnum + 14) in party_cards:
                if await last_card(party_cards, cardnum, cardnum + 14) == cardnum:
                    party_cards = remove_card(party_cards, cardnum + 14)
                elif await last_card(party_cards, cardnum, cardnum + 14) == (cardnum + 14):
                    party_cards = remove_card(party_cards, cardnum)

    #remove the earliest of any duplicate cards
    party_cards = remove_earliest_duplicates(party_cards)

    # drop the earliest drafted cards with conflicts if we have too many party cards
    if len(party_cards) > party_size:
        party_cards = party_cards[(len(party_cards) - party_size):]

    print(f'after removing and downsizing to party size cap and removing duplicates, the party-related cards in this one are {party_cards}')



    sc_list = []
    for count, x in enumerate(party_cards):
        if x == 1 or x == 15:
            sc_list.append(''.join([' -sc', str(count + 1), ' terra']))
        elif x == 2 or x == 16:
            sc_list.append(''.join([' -sc', str(count + 1), ' locke']))
        elif x == 3 or x == 17:
            sc_list.append(''.join([' -sc', str(count + 1), ' cyan']))
        elif x == 4 or x == 18:
            sc_list.append(''.join([' -sc', str(count + 1), ' shadow']))
        elif x == 5 or x == 19:
            sc_list.append(''.join([' -sc', str(count + 1), ' edgar']))
        elif x == 6 or x == 20:
            sc_list.append(''.join([' -sc', str(count + 1), ' sabin']))
        elif x == 7 or x == 21:
            sc_list.append(''.join([' -sc', str(count + 1), ' celes']))
        elif x == 8 or x == 22:
            sc_list.append(''.join([' -sc', str(count + 1), ' strago']))
        elif x == 9 or x == 23:
            sc_list.append(''.join([' -sc', str(count + 1), ' relm']))
        elif x == 10 or x == 24:
            sc_list.append(''.join([' -sc', str(count + 1), ' setzer']))
        elif x == 11 or x == 25:
            sc_list.append(''.join([' -sc', str(count + 1), ' mog']))
        elif x == 12 or x == 26:
            sc_list.append(''.join([' -sc', str(count + 1), ' gau']))
        elif x == 13:
            sc_list.append(''.join([' -sc', str(count + 1), ' gogo']))
        elif x == 14:
            sc_list.append(''.join([' -sc', str(count + 1), ' umaro']))

    while len(sc_list) < party_size:
        sc_list.append(''.join([' -sc', str(len(sc_list) + 1), ' random']))

    sparty = ''.join(sc_list)

    # SWORDTECHS
    # fst = random.choices([' -fst', ''], weights=([1, 0]), k=1)[0]
    # sel = random.choices([' -sel', ''], weights=([1, 5]), k=1)[0]
    swdtech = ' -fst'

    # BLITZES
    # brl = random.choices([' -brl', ''], weights=([10, 1]), k=1)[0]
    # bel = random.choices([' -bel', ''], weights=([1, 10]), k=1)[0]
    blitz = ' -brl'

    # LORES
    slr1 = 3
    slr2 = 6
    # slrr = ' '.join([' -slr', str(slr1), str(slr2)])
    # slr = random.choices([slrr, ''], weights=([10, 1]), k=1)[0]
    slr = ' '.join([' -slr', str(slr1), str(slr2)])
    # lmprp1 = random.randint(75, 100)
    # lmprp2 = random.randint(lmprp1, 125)
    # lmprv1 = random.randint(20, 40)
    # lmprv2 = random.randint(lmprv1, 75)
    # lmprp = ' '.join([' -lmprp', str(lmprp1), str(lmprp2)])
    # lmprv = ' '.join([' -lmprv', str(lmprv1), str(lmprv2)])
    # loremp = random.choices(['', ' -lmps', lmprp, lmprv], weights=([1, 3, 10, 3]), k=1)[0]
    loremp = ' -lmprp 75 125'
    # lel = random.choices([' -lel', ''], weights=([1, 0]), k=1)[0]
    lel = ' -lel'
    lores = ''.join([slr, loremp, lel])

    # RAGES
    # srr1 = random.randint(0, 10)
    # srr2 = random.randint(srr1, 25)
    # srr = ' '.join([' -srr', str(srr1), str(srr2)])
    # srages = random.choices(['', srr], weights=([1, 13]), k=1)[0]
    srages = ' -srr 25 35'
    # rnl = random.choices([' -rnl', ''], weights=([1, 0]), k=1)[0]
    # rnc = random.choices([' -rnc', ''], weights=([15, 1]), k=1)[0]
    rage = ''.join([srages, ' -rnl', ' -rnc'])

    # DANCES
    '''
    sdr1 = random.randint(0, 2)
    sdr2 = random.randint(sdr1, 4)
    sdr = ' '.join([' -sdr', str(sdr1), str(sdr2)])
    das = random.choices([' -das', ''], weights=([1, 0]), k=1)[0]
    dda = random.choices([' -dda', ''], weights=([1, 0]), k=1)[0]
    dns = random.choices([' -dns', ''], weights=([1, 0]), k=1)[0]
    d_el = random.choices([' -del', ''], weights=([0, 1]), k=1)[0]
    dance = ''.join([sdr, das, dda, dns, d_el])
    '''
    dance = ' -sdr 1 2 -das -dda -dns'

    # STEAL CHANCES
    # steal = random.choice(['', ' -sch', ' -sch', ' -sca', ' -sca', ' -sca'])
    steal = ' -sch'

    # SKETCH/CONTROL
    sketch = ' -scis'

    # CHARACTERS
    # sal = random.choices([' -sal', ''], weights=([13, 1]), k=1)[0]
    # sn = random.choices([' -sn', ''], weights=([1, 13]), k=1)[0]
    sal = ' -sal'
    sn = ''
    # eu = random.choices([' -eu', ''], weights=([13, 1]), k=1)[0]
    eu = ' -eu'
    # csrp1 = random.randint(90, 120)
    # csrp2 = random.randint(csrp1, 130)
    stats_card = await last_card(cards, 29, 30, 31, 32, 33)
    if stats_card == 29:
        csrp1 = 60
        csrp2 = 90
    elif stats_card == 30:
        csrp1 = 20
        csrp2 = 60
    elif stats_card == 31:
        csrp1 = 110
        csrp2 = 140
    elif stats_card == 32:
        csrp1 = 140
        csrp2 = 200
    elif stats_card == 33:
        csrp1 = 10
        csrp2 = 200
    else:
        csrp1 = 85
        csrp2 = 120

    csrp = ' '.join([' -csrp', str(csrp1), str(csrp2)])
    cstats = ''.join([sal, sn, eu, csrp])

    # COMMANDS
    # scc = random.choices([' -scc', ''], weights=([1, 10]), k=1)[0]
    scc = ''
    command_card = await last_card(cards, 86, 87, 88, 89)
    if command_card == 88:
        command_list = ['03', '05', '07', '08', '09', '10', '11', '12', '13', '15', '19', '16', '97']
    elif command_card == 89:
        command_list = ['99', '99', '99', '99', '99', '99', '99', '99', '99', '99', '99', '99', '99']
    else:
        command_list = ['98', '98', '98', '98', '98', '98', '98', '98', '98', '98', '98', '98', '98']
    # hard code commands based on party cards
    if 1 in party_cards:
        command_list[0] = '03'
    if 2 in party_cards:
        command_list[1] = '05'
    if 3 in party_cards:
        command_list[2] = '07'
    if 4 in party_cards:
        command_list[3] = '08'
    if 5 in party_cards:
        command_list[4] = '09'
    if 6 in party_cards:
        command_list[5] = '10'
    if 7 in party_cards:
        command_list[6] = '11'
    if 8 in party_cards:
        command_list[7] = '12'
    if 9 in party_cards:
        command_list[8] = '13'
    if 10 in party_cards:
        command_list[9] = '15'
    if 11 in party_cards:
        command_list[10] = '19'
    if 12 in party_cards:
        command_list[11] = '16'
    if 15 in party_cards:
        command_list[0] = '29'
    if 16 in party_cards:
        command_list[1] = '06'
    if 17 in party_cards:
        command_list[2] = '08'
    if 18 in party_cards:
        command_list[3] = '07'
    if 19 in party_cards:
        command_list[4] = '22'
    if 20 in party_cards:
        command_list[5] = '07'
    if 21 in party_cards:
        command_list[6] = '27'
    if 22 in party_cards:
        command_list[7] = '26'
    if 23 in party_cards:
        command_list[8] = '23'
    if 24 in party_cards:
        command_list[9] = '09'
    if 25 in party_cards:
        command_list[10] = '22'
    if 26 in party_cards:
        command_list[11] = '06'

    # com = random.choices([' -com 99999999999999999999999999', '', ' -com 98989898989898989898989898'],
    #                     weights=([2, 1, 13]), k=1)[0]
    com = ' -com '
    com += ''.join(command_list)
    # recskills = ['10', '6', '14', '19', '24', '26', '22', '12', '3', '28', '16', '11', '27', '13', '15', '5',
    #             '7', '8', '9', '23', '29']
    if command_card == 86:
        rec1 = ' -rec1 28'
        rec2 = ' -rec2 14'
        rec3 = ' -rec3 11'
        rec4 = ' -rec4 13'
        rec5 = ' -rec5 05'
        rec6 = ' -rec6 24'
    elif command_card == 87:
        rec1 = ' -rec1 28'
        rec2 = ' -rec2 29'
        rec3 = ' -rec3 08'
        rec4 = ' -rec4 27'
        rec5 = ' -rec5 10'
        rec6 = ' -rec6 07'
    else:
        rec1 = ' -rec1 28'
        rec2 = ' -rec2 27'
        rec3 = ''
        rec4 = ''
        rec5 = ''
        rec6 = ''

    commands = ''.join([scc, com, rec1, rec2, rec3, rec4, rec5, rec6])

    party = ''.join([sparty, swdtech, blitz, lores, rage, dance, cstats, commands, steal, sketch])

    # -----BATTLE-----
    # XP, GP, MP growth rates
    '''
    xpm = ' '.join([' -xpm', str(random.choices([2, 3, 4], weights=([1, 10, 1]), k=1)[0])])
    gpm = ' '.join([' -gpm', str(random.choices([4, 5, 6], weights=([1, 10, 1]), k=1)[0])])
    mpm = ' '.join([' -mpm', str(random.choices([4, 5, 6], weights=([1, 10, 1]), k=1)[0])])
    '''
    batreward_card = await last_card(cards, 48, 49)
    if batreward_card == 48:
        xpm = ' -xpm 4'
        gpm = ' -gpm 6'
        mpm = ' -mpm 6'
    elif batreward_card == 49:
        xpm = ' -xpm 2'
        gpm = ' -gpm 4'
        mpm = ' -mpm 4'
    else:
        xpm = ' -xpm 3'
        gpm = ' -gpm 5'
        mpm = ' -mpm 5'

    if 113 in cards:
        nxppd = ''
    else:
        nxppd = ' -nxppd'

    # nxppd = random.choices([' -nxppd', ''], weights=([13, 1]), k=1)[0]
    xpmpgp = ''.join([xpm, gpm, mpm, nxppd])

    # BOSSES
    boss_card = await last_card(cards, 34, 35)
    if boss_card == 34:
        bb = ''
    elif boss_card == 35:
        bb = ' -bbr'
    else:
        bb = ' -bbs'

    if 37 in cards:
        stloc = ' -stloc shuffle'
    elif boss_card == 34:
        stloc = ' -stloc original'
    else:
        stloc = ' -stloc mix'

    # bb = random.choices([' -bbr', ' -bbs', ''], weights=([1, 13, 1]), k=1)[0]
    if boss_card == 34:
        drloc = ' -drloc original'
    elif 38 in cards:
        drloc = ' -drloc mix'
    else:
        drloc = ' -drloc shuffle'
    # bmbd = random.choices([' -bmbd', ''], weights=([0, 1]), k=1)[0]
    srp3 = ''
    # srp3 = random.choices([' -srp3', ''], weights=([0, 1]), k=1)[0]
    if 115 in cards:
        bnds = ' -bnds'
    else:
        bnds = ''
    # bnds = random.choices([' -bnds', ''], weights=([1, 13]), k=1)[0]
    if 117 in cards:
        be = ''
    else:
        be = ' -be'
    # be = random.choices([' -be', ''], weights=([1, 0]), k=1)[0]
    bnu = ' -bnu'
    # bnu = random.choices([' -bnu', ''], weights=([10, 1]), k=1)[0]
    bosses = ''.join([bb, drloc, stloc, srp3, bnds, be, bnu])

    # BOSS AI
    '''
    dgne = random.choices([' -dgne', ''], weights=([1, 0]), k=1)[0]
    wnz = random.choices([' -wnz', ''], weights=([1, 0]), k=1)[0]
    mmnu = random.choices([' -mmnu', ''], weights=([1, 0]), k=1)[0]
    cmd = random.choices([' -cmd', ''], weights=([1, 0]), k=1)[0]
    '''
    dgne = ' -dgne'
    wnz = ' -wnz'
    mmnu = ' -mmnu'
    cmd = ' -cmd'
    b_ai = ''.join([dgne, wnz, mmnu, cmd])

    # SCALING
    '''
    scale_opt = ['0.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']
    lspf = ' '.join([' -lsced', random.choices(scale_opt, weights=([0, 1, 1, 10, 2, 1, 0, 0, 0, 0]), k=1)[0]])
    lsaf = ' '.join([' -lsa', random.choices(scale_opt, weights=([0, 13, 1, 0, 0, 0, 0, 0, 0, 0]), k=1)[0]])
    lshf = ' '.join([' -lsh', random.choices(scale_opt, weights=([0, 13, 1, 0, 0, 0, 0, 0, 0, 0]), k=1)[0]])
    lstf = ' '.join([' -lst', random.choices(scale_opt, weights=([0, 1, 5, 10, 1, 0, 0, 0, 0, 0]), k=1)[0]])
    hmpf = ' '.join([' -hmced', random.choices(scale_opt, weights=([0, 1, 1, 10, 2, 1, 0, 0, 0, 0]), k=1)[0]])
    hmaf = ' '.join([' -hma', random.choices(scale_opt, weights=([0, 13, 1, 0, 0, 0, 0, 0, 0, 0]), k=1)[0]])
    hmhf = ' '.join([' -hmh', random.choices(scale_opt, weights=([0, 13, 1, 0, 0, 0, 0, 0, 0, 0]), k=1)[0]])
    hmtf = ' '.join([' -hmt', random.choices(scale_opt, weights=([0, 1, 5, 10, 1, 0, 0, 0, 0, 0]), k=1)[0]])
    xgpf = ' '.join([' -xgced', random.choices(scale_opt, weights=([0, 1, 1, 10, 2, 1, 0, 0, 0, 0]), k=1)[0]])
    xgaf = ' '.join([' -xga', random.choices(scale_opt, weights=([0, 13, 1, 0, 0, 0, 0, 0, 0, 0]), k=1)[0]])
    xghf = ' '.join([' -xgh', random.choices(scale_opt, weights=([0, 13, 1, 0, 0, 0, 0, 0, 0, 0]), k=1)[0]])
    xgtf = ' '.join([' -xgt', random.choices(scale_opt, weights=([0, 1, 5, 10, 1, 0, 0, 0, 0, 0]), k=1)[0]])
    asrf = ' '.join([' -asr', random.choices(scale_opt, weights=([0, 0, 1, 10, 2, 1, 0, 0, 0, 0]), k=1)[0]])
    asef = ' '.join([' -ase', random.choices(scale_opt, weights=([0, 0, 1, 10, 2, 1, 0, 0, 0, 0]), k=1)[0]])

    lscale = random.choices([lspf, lsaf, lshf, lstf, ''], weights=([15, 2, 2, 1, 0]), k=1)[0]
    hmscale = random.choices([hmpf, hmaf, hmhf, hmtf, ''], weights=([15, 2, 2, 1, 0]), k=1)[0]
    xgscale = random.choices([xgpf, xgaf, xghf, xgtf, ''], weights=([15, 2, 2, 1, 0]), k=1)[0]
    ascale = random.choices([asrf, asef, ''], weights=([1, 13, 0]), k=1)[0]

    msl = ' '.join([' -msl', str(random.randint(40, 60))])
    '''
    scale_card = await last_card(cards, 43, 44, 45, 46, 47, 144)
    if scale_card == 43:
        lscale = ' -lsced 4'
        hmscale = ' -hmced 1'
        xgscale = ' -xgced 2.5'
        msl = ' -msl 70'
    elif scale_card == 44:
        lscale = ' -lsced 3'
        hmscale = ' -hmced 2.5'
        xgscale = ' -xgced 2'
        msl = ' -msl 60'
    elif scale_card == 45:
        lscale = ' -lsced 2.5'
        hmscale = ' -hmced 2.5'
        xgscale = ' -xgced 2'
        msl = ' -msl 50'
    elif scale_card == 46:
        lscale = ' -lsce 2'
        hmscale = ' -hmce 2'
        xgscale = ' -xgce 2.5'
        msl = ' -msl 50'
    elif scale_card == 47:
        lscale = ' -lsh 1'
        hmscale = ' -hmh 1'
        xgscale = ' -xgh 1'
        msl = ' -msl 50'
    elif scale_card == 144:
        lscale = ' -lsc 2.5'
        hmscale = ' -hmc 2.5'
        xgscale = ' -xgc 2'
        msl = ' -msl 50'
    else:
        lscale = ' -lsced 2'
        hmscale = ' -hmced 2'
        xgscale = ' -xgced 2'
        msl = ' -msl 40'

    if 132 in cards:
        sed = ''
    else:
        sed = ' -sed'

    if 116 in cards:
        ascale = ' -asr 2'
    else:
        ascale = ' -ase 2'

    sfb = ''
    # sfb = random.choices([' -sfb', ''], weights=([0, 1]), k=1)[0]
    # sed = random.choices([' -sed', ''], weights=([13, 1]), k=1)[0]
    scaling = ''.join([lscale, hmscale, xgscale, ascale, msl, sfb, sed])

    # ENCOUNTERS
    '''
    renc = random.choices(['', ' -res', ' '.join([' -rer', str(random.randint(0, 10))])], weights=([1, 10, 10]), k=1)[0]
    fenc = random.choices(['', ' '.join([' -fer', str(random.randint(0, 10))])], weights=([1, 13]), k=1)[0]
    escr = ' -escr 100'
    '''
    if 40 in cards:
        renc = ' -rer 20'
    else:
        renc = ' -res'

    if 41 in cards:
        fenc = ' -fer 20'
    else:
        fenc = ' -fer 0'
    escr = ' -escr 100'

    encounters = ''.join([renc, fenc, escr])

    battle = ''.join([bosses, b_ai, scaling, encounters, xpmpgp])

    # -----MAGIC-----
    # ESPERS
    '''
    esr1 = random.randint(1, 3)
    esr2 = random.randint(esr1, 5)
    esr = ' '.join([' -esr', str(esr1), str(esr2)])
    ess = random.choices(['', esr, ' -esrr', ' -ess', ' -essrr', ' -esrt'], weights=([1, 13, 2, 2, 2, 3]), k=1)[0]
    ebonus = random.choices(['', ' '.join([' -ebr', str(random.randint(67, 100))]), ' -ebs'], weights=([1, 10, 2]),
                            k=1)[0]
    emprp1 = random.randint(75, 100)
    emprp2 = random.randint(emprp1, 125)
    emprv1 = random.randint(25, 75)
    emprv2 = random.randint(emprv1, 99)
    eer1 = random.randint(6, 12)
    eer2 = random.randint(eer1, 12)
    emprp = ' '.join([' -emprp', str(emprp1), str(emprp2)])
    emprv = ' '.join([' -emprv', str(emprv1), str(emprv2)])
    emp = random.choices(['', emprp, emprv, ' -emps'], weights=([1, 10, 1, 3]), k=1)[0]
    eer = ' '.join([' -eer', str(eer1), str(eer2)])
    eebr = ' '.join([' -eebr', str(random.randint(6, 12))])
    eeq = random.choices([eer, eebr, ''], weights=([1, 1, 15]), k=1)[0]
    ems = random.choices(['', ' -ems'], weights=([13, 1]), k=1)[0]
    '''
    if 85 in cards:
        stesp = ' -stesp 1 1'
    else:
        stesp = ''

    esper_card = await last_card(cards, 79, 80, 142, 145)
    if esper_card == 79:
        esr1 = 3
        esr2 = 5
        ebonus = ' -ebr 100'
        emprp1 = 50
        emprp2 = 80
        ems = ' -ems'
    elif esper_card == 80:
        esr1 = 0
        esr2 = 2
        ebonus = ' -ebr 20'
        emprp1 = 100
        emprp2 = 150
        ems = ''
    else:
        esr1 = 1
        esr2 = 4
        ebonus = ' -ebr 75'
        emprp1 = 75
        emprp2 = 125
        ems = ''
    if esper_card == 142:
        ess = ''
        ebonus = ''
        emp = ''
        eeq = ''
        ems = ''
    elif esper_card == 145:
        ess = ' -esrt'
        ebonus = ' -ebr 75'
        emp = ' -emprp 75 125'
        eeq = ''
        ems = ' -ems'
    else:
        ess = ' '.join([' -esr', str(esr1), str(esr2)])
        emp = ' '.join([' -emprp', str(emprp1), str(emprp2)])
        eeq = ''

    espers = ''.join([stesp, ess, ebonus, emp, eeq, ems])

    # NATURAL MAGIC
    '''
    nm1 = random.choices(['', ' -nm1 random'], weights=([0, 1]), k=1)[0]
    nm2 = random.choices(['', ' -nm2 random'], weights=([0, 1]), k=1)[0]
    rnl1 = random.choices(['', ' -rnl1'], weights=([0, 1]), k=1)[0]
    rnl2 = random.choices(['', ' -rnl2'], weights=([0, 1]), k=1)[0]
    rns1 = random.choices(['', ' -rns1'], weights=([0, 1]), k=1)[0]
    rns2 = random.choices(['', ' -rns2'], weights=([0, 1]), k=1)[0]
    '''
    nat_card = await last_card(cards, 76, 77, 78)
    if nat_card == 76:
        nm1 = ''
        nm2 = ''
    elif nat_card == 77:
        nm1 = ' -nm1 terra'
        nm2 = ' -nm2 celes'
    elif nat_card == 78:
        nm1 = ' -nm1 strago'
        nm2 = ' -nm2 relm'
    else:
        nm1 = ' -nm1 random'
        nm2 = ' -nm2 random'
    rnl1 = ' -rnl1'
    rnl2 = ' -rnl2'
    rns1 = ' -rns1'
    rns2 = ' -rns2'
    m_indicator = ' -nmmi'
    nmagic = ''.join([nm1, nm2, rnl1, rnl2, rns1, rns2, m_indicator])

    # MAGIC MP COSTS AND ULTIMA
    mp_card = await last_card(cards, 81, 82, 83)
    if mp_card == 81:
        mmprp1 = 25
        mmprp2 = 75
    elif mp_card == 82:
        mmprp1 = 125
        mmprp2 = 175
    elif mp_card == 83:
        mmprp1 = 25
        mmprp2 = 175
    else:
        mmprp1 = 75
        mmprp2 = 125

    mmp = ' '.join([' -mmprp', str(mmprp1), str(mmprp2)])

    # remove learnable spells - cards 123,124,125
    rls_list = []
    if 123 in cards:
        rls_list.append('black')
    if 124 in cards:
        rls_list.append('white')
    if 125 in cards:
        rls_list.append('gray')
    if len(rls_list) > 0:
        rls = ' -rls ' + ','.join(rls_list)
    else:
        rls = ''

    if 84 in cards:
        ultima = ' -u254'
    else:
        ultima = ''

    mmagic = ''.join([mmp, rls, ultima])

    magic = ''.join([espers, nmagic, mmagic])

    # -----ITEMS-----
    # STARTING GOLD/ITEMS
    '''
    gp = ' '.join([' -gp', str(random.randint(0, 20000))])
    smc = ' -smc 3'
    sws = ' '.join([' -sws', str(random.randint(0, 7))])
    sfd = ' '.join([' -sfd', str(random.randint(0, 7))])
    sto = ' '.join([' -sto', str(random.randint(0, 4))])
    '''
    smc = ' -smc 3'
    start_card = await last_card(cards, 60, 61, 62)
    if start_card == 60:
        gp = ' -gp 0'
        sws = ' -sws 0'
        sfd = ' -sfd 0'
        sto = ' -sto 0'
    elif start_card == 61:
        gp = ' -gp 30000'
        sws = ' -sws 5'
        sfd = ' -sfd 5'
        sto = ' -sto 1'
    elif start_card == 62:
        gp = ' -gp 100000'
        sws = ' -sws 10'
        sfd = ' -sfd 10'
        sto = ' -sto 2'
    else:
        gp = ' -gp 5000'
        sws = ' -sws 0'
        sfd = ' -sfd 0'
        sto = ' -sto 1'
    s_inv = ''.join([gp, smc, sfd, sto, sws])

    # ITEMS
    '''
    ier1 = random.randint(7, 14)
    ier2 = random.randint(ier1, 14)
    ier = ' '.join([' -ier', str(ier1), str(ier2)])
    iebr = ' '.join([' -iebr', str(random.randint(7, 14))])
    ieor = ' '.join([' -ieor', str(random.randint(33, 100))])
    iesr = ' '.join([' -iesr', str(random.randint(33, 100))])
    iequip = random.choices(['', ier, iebr, ieor, iesr], weights=([1, 1, 1, 13, 1]), k=1)[0]
    ierr1 = random.randint(7, 14)
    ierr2 = random.randint(ierr1, 14)
    ierr = ' '.join([' -ierr', str(ierr1), str(ierr2)])
    ierbr = ' '.join([' -ierbr', str(random.randint(7, 14))])
    ieror = ' '.join([' -ieror', str(random.randint(33, 100))])
    iersr = ' '.join([' -iersr', str(random.randint(33, 100))])
    requip = random.choices(['', ierr, ierbr, ieror, iersr], weights=([1, 1, 1, 13, 1]), k=1)[0]
    '''
    equip_card = await last_card(cards, 65, 66, 67)
    if equip_card == 65:
        iequip = ' -ieor 100'
        requip = ' -ieror 100'
    elif equip_card == 66:
        iequip = ' -iebr 7'
        requip = ' -ierbr 7'
    elif equip_card == 67:
        iequip = ''
        requip = ''
    else:
        iequip = ' -ieor 33'
        requip = ' -ieror 33'

    curse_card = await last_card(cards, 63, 64)
    if curse_card == 63:
        csb1 = 1
        csb2 = 32
    elif curse_card == 64:
        csb1 = 1
        csb2 = 8
    else:
        csb1 = 5
        csb2 = 13
    # csb1 = random.randint(1, 32)
    # csb2 = random.randint(csb1, 32)
    csb = ' '.join([' -csb', str(csb1), str(csb2)])

    # mca = random.choices([' -mca', ''], weights=([1, 0]), k=1)[0]
    mca = ' -mca'
    # stra = random.choices([' -stra', ''], weights=([1, 0]), k=1)[0]
    stra = ' -stra'
    # saw = random.choices([' -saw', ''], weights=([1, 0]), k=1)[0]
    saw = ' -saw'
    equips = ''.join([iequip, requip, csb, mca, stra, saw])

    # SHOPS
    shop_card = await last_card(cards, 68, 69, 70, 71, 133, 140, 141)
    if shop_card == 68:
        shopinv = ' -sirt'
        sprp1 = 50
        sprp2 = 150
        ssf = ''
    elif shop_card == 69:
        shopinv = ' -sisr 10'
        sprp1 = 30
        sprp2 = 80
        ssf = ''
    elif shop_card == 70:
        shopinv = ' -sisr 50'
        sprp1 = 120
        sprp2 = 160
        ssf = ' -ssf4'
    elif shop_card == 71:
        shopinv = ''
        sprp1 = 100
        sprp2 = 100
        ssf = ''
    elif shop_card == 133:
        shopinv = ' -sie'
        sprp1 = 50
        sprp2 = 150
        ssf = ' -ssf8'
    elif shop_card == 140:
        shopinv = ' -sisr 60'
        sprv1 = 2000
        sprv2 = 2000
        ssf = ''
    elif shop_card == 141:
        shopinv = ' -sisr 60'
        sprv1 = 0
        sprv2 = 0
        ssf = ' -ssf0'
    else:
        shopinv = ' -sisr 20'
        sprp1 = 75
        sprp2 = 125
        ssf = ''
    if shop_card == 140 or shop_card == 141:
        shopprices = ' '.join([' -sprv', str(sprv1), str(sprv2)])
    else:
        shopprices = ' '.join([' -sprp', str(sprp1), str(sprp2)])
    sdm = ' -sdm 5'
    npi = ' -npi'

    toy_card = await last_card(cards, 75, 134)
    if toy_card == 75:
        snbr = ' -snbr'
        snes = ' -snes'
        snsb = ' -snsb'
    elif toy_card == 134:
        snbr = ''
        snes = ''
        snsb = ''
    else:
        snbr = ' -sebr'
        snes = ''
        snsb = ' -sesb'
    '''
    sisr = ' '.join([' -sisr', str(random.randint(20, 40))])
    shopinv = random.choices(['', sisr, ' -sirt', ' -sie'], weights=([1, 13, 3, 0]), k=1)[0]
    sprv1 = random.randint(0, 65535)
    sprv2 = random.randint(sprv1, 65535)
    sprp1 = random.randint(75, 100)
    sprp2 = random.randint(sprp1, 125)
    sprv = ' '.join([' -sprv', str(sprv1), str(sprv2)])
    sprp = ' '.join([' -sprp', str(sprp1), str(sprp2)])
    shopprices = random.choices(['', sprv, sprp], weights=([1, 2, 15]), k=1)[0]
    ssf = random.choices(['', ' -ssf4', ' -ssf8', ' -ssf0'], weights=([13, 1, 1, 0]), k=1)[0]
    sdm = ' '.join([' -sdm', str(random.randint(4, 5))])
    npi = random.choices(['', ' -npi'], weights=([0, 1]), k=1)[0]
    snbr = random.choices(['', ' -snbr'], weights=([13, 1]), k=1)[0]
    snes = random.choices(['', ' -snes'], weights=([13, 1]), k=1)[0]
    snsb = random.choices(['', ' -snsb'], weights=([13, 1]), k=1)[0]
    '''
    shops = ''.join([shopinv, shopprices, ssf, sdm, npi, snbr, snes, snsb])

    # CHESTS
    chest_card = await last_card(cards, 72, 73, 74, 135, 136)
    cms = ' -cms'
    if chest_card == 72:
        ccontents = ' -ccsr 100'
    elif chest_card == 73:
        ccontents = ' -ccrt'
    elif chest_card == 74:
        ccontents = ' -ccrs'
    elif chest_card == 135:
        ccontents = ''
        cms = ''
    elif chest_card == 136:
        ccontents = ' -cce'
    else:
        ccontents = ' -ccsr 20'

    # ccontents = random.choices(['', ' -ccrt', ' -cce', ' '.join([' -ccsr', str(random.randint(20, 40))])],
    #                           weights=([1, 3, 0, 13]), k=1)[0]
    # cms = random.choices(['', ' -cms'], weights=([0, 1]), k=1)[0]
    chests = ''.join([ccontents, cms])

    items = ''.join([s_inv, equips, shops, chests])

    # -----CUSTOM-----
    # SEE CUSTOM_SPRITES_PORTRAITS.PY

    # -----OTHER-----
    # COLISEUM
    '''
    co = random.choices(['', ' -cor', ' -cos'], weights=([0, 13, 1]), k=1)[0]
    cr = random.choices(['', ' -crs', ' -crr'], weights=([0, 1, 13]), k=1)[0]
    crvr1 = random.randint(30, 50)
    crvr2 = random.randint(crvr1, 75)
    visible = random.choices(['', ' '.join([' -crvr', str(crvr1), str(crvr2)])], weights=([0, 1]), k=1)[0]
    rmenu = random.choices(['', ' -crm'], weights=([1, 13]), k=1)[0]
    colo = ''.join([co, cr, visible, rmenu])
    '''
    colo = ' -cor -crr -crvr 50 60 -crm'

    # AUCTION HOUSE
    '''
    ari = random.choices(['', ' -ari'], weights=([0, 1]), k=1)[0]
    anca = random.choices(['', ' -anca'], weights=([0, 1]), k=1)[0]
    adeh = random.choices(['', ' -adeh'], weights=([0, 1]), k=1)[0]
    ah = ''.join([ari, anca, adeh])
    '''
    ah = ' -ari -anca -adeh'

    # MISC
    '''
    asprint = random.choices(['', ' -as'], weights=([0, 1]), k=1)[0]
    ond = random.choices(['', ' -ond'], weights=([0, 1]), k=1)[0]
    rr = random.choices(['', ' -rr'], weights=([0, 1]), k=1)[0]
    scan = random.choices(['', ' -scan'], weights=([1, 0]), k=1)[0]
    etimers = random.choices(['', ' -etr', ' -etn'], weights=([5, 1, 0]), k=1)[0]
    ychoices = [' -ymascot', ' -ycreature', ' -yimperial', ' -ymain', ' -yreflect', ' -ystone', ' -ysketch',
                ' -yrandom', ' -yremove', '']
    ychoice = random.choices(ychoices, weights=([1, 1, 1, 1, 1, 1, 1, 1, 1, 13]), k=1)[0]
    flashes = random.choice(['', ' -frm', ' -frw'])
    '''
    asprint = ' -as'
    ond = ' -ond'
    rr = ' -rr'
    scan = ''
    etimers = ' -etn'
    y_card = await last_card(cards, 126, 127)
    if y_card == 126:
        ychoice = ' -yremove'
    elif y_card == 127:
        ychoice = ' -yvxz'
    else:
        ychoice = ''
    flashes = ' -frw'
    hdmap = ' -wmhc'
    misc = ''.join([asprint, ond, rr, scan, etimers, ychoice, flashes, hdmap])

    # CHALLENGES
    # nmc = random.choices(['', ' -nmc'], weights=([1, 5]), k=1)[0]
    nmc = ' -nmc'
    if 147 in cards:
        ame = ' -ame 0'
    else:
        ame = ' -ame 2'
    # noshoes = random.choices(['', ' -noshoes'], weights=([1, 5]), k=1)[0]
    noshoes = ' -noshoes'
    # nee = random.choices(['', ' -nee'], weights=([13, 1]), k=1)[0]
    if 129 in cards:
        nee = ' -nee'
    else:
        nee = ''
    # nil = random.choices(['', ' -nil'], weights=([1, 5]), k=1)[0]
    if 130 in cards:
        nil = ' -nil'
    else:
        nil = ''
    # nfps = random.choices(['', ' -nfps'], weights=([0, 1]), k=1)[0]
    if curse_card == 64:
        nfps = ''
    else:
        nfps = ' -nfps'
    # nu = random.choices(['', ' -nu'], weights=([1, 10]), k=1)[0]
    if 84 in cards:
        nu = ''
    else:
        nu = ' -nu'
    # nfp = random.choices(['', ' -nfce'], weights=([13, 1]), k=1)[0]
    if 128 in cards:
        nfp = ' -nfce'
    else:
        nfp = ''
    pd = random.choices(['', ' -pd'], weights=([1, 0]), k=1)[0]
    if 114 in cards:
        pd = ' -pd'
    else:
        pd = ''
    challenges = ''.join([nmc, ame, noshoes, nee, nil, nfps, nu, nfp, pd])

    # BUG FIXES
    '''
    fs = random.choices(['', ' -fs'], weights=([0, 1]), k=1)[0]
    fe = random.choices(['', ' -fe'], weights=([0, 1]), k=1)[0]
    fvd = random.choices(['', ' -fvd'], weights=([0, 1]), k=1)[0]
    fr = random.choices(['', ' -fr'], weights=([0, 1]), k=1)[0]
    fj = random.choices(['', ' -fj'], weights=([0, 1]), k=1)[0]
    fbs = random.choices(['', ' -fbs'], weights=([0, 1]), k=1)[0]
    fedc = random.choices(['', ' -fedc'], weights=([0, 1]), k=1)[0]
    bugfixes = ''.join([fs, fe, fvd, fr, fj, fbs, fedc])
    '''
    bugfixes = ' -fs -fe -fvd -fr -fj -fbs -fedc -fc'

    other = ''.join([colo, ah, challenges, misc, bugfixes])

    flagset = ''.join([game, party, battle, magic, items, other])
    return flagset