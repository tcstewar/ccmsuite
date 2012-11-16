from ccm.lib.actr import *

class Count(ACTR):
  goal=Buffer()
  retrieve=Buffer()
  memory=Memory(retrieve)
  
  def init():
    memory.add('count 0 1')
    memory.add('count 1 2')
    memory.add('count 2 3')
    memory.add('count 3 4')
    memory.add('count 4 5')
    memory.add('count 5 6')
    memory.add('count 6 7')
    memory.add('count 7 8')
    memory.add('count 8 9')
    memory.add('count 9 10')

  def start(goal='countFrom ?start ?end starting'):
    memory.request('count ?start ?next')
    goal.set('countFrom ?start ?end counting')

  def increment(goal='countFrom ?x !?x counting',
                retrieve='count ?x ?next'):
    print x
    memory.request('count ?next ?nextNext')
    goal.modify(_1=next)

  def stop(goal='countFrom ?x ?x counting'):
    print x
    goal.set('countFrom ?x ?x stop')

model=Count()
model.goal.set('countFrom 2 5 starting')
model.run()

