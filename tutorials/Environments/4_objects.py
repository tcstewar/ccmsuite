# CCM Suite Environment Tutorial 4
#
# The purpose of this tutorial is to demonstrate an
#  alternate method of creating environments.  Here,
#  the environment is divided up into Objects, and
#  the objects can be acted upon.  This can help
#  organize a complex environment.
#
# In this example, we are going to have two buttons
#  (buttonA and buttonB) and a display that will
#  show the reward.

import ccm
log=ccm.log()

      

class ForcedChoiceEnvironment(ccm.Model):
  trials=0
  score=0

  # make the buttons  
  button1=ccm.Model(letter='A',reward=1)
  button2=ccm.Model(letter='B',reward=0)
  
  # make the display.  Initially it shows a reward of zero.
  display=ccm.Model(reward=0)


  def press(self,letter):
      if letter==self.button1.letter:
          self.display.reward=self.button1.reward
      elif letter==self.button2.letter:
          self.display.reward=self.button2.reward
          
      self.score=self.score+self.display.reward  
          
      log.action=letter
      self.trials+=1
      if self.trials==200: self.stop()
          

import random
class SimpleModel(ccm.Model):
  def start(self):
    while True:
      choice=random.choice(['A','B'])
      self.parent.press(choice)
      yield 1
           
model=SimpleModel()
env=ForcedChoiceEnvironment()
env.agent=model
env.run()
