import ccm
log=ccm.log()

class MatchEnvironment(ccm.Model):
    def start(self):
        self.count=0
        yield 1   # wait one second
        self.letter=ccm.Model(isa='letter',x=0.5,y=0.5,visible=True)
        self.letter.text=self.random.choice('BCDFGHJKLMNPQRSTVWXYZ')
        self.target=self.letter.text

    def press(self,key):
        self.pressed=key
        if key==self.target:
            log.success=True
        else:
            log.success=False
        self.letter.visible=False
        self.count+=1
        if self.count==10:
            self.stop()
        else:
            yield 1
            self.letter.text=self.random.choice('BCDFGHJKLMNPQRSTVWXYZ')
            self.letter.visible=True
            self.target=self.letter.text
        
from ccm.lib.actr import *
# Define the ACT-R Model    
class Model(ACTR):
  goal=Buffer()
  visual=Buffer()
  vision=SOSVision(visual)
  
  def findUnattendedLetter(goal='attend',vision='busy:False'):
    vision.request('isa:letter')
    goal.set('attend')
    
  def encodeLetter(goal='attend',visual='isa:letter text:?letter'):
    goal.set('respond ?letter')
    
  def respond(goal='respond ?letter'):
    self.parent.press(letter)
    visual.clear()
    goal.set('attend')


env=MatchEnvironment()
env.model=Model()
env.model.goal.set('attend')

ccm.display(env)
    
env.run()
