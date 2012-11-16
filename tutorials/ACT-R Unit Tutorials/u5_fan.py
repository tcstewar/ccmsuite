import ccm

from ccm.lib.actr import *

class FanModel(ACTR):
  focus=Buffer()
  retrieval=Buffer()
  memory=Memory(retrieval,latency=0.63)
  spread=DMSpreading(memory,focus)
  spread.strength=1.6
  spread.weight[focus]=0.5
  
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
    focus.set('wait')
    
  def wait(focus='wait',top='style:?style!None person:?person!None location:?location!None'):
    focus.set('test ?style ?person ?location')
    retrieval.clear()
    
  def start_person(focus='test byperson ?person ?location'):
    memory.request('?person in ?')
    focus.set('recall ?person ?location')
  def start_location(focus='test bylocation ?person ?location'):
    memory.request('? in ?location')
    focus.set('recall ?person ?location')
    
  def respond_yes(focus='recall ?person ?location',
                  retrieval='?person in ?location'):
    top.sayYes()
    focus.set('wait')
  def respond_no_person(focus='recall ?person ?location',
                        retrieval='? in !?location'):
    top.sayNo()
    focus.set('wait')
  def respond_no_location(focus='recall ?person ?location',
                        retrieval='!?person in ?'):
    top.sayNo()
    focus.set('wait')

log=ccm.log()


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
    for fan1 in [1,2,3]:
      for fan2 in [1,2,3]:
       value=None
       for style in ['byperson','bylocation']:
        t1=self.now()
        # visual perception time:
        yield 0.47
        
        self.style=style
        self.person,self.location=tests[fan2,fan1]
        yield self.sayYes,self.sayNo
        self.style=None
        self.person=None
        self.location=None
        
        # motor time
        yield 0.21
        rt=self.now()-t1
        if value is None: value=rt
        else: value=(value+rt)/2
       log.y[fan1,fan2]=value
    
  def sayYes(self):
    pass
  def sayNo(self):
    pass


env=FanTest()
env.model=FanModel()
env.run()    
