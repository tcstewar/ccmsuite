# initial code to set up Python ACT-R
import ccm
from ccm.lib.actr import *
log=ccm.log(html=True)

# define the model
class ExpertCountingModel(ACTR):
    goal=Buffer()
    imaginal=Buffer()

    def countFromOne(goal='action:counting target:!one',imaginal='number:one'):
        imaginal.set('number:two')        
    def countFromTwo(goal='action:counting target:!two',imaginal='number:two'):
        imaginal.set('number:three')        
    def countFromThree(goal='action:counting target:!three',imaginal='number:three'):
        imaginal.set('number:four')        
    def countFromFour(goal='action:counting target:!four',imaginal='number:four'):
        imaginal.set('number:five')        
    def countFromFive(goal='action:counting target:!five',imaginal='number:five'):
        imaginal.set('number:six')        
    def countFromSix(goal='action:counting target:!six',imaginal='number:six'):
        imaginal.set('number:seven')        
    def countFromSeven(goal='action:counting target:!seven',imaginal='number:seven'):
        imaginal.set('number:eight')        
    def countFromEight(goal='action:counting target:!eight',imaginal='number:eight'):
        imaginal.set('number:nine')        
    def countFromNine(goal='action:counting target:!nine',imaginal='number:nine'):
        imaginal.set('number:ten')        
        
    def countFinished(goal='action:counting target:?x',imaginal='number:?x'):
        print 'Finished counting to',x
        goal.clear()
        
        
# run the model        
model=ExpertCountingModel()
ccm.log_everything(model)
model.goal.set('action:counting target:five')
model.imaginal.set('number:one')
model.run()


