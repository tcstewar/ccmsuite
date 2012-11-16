# initial code to set up Python ACT-R
import ccm
from ccm.lib.actr import *
log=ccm.log()

# define the model
class MyModel(ACTR):
    goal=Buffer()
    
    def greeting1(goal='action:greet style:casual person:?name'):
        print "Hi",name
        goal.clear()
        
    def greeting2(goal='action:greet style:formal person:?name'):
        print "Greetings",name
        goal.clear()
        
        
        
# run the model        
model=MyModel()
ccm.log_everything(model)
model.goal.set('action:greet style:formal person:Terry')
model.run()


