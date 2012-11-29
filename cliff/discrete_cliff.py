normal_reward=-1
cliff_reward=-100
goal_reward=0
directions=4
time_limit=10000


import sys
sys.path.append('.')

import ccm
from ccm.lib import grid
from ccm.lib import continuous
from ccm.lib import qlearn

log=ccm.log()

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

class Agent(grid.Body):
    def __init__(self):
        self.ai=qlearn.QLearn(actions=range(directions),epsilon=0.1,alpha=0.1,gamma=0.9)
        self.last_action=None
        self.score=0
    def color(self):
        return 'blue'
    def update(self):
        reward=self.calc_reward()
        state=self.calc_state()
        action=self.ai.chooseAction(state)
        if self.last_action!=None:
          self.ai.learn(self.last_state,self.last_action,reward,state)
        self.last_state=state
        self.last_action=action

        here=self.cell
        if here.goal or here.cliff:
          self.cell=Cell.start_cell
          self.last_action=None
        else:
          self.go_in_direction(action)

    def calc_state(self):
        return self.cell.x,self.cell.y
    def calc_reward(self):
        here=self.cell
        if here.cliff:
            return cliff_reward
        elif here.goal:
            self.score+=1
            return goal_reward
        else:
            return normal_reward


world=grid.World(Cell,map=map,directions=directions)

agent=Agent()
world.add(agent,cell=Cell.start_cell)

#ccm.display(world)
world.run(limit=time_limit)
log.score=agent.score
agent.score=0
world.run(limit=time_limit)
log.score2=agent.score
