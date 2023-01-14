import os.path as osp
import pickle as pkl

class Course(object):
    """
    A "Course" here is defined as any number of holes that you play.

    It is a collection of Holes
    """

    def __init__(self, course_name, holes=None):
        self.name = course_name
        self.savename = course_name.replace(' ', '_') + '.pkl'
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
        file_loc = osp.abspath(__file__)
        save_path = osp.join('data', 'courses', self.savename)
        return save_path

    def __str__(self):
        retstr = """Course name: %s
Length: %d holes
Par: %d strokes
Distance: %d Yards""" % (self.name, self.course_len, self.total_par, self.total_yds)
        return retstr
