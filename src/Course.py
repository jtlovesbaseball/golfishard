import json
import os.path as osp
import pickle as pkl
from collections import OrderedDict


class Course(object):
    """
    A "Course" here is defined as any number of holes that you play.

    It is a collection of Holes
    """

    def __init__(self, course_name, holes=None):
        self.name = course_name
        self.savename = course_name.replace(' ', '_') + '.pkl'

        save_path = osp.join('data', 'courses', self.savename)

        if osp.exists(save_path):
            print("Loading from Saved")
            loaded = pkl.load(open(save_path, 'rb'))
            self.course_len = loaded.course_len
            self.holes = loaded.holes
        else:
            print("Creating new course")
            self.course_len = len(holes)
            self.holes = [] if holes is None else holes

        self.total_yds = 0
        self.total_par = 0

        for hole in self.holes:
            yds = hole.get_yds()
            par = hole.get_par()
            self.total_yds += yds
            self.total_par += par

    def save_path(self):
        save_path = osp.join('data', 'courses', self.savename)
        return save_path

    def save(self, force=False):
        if osp.exists(self.save_path()) and not force:
            print("Already saved, use force=True to overwrite")
            return
        filehandler = open(self.save_path(), 'wb')
        pkl.dump(self, filehandler)
        filehandler.close()
        print("Save Successful")

    def play(self, golfer, scores, date, ttt=None, comments=""):
        """
        Hey this one sounds fun lets play golf

        :param golfer: name of golfer
        :param scores: list of scores (NO LYING*!)
        :param date: python datetime object
        :param ttt: tee time temperature
        :param comments: anything you'd like to add?
        :return: a line, like it's a csv
        """
        scorestr = ""
        parstr = ""
        for score, hole in zip(scores, self.holes):
            scorestr += "%d," % score
            parstr += "%d," % hole.get_par()
        scorestr = scorestr[:-1]
        parstr = parstr[:-1]

        named_strokes, final_score = Course.get_named_strokes(scores, [x.get_par() for x in self.holes])
        named_str = json.dumps(named_strokes, separators=(',', ': '))
        timestr = date.strftime('%A_%m_%d_%Y_%H:%M')
        course_savename = self.savename
        retstr = "%s,%s,%s,%s,%s,%s,%d,%s,%d,%s\n" % (golfer, course_savename, scorestr, parstr, named_str,
                                                      self.total_par + final_score, self.total_par,
                                                      timestr, ttt, comments if len(comments) > 0 else "none")
        return retstr

    @staticmethod
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

    @staticmethod
    def get_named_final_score(score):
        retstr = ""

    def __str__(self):
        retstr = """Course name: %s
Length: %d holes
Par: %d strokes
Distance: %d Yards""" % (self.name, self.course_len, self.total_par, self.total_yds)
        return retstr
