class Course(object):
    """
    A "Course" here is defined as any number of holes that you play.

    It is a collection of Holes
    """

    def __init__(self, course_name, holes=None):
        self.name = course_name
        self.course_len = len(holes)
        self.holes = [] if holes is None else holes

        self.total_yds = 0
        self.total_par = 0

        for hole in self.holes:
            yds = hole.get_yds()
            par = hole.get_par()
            self.total_yds += yds
            self.total_par += par

    def __str__(self):
        retstr = """"""
        return retstr
