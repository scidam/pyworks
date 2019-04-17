'''
Created on May 20, 2016

Simple action with loop (sawl): perfomance testing module

@author: dmitry
'''

# model initialization
from . import *
from pyforest.actions.death import KillRandomlyAction

import cProfile, pstats, StringIO
pr = cProfile.Profile()

action = KillRandomlyAction()
model.insert_action(action)


pr.enable()
for i in range(100):
    model.actions[0].activate()
pr.disable()

s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print s.getvalue()
