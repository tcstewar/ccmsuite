import ccm
log=ccm.log()

from ccm.lib import grid
from ccm.lib.actr import *

mymap="""
################
#              #
#              #
#              #
########  ######
#     #        #
#     #       D#
#            DD#
################
"""

class MyCell(grid.Cell):
    dirty=False
    def color(self):
        if self.dirty: return 'brown'
        elif self.wall: return 'black'
        else: return 'white'
    def load(self,char):      
        if char=='#': self.wall=True
        elif char=='D': self.dirty=True

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
    def go_towards(self,x,y):
        if self.busy: return
        self.busy=True
        self.action='going towards %s %s'%(x,y)
        yield 0.4
        self.parent.body.go_towards(x,y)
        self.action=None
        self.busy=False
        
class ObstacleModule(ccm.ProductionSystem):
    production_time=0
    ahead=False
    left=False
    right=False
    def check_ahead(self='ahead:False',body='ahead_cell.wall:True'):
        self.ahead=True
    def check_left(self='left:False',body='left_cell.wall:True'):
        self.left=True
    def check_right(self='right:False',body='right_cell.wall:True'):
        self.right=True
    def check_ahead2(self='ahead:True',body='ahead_cell.wall:False'):
        self.ahead=False
    def check_left2(self='left:True',body='left_cell.wall:False'):
        self.left=False
    def check_right2(self='right:True',body='right_cell.wall:False'):
        self.right=False
                
                
            


class MyAgent(ACTR):
    focus=Buffer()
    body=grid.Body()
    motor=MotorModule()
    obstacle=ObstacleModule()
    
    visual=Buffer()
    vision=Memory(visual)
    visionScanner=grid.VisionScanner(body,vision)

    def init():
        focus.set('wander')
        visual.clear()
    
    def wandering_forward(focus='wander',motor='busy:False',obstacle='ahead:False'):
        motor.go_forward()

    def wandering_left(focus='wander',motor='busy:False',obstacle='left:False'):
        motor.go_left()

    def wandering_right(focus='wander',motor='busy:False',obstacle='right:False'):
        motor.go_right()

    def wandering_dead_end(focus='wander',motor='busy:False',obstacle='right:True left:True ahead:True'):
        motor.go_right()

    def look_for_dirt(focus='wander',vision='busy:False',visual=None):
        vision.request('dirty:True')

    def found_dirt(focus='wander',visual='dirty:True x:?x y:?y'):
        focus.set('go to ?x ?y')

    def go_to_location(focus='go to ?x ?y',motor='busy:False'):
        motor.go_towards(x,y)


class MuddyDog(ACTR):
    focus=Buffer()
    body=grid.Body()
    def init():
        focus.set('wander')
    def wandering_forward(focus='wander'):
        body.go_forward()
        body.cell.dirty=True

    def wandering_left(focus='wander'):
        body.turn_left()

    def wandering_right(focus='wander'):
        body.turn_right()

world=grid.World(MyCell,map=mymap)
agent=MyAgent()
world.add(agent,x=5,y=3)

dog=MuddyDog()
world.add(dog,x=2,y=7)

ccm.log_everything(agent)
ccm.display(world)
world.run()
