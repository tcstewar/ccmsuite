# CCM Suite Environment Tutorial 1
#
# The purpose of this tutorial is to make a simple environment
#  where an agent is capable of pressing either button 'A' or 'B'.
#  If they press 'A', they get one point, and if they press 'B' they
#  get 0 points.

import ccm                        # this is needed to make use of CCMSuite
log=ccm.log()                     # this sets up a log for recording data


class ForcedChoiceEnvironment(ccm.Model):
  # this is an action that can be taken by the agent in the environment
  def press(self,letter):     # 'self' refers to the thing we are currently
                              #  of defining.  In this case, the environment
    log.action=letter    # here we record what letter was pressed
    if letter=='A':
      self.reward=1      # if it was 'A', we set the reward to one.  
    else:  
      self.reward=0      # otherwise, set it to zero.


# This defines a simple agent.  We will examine this in more detail in the
#  tutorials on creating models
class SimpleModel(ccm.Model):
  def start(self):
    while True:               # repeat the following forever
      self.parent.press('A')
      yield 1                 # wait for 1 second before continuing
      

# Now that the agent and the environment have been defined, we can create
#  one of each, connect them together, and run the simulation.      
env=ForcedChoiceEnvironment()   # create the environment
model=SimpleModel()             # create the agent
env.agent=model                 # put the agent in the environment
env.run()                       # run the simulation.
