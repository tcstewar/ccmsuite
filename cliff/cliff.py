import sys
sys.path.append('.')

import ccm
from ccm.lib import grid
from ccm.lib import continuous

map="""
..............
.SXXXXXXXXXXG.
.            .
.            .
.            .
..............
"""

class Cell(grid.Cell):
    start_cell=None
    def __init__(self):
        self.cliff=False
        self.goal=False
        self.wall=False
    def color(self):
        if self.cliff: return 'red'
        if self.goal: return 'green'
        if self.wall: return 'black'
        else: return 'white'
    def load(self,data):
        if data=='S': Cell.start_cell=self
        if data=='.': self.wall=True
        if data=='X': self.cliff=True
        if data=='G': self.goal=True


import random

class Agent(continuous.Body):
    def __init__(self):
        grid.Body.__init__(self)
    def colour(self):
        return 'blue'
    
    def start(self):
        pass
        #while True:
        #    self.turn(random.uniform(-0.1, 0.1))
        #    self.go_forward(0.05)
        #    yield 0.01
            

class World(grid.World):
    def key_pressed(self, key):
        if key=='w':
            agent.go_forward(0.1)
        if key=='s':
            agent.go_forward(-0.1)
        if key=='a':
            agent.turn(-0.1)
        if key=='d':
            agent.turn(0.1)
        


world=World(Cell,map=map,directions=6)

agent=Agent()
world.add(agent,cell=Cell.start_cell, dir=0)

ccm.display(world)
world.run()
