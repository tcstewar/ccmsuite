from ccm.lib.actr import *

class Semantic(ACTR):
  goal=Buffer()
  retrieve=Buffer()
  memory=Memory(retrieve)

  text=TextOutput()
  
  def init():
    memory.add('property shark dangerous true')
    memory.add('property shark locomotion swimming')
    memory.add('property shark category fish')
    memory.add('property fish category animal')
    memory.add('property bird category animal')
    memory.add('property canary category bird')
    
  def initialRetrieve(goal='isMember ?obj ?cat result:None'):
    goal.modify(result='pending')
    memory.request('property ?obj category ?')

  def directVerify(goal='isMember ?obj ?cat result:pending',
                   retrieve='property ?obj category ?cat'):
    goal.modify(result='yes')
    text.write('Yes')

  def chainCategory(goal='isMember ?obj1 ?cat result:pending',
                    retrieve='property ?obj1 category ?obj2!?cat'):
    goal.modify(_1=obj2)
    memory.request('property ?obj2 category ?')

  def fail(goal='isMember ?obj1 ?cat result:pending',memory='error:True'):
    goal.modify(result='no')
    text.write('No')


model=Semantic()
model.goal.set('isMember shark fish result:None')
model.run()
model.goal.set('isMember shark animal result:None')
model.run()
model.goal.set('isMember canary fish result:None')
model.run()

