salience_weight=0.25
fixed_weight=-0.2
latency=1

import ccm
log=ccm.log()

from ccm.lib.actr import *

class FanModel(ACTR):
  focus=Buffer()
  retrieval=Buffer()
  memory=Memory(retrieval,latency=latency)
  fixed=DMFixed(memory,default=fixed_weight)

  salience=DMSalience(memory)
  salience.weights(_0=salience_weight,_2=salience_weight)
  
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
    salience.context('? in ?')
    focus.set('wait')
    
  def wait(focus='wait',top='person:?person!None location:?location!None'):
    focus.set('test ?person ?location')
    retrieval.clear()
    
  def start_recall(focus='test ?person ?location'):
    memory.request('?person in ?location')
    focus.set('recall ?person ?location')
    
  def respond_yes(focus='recall ?person ?location',
                  retrieval='?person in ?location'):
    top.sayYes()
    focus.set('wait')
  def respond_no(focus='recall ?person ?location',
                        memory='error:True'):
    top.sayNo()
    focus.set('wait')



tests={
 (1,1):('lawyer','store'),
 (1,2):('captain','cave'),
 (1,3):('hippie','church'),
 (2,1):('debutante','bank'),
 (2,2):('earl','castle'),
 (2,3):('hippie','bank'),
 (3,1):('fireman','park'),
 (3,2):('captain','park'),
 (3,3):('hippie','park'),
 }
 
persons=[None,'lawyer','captain','hippie']
locations=[None,'store','bank','park']

class FanTest(ccm.Model):
  def start(self):
    data={}
    for fan1 in [1,2,3]:
      for fan2 in [1,2,3]:
        t1=self.now()
        # visual perception time:
        yield 0.47
        
        self.person,self.location=tests[fan2,fan1]
        yield self.sayYes,self.sayNo
        self.person=None
        self.location=None
        
        # motor time
        yield 0.21
        rt=self.now()-t1
        log.y[fan1,fan2]=rt
        data[fan1,fan2]=rt
    
  def sayYes(self):
    pass#log.yes=True
  def sayNo(self):
    pass#log.yes=False


env=FanTest()
env.model=FanModel()
env.run()    
