class Hole(object):
    """
    A hole has a yardage, par, handicap, and notes
    """

    def __init__(self, number, yards, par, stroke_index, total_holes=9.0, comments=""):
        self.hole_num = number
        self.yds = yards
        self.par = par
        self.stroke_index = stroke_index
        self.adjusted_index = stroke_index / float(total_holes)
        self.comments = comments

    def get_yds(self):
        return self.yds

    def get_par(self):
        return self.par

    def __str__(self):
        return """Hole Number: %d
Yards: %d
Par:   %d
Handicap: %d
        """ % (self.hole_num, self.yds, self.par, self.stroke_index)