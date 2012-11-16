# CCM Suite Environment Tutorial 3
#
# The purpose of this tutorial is to expand the previous one
#  so that we are measuring something specific about the
#  agent's performance.  In this case, we want to measure
#  the proportion of time they press 'A' in the first 100
#  trials, and the proportion of time they press 'A' in the
#  second 100 trials.  We call these Pmax1 and Pmax2, to be
#  consistent with (Erev and Barron, 2005).

import ccm
log=ccm.log()

class ForcedChoiceEnvironment(ccm.Model):
  score=0
  trials=0

  def press(self,letter):
    log.action=letter
    if letter=='A':
      self.reward=1
    else:  
      self.reward=0
      
    self.score=self.score+self.reward        
    log.score=self.score
      
    self.trials=self.trials+1
    log.trials=self.trials
 
    # on the 100th trial,
    if self.trials==100:     
      # calculate Pmax1 by taking the current score and dividing by 100
      log.Pmax1=self.score/100.0         # Note: we are dividing by 100.0
                                         # instead of 100 because Python,
                                         # like most programming languagues,
                                         # only keeps decimal places in the
                                         # answer if there are decimal places
                                         # to start with.  So 2/3 is 0, but
                                         # 2/3.0 or 2.0/3 is 0.6666666666.
      self.score=0   # reset the score
      
    # on the 200th trial,  
    if self.trials==200:
      # calculate Pmax2 by taking the current score and dividing by 100
      log.Pmax2=self.score/100.0
      
      # stop the simulation
      self.stop()


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
