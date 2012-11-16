import ccm
log=ccm.log(html=True)

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
agent.body.color='blue'
world.add(agent,x=5,y=3)

agent2=MyAgent()
agent2.body.color='green'
world.add(agent2,x=9,y=6)

agent3=MyAgent()
agent3.body.color='red'
world.add(agent3,x=2,y=6)

ccm.log_everything(agent,log.blue)
ccm.log_everything(agent2,log.green)
ccm.log_everything(agent3,log.red)

ccm.display(world)
world.run()
