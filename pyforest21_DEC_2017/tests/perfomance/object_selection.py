'''
Created on May 20, 2016

Profile of tree selection

@author: dmitry
'''

# model initialization
from . import *

import cProfile, pstats, StringIO
pr = cProfile.Profile()



pr.enable()
for k in range(1000):
    model.objects.select_by_stages(['seedling'])
pr.disable()

s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print s.getvalue()




