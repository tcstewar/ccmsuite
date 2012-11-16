# initial code to set up Python ACT-R
import ccm
from ccm.lib.actr import *
log=ccm.log(html=True)

# define the model
class ExpertCountingModel(ACTR):
    goal=Buffer()

    def countFromOne(goal='action:counting current:one target:!one'):
        goal.modify(current='two')        
    def countFromTwo(goal='action:counting current:two target:!two'):
        goal.modify(current='three')        
    def countFromThree(goal='action:counting current:three target:!three'):
        goal.modify(current='four')        
    def countFromFour(goal='action:counting current:four target:!four'):
        goal.modify(current='five')        
    def countFromFive(goal='action:counting current:five target:!five'):
        goal.modify(current='six')        
    def countFromSix(goal='action:counting current:six target:!six'):
        goal.modify(current='seven')        
    def countFromSeven(goal='action:counting current:seven target:!seven'):
        goal.modify(current='eight')        
    def countFromEight(goal='action:counting current:eight target:!eight'):
        goal.modify(current='nine')        
    def countFromNine(goal='action:counting current:nine target:!nine'):
        goal.modify(current='ten')        
        
    def countFinished(goal='action:counting current:?x target:?x'):
        print 'Finished counting to',x
        goal.clear()
        
        
# run the model        
model=ExpertCountingModel()
ccm.log_everything(model)
model.goal.set('action:counting current:one target:five')
model.run()


