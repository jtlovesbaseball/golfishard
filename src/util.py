import datetime
import json
import os.path as osp
import pickle as pkl
from copy import deepcopy
from collections import OrderedDict


def generate_pretty_text(names):
    retstr = ''
    for name in names:
        ez = name.replace('{', '')
        ez = ez.replace('}', '')
        indicies = []
        for idx, letter in enumerate(ez):
            if letter == '\"':
                indicies.append(idx)
        ez_name = ez[indicies[0] + 1: indicies[1]]
        ez_num = int(ez[indicies[1] +2:].strip())
        retstr += '%12s : %2d\n' % (ez_name, ez_num)
    return retstr


def generate_ascii_table(parstr, scorestr, yds=None, sis=None, handicap=None):
    """
    Generates ascii score table
    :param parstr: Pars
    :param scorestr:
    :param yds:
    :param sis:
    :return:
    """
    ROW_WID = 67
    retstr = '-' * ROW_WID
    retstr += '\n'
    holes = [x + 1 for x in range(len(parstr))]
    par = [int(x) for x in parstr]
    score = [int(x) for x in scorestr]
    diff = [x - y for x, y in zip(score, par)]
    targets = deepcopy(par) if handicap is not None else None
    if handicap is not None:
        remain = handicap
        while remain > 0:
            for i in range(9):
                si_index = i + 1
                index_to_increment = sis.index(si_index)
                targets[index_to_increment] += 1
                remain -= 1
    hcap = [x - y for x, y in zip(score, targets)]
    order = {'HOLE': holes, 'YDS ': yds, 'SI  ': sis, 'PAR ': par, 'TRGT': targets,
             'SHOT': score, 'SCRE': diff, 'HCAP': hcap}
    for row in order:
        values = order[row]
        if values is None:  # Practicers of terrorism or veganism for instance
            continue
        retstr += "|%-5s|" % row
        for value in values:
            if row == 'YDS ':
                retstr += ' %3d |' % value
            else:
                retstr += '  %2d |' % value
        if row == 'HOLE':
            retstr += ' TOT |'
        elif row == 'SI  ':
            retstr += '     |'
        elif row == 'YDS ':
            retstr += '%4d |' % sum(values)
        elif row == 'SCRE' and sum(diff) > 0:
            retstr += ' +%2d |' % sum(values)
        elif row == 'HCAP':
            if sum(hcap) <= 0:
                retstr += ' %2d |' % sum(values)
            else:
                retstr += ' +%2d |' % sum(values)
        else:
            retstr += '  %2d |' % sum(values)
        retstr += '\n'
        retstr += ('-' * ROW_WID)
        retstr += '\n'
    return retstr, hcap, targets


def analyze(game_str, print_from_fx=True, apply_handicap=True):
    """
    Analyzes the game, and returns some human readable text about the players performance

    :param game_str: Game string we want (returned from .play() fx or from games_played.csv)
    :param print_from_fx: if false only returns game string analysis
    :return: game string analysis
    """
    game_split = game_str.split(',')
    begin_named, end_named= -1, -1
    for gs in game_split:
        if '{' in gs:
            begin_named = game_split.index(gs)
        if '}' in gs:
            end_named = game_split.index(gs)

    if begin_named == 20:
        pass
    else:
        print("Proably an 18 hole course")
        return 'General panic and anxiety'
    player = game_split[0]
    course = game_split[1]
    coursepklpath = osp.join(osp.abspath('.'), 'data', 'courses', course)
    yds, sis = None, None
    if osp.exists(coursepklpath):
        coursedata = pkl.load(open(coursepklpath, 'rb'))
        yds = [hole.get_yds() for hole in coursedata.holes]
        sis = [hole.stroke_index for hole in coursedata.holes]
    scorestr = game_split[2:11]
    parstr = game_split[11:begin_named]
    named_str = game_split[begin_named: end_named + 1]
    date_str = game_split[-3]
    handicap_9 = calculate_handicap(player, date_str)
    ascii_table, hcap, targets = generate_ascii_table(parstr, scorestr, yds, sis, handicap_9)

    named_pretty = generate_pretty_text(named_str)
    named_hcap, _fs = get_named_strokes([int(x) for x in scorestr], targets)
    named_hcap_pretty = ""
    for nh in named_hcap:
        named_hcap_pretty += "%-13s: %2d\n" % (nh, named_hcap[nh])
    tot_strokes = sum([int(x) for x in scorestr])
    tot_par = sum([int(x) for x in parstr])
    tot_target = sum(targets)
    rank = tot_strokes - tot_par
    rank = '(+' + str(rank) + ')'
    hcap_rank = tot_strokes - tot_target
    target_rank = '(+' + str(hcap_rank) + ')'
    if hcap_rank < 0:
        target_rank = str.replace(target_rank, '+', '')
    retstr = """Player: %s (Handicap %.1f (18 Hole))
Course: %s
Date: %s
%s
Raw %s:
%s
With Handicap % s:
%s
Total Score: %d
    """ % (player, handicap_9 * 2, course.split('.')[0], date_str,
           ascii_table, rank, named_pretty, target_rank,
           named_hcap_pretty, tot_strokes)

    return retstr


def calculate_handicap(player, date_str, clip=False):
    """
    Calculates a players handicap on a 9 hole segment

    :param player: player we are searching for
    :return: handicap on a 9 hole course
    """
    game_file = open(osp.join(osp.abspath('.'), 'data', 'games', 'games_played.csv'))
    scores = []
    for line in game_file:
        lnsp = line.split(',')
        if lnsp[0] != player:
            continue
        game_date = lnsp[-3]
        game_date_split = game_date.split('_')
        game_month, game_day, game_year = int(game_date_split[1]), int(game_date_split[2]), int(game_date_split[3])

        this_date = date_str
        this_date_split = this_date.split('_')

        this_month, this_day, this_year = int(this_date_split[1]), int(this_date_split[2]), int(this_date_split[3])

        if(datetime.datetime(month=game_month, day=game_day, year=game_year) >=
                datetime.datetime(month=this_month, day=this_day, year=this_year)):
            break

        shot = int(lnsp[-5])
        par  = int(lnsp[-4])
        score = shot - par
        scores.append(score)
    if len(scores) < 3 or not clip:
        scores.append(24)  # Seed score
    else:
        scores.sort()
        scores = scores[1:-1]  # Remove the best and worst if you've played > 3
    if len(scores) > 25:
        scores = scores[-25:]
    print(scores)
    return float(sum(scores)) / len(scores)

def get_named_strokes(strokes, pars):
    named = {3: 'Triple Bogey', 2: 'Double Bogey', 1: 'Bogey',
             0: 'Par', -1: 'Birdie', -2: 'Eagle', -3: 'Albatross', -4: 'Pterodactyl'}
    ret_dict = OrderedDict()
    differences = [x - y for x, y in zip(strokes, pars)]
    differences.sort()
    cum_score = 0  # haha
    for diff in differences:
        cum_score += diff
        try:
            name = named[diff]
        except:  # +4, +5, the "JT scores"
            name = '+' + str(diff)
        if name not in ret_dict:
            ret_dict[name] = 0
        ret_dict[name] += 1
    return ret_dict, cum_score