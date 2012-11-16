# initial code to set up Python ACT-R
import ccm
from ccm.lib.actr import *
log=ccm.log(html=True)

# define the model
class RepeatedBinaryChoiceModel(ACTR):
    goal=Buffer()
    
    pmnoise=PMNoise(noise=0.3)
    pm=PMNew(alpha=0.2)
    
    def pressA(goal='action:choose'):
        self.reward(0.3)
        
    def pressB(goal='action:choose'):
        self.reward(0.1)
        
        
# run the model        
model=RepeatedBinaryChoiceModel()
ccm.log_everything(model)
model.goal.set('action:choose')
model.run(limit=1.5)


