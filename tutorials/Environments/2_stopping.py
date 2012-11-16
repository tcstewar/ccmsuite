# CCM Suite Environment Tutorial 2
#
# The purpose of this tutorial is to enhance the previous tutorial
#  so that it keeps track of the total score and stops after 200 trials.


import ccm
log=ccm.log()

class ForcedChoiceEnvironment(ccm.Model):
  score=0            # for storing the total score
  trials=0           # for storing the number of trials so far
  

  def press(self,letter):
    log.action=letter
    if letter=='A':
      self.reward=1
    else:  
      self.reward=0
      
    self.score=self.score+self.reward  
    log.score=self.score         # record the score in the log
      
    self.trials=self.trials+1    # increase the number of trials
    log.trials=self.trials       # record the number of trials
    if self.trials==20:         # if the number of trials is 200
       self.stop()               #  stop the simulation


class SimpleModel(ccm.Model):
  def start(self):
    while True:
      self.parent.press('A')
      yield 1
      
      
      
model=SimpleModel()
env=ForcedChoiceEnvironment()
env.agent=model
env.run()
