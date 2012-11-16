import ccm
log=ccm.log()

from ccm.lib import grid

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

world=grid.World(MyCell,map=mymap)
ccm.display(world)
world.run()
