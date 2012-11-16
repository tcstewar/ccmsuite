import ccm
from ccm.lib.actr import *
log=ccm.log(html=True)

class FanModel(ACTR):
  goal=Buffer()
  retrieval=Buffer()
  memory=Memory(retrieval,latency=0.63)
  spread=DMSpreading(memory,goal)
  spread.strength=1.6
  spread.weight[goal]=0.5
  
  def init():
    memory.add('hippie in park')
    memory.add('hippie in church')    
    memory.add('hippie in bank')    
    memory.add('captain in park')    
    memory.add('captain in cave')    
    memory.add('debutante in bank')    
    memory.add('fireman in park')    
    memory.add('giant in beach')    
    memory.add('giant in castle')    
    memory.add('giant in dungeon')    
    memory.add('earl in castle')    
    memory.add('earl in forest')    
    memory.add('lawyer in store')
    
  def start_person(goal='test ?person ?location'):
    memory.request('?person in ?')
    goal.set('recall ?person ?location')
  def start_location(goal='test ?person ?location'):
    memory.request('? in ?location')
    goal.set('recall ?person ?location')
    
  def respond_yes(goal='recall ?person ?location',
                  retrieval='?person in ?location'):
    print 'yes'
    goal.clear()

  def respond_no_person(goal='recall ?person ?location',
                        retrieval='? in !?location'):
    print 'no'
    goal.clear()

  def respond_no_location(goal='recall ?person ?location',
                        retrieval='!?person in ?'):
    print 'no'
    goal.clear()



model=FanModel()
ccm.log_everything(model)
model.goal.set('test hippie park')
model.run()

