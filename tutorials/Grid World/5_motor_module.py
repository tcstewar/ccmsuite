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

class MotorModule(ccm.Model):
    busy=False
    def go_forward(self):
        if self.busy: return
        self.busy=True
        self.action='going forward'
        yield 0.4
        self.parent.body.go_forward()
        self.action=None
        self.busy=False
    def go_left(self):
        if self.busy: return
        self.busy=True
        self.action='turning left'
        yield 0.1
        self.parent.body.turn_left()
        self.action='going forward'
        yield 0.3
        self.parent.body.go_forward()
        self.action=None
        self.busy=False
    def go_right(self):
        if self.busy: return
        self.busy=True
        self.action='turning right'
        yield 0.1
        self.parent.body.turn_right()
        self.action='going forward'
        yield 0.3
        self.parent.body.go_forward()
        self.action=None
        self.busy=False
        
        


class MyAgent(ACTR):
    focus=Buffer()
    body=grid.Body()
    motor=MotorModule()

    def init():
        focus.set('wander')

    def wandering_forward(focus='wander',motor='busy:False'):
        motor.go_forward()

    def wandering_left(focus='wander',motor='busy:False'):
        motor.go_left()

    def wandering_right(focus='wander',motor='busy:False'):
        motor.go_right()
            

world=grid.World(MyCell,map=mymap)
agent=MyAgent()
world.add(agent,x=5,y=3)
ccm.display(world)
ccm.log_everything(agent)
world.run()
