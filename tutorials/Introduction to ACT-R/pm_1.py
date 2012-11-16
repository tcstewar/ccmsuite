# initial code to set up Python ACT-R
import ccm
from ccm.lib.actr import *
log=ccm.log()

# define the model
class MyModel(ACTR):
    goal=Buffer()
    
    def greeting(goal='action:greet'):
        print "Hello"
        goal.clear()
        
# run the model        
model=MyModel()
ccm.log_everything(model)
model.goal.set('action:greet')
model.run()


