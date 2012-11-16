# CCM Suite Environment Tutorial 5
#
# The purpose of this tutorial is to demonstrate an
#  alternate method of creating environments.  Here,
#  the environment is divided up into Objects, and
#  the objects can be acted upon.  This can help
#  organize a complex environment.
#
# In this example, we are going to have two buttons
#  (button1 and button2) and a display that will
#  show the reward.  button1 and button2 have a special
#  'press' action that we hae defined.

import ccm
log=ccm.log()


class Button(ccm.Model):
    def press(self):
        log.action=self.letter
        self.parent.display.reward=self.reward
        self.parent.score+=self.reward
        self.parent.trials+=1
        if self.parent.trials==200: self.stop()
        
      

class ForcedChoiceEnvironment(ccm.Model):
  trials=0
  score=0
  button1=Button(letter='A',reward=1)
  button2=Button(letter='B',reward=0)
  display=ccm.Model(reward=0)

          

import random
class SimpleModel(ccm.Model):
  def start(self):
    while True:
      choice=random.choice(['A','B'])
      if choice=='A': self.parent.button1.press()
      if choice=='B': self.parent.button2.press()
      yield 1
           
model=SimpleModel()
env=ForcedChoiceEnvironment()
env.agent=model
env.run()
