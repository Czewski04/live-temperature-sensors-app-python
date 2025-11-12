import numpy as np


class Voter:
    def __init__(self):
        self.avg = False
        self.median = False


    def average_voting(self, data):
        return np.average(data)


    def median_voting(self, data):
        return np.median(data)


    def vote(self, data):
        results = {}
        if self.avg:
            results['Average'] = self.average_voting(data)
        if self.median:
            results['Median'] = self.median_voting(data)
        return results

    def update_votes(self, avg, median):
        self.avg = avg
        self.median = median