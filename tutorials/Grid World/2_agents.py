import ccm
log=ccm.log()

from ccm.lib import grid
from ccm.lib.actr import *

mymap="""
################
#              #
#              #
#              #
######### ######
#     #        #
#     #        #
#              #
################
"""

class MyCell(grid.Cell):
    def color(self):
        if self.wall: return 'black'
        else: return 'white'
    def load(self,char):      
        if char=='#': self.wall=True


class MyAgent(ACTR):
    focus=Buffer()
    body=grid.Body()

    def init():
        focus.set('wander')

    def wandering_forward(focus='wander'):
        body.go_forward()

    def wandering_left(focus='wander'):
        body.turn_left()
        body.go_forward()

    def wandering_right(focus='wander'):
        body.turn_right()
        body.go_forward()
            

world=grid.World(MyCell,map=mymap)
agent=MyAgent()
world.add(agent,x=5,y=3)
ccm.display(world)
world.run()
