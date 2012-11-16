from ccm.lib.actr import *

class Addition(ACTR):
  goal=Buffer()
  retrieve=Buffer()
  memory=Memory(retrieve)  
  
  def init():
    memory.add('addfact 3 4 7')
    memory.add('addfact 6 7 13')
    memory.add('addfact 10 3 13')
    memory.add('addfact 1 7 8')

  def startPair(goal='add ? ?one1 ? ?one2 ? None?ans ?'):
    goal.modify(_6='busy')
    memory.request('addfact ?one1 ?one2 ?')
    
  def addOnes(goal='add ? ? ? ? ? busy?ans ?carry', retrieve='addfact ? ? ?sum'):
    goal.modify(_6=sum,_7='busy')
    memory.request('addfact 10 ? ?sum')
    
  def processCarry(goal='add ?ten1 ? ?ten2 ? None?tenAns ?oneAns busy?carry',retrieve='addfact 10 ?rem ?sum'):
    goal.modify(_6=rem,_7=1,_5='busy')
    memory.request('addfact ?ten1 ?ten2 ?')
    
  def noCarry(goal='add ?ten1 ? ?ten2 None?tenAns ?oneAns busy?carry',memory='error:True'):
    goal.modify(_6=0,_4='busy')
    memory.request('addfact ?ten1 ?ten2 ?')
    
  def addTensDone(goal='add ? ? ? ? busy?tenAns ?oneAns 0',retrieve='addfact ? ? ?sum'):
    print sum,oneAns
    goal.modify(_5=sum)
  def addTensCarry(goal='add ? ? ? ? busy?tenAns ? 1?carry',retrieve='addfact ? ? ?sum'):
    goal.modify(_7=0)
    memory.request('addfact 1 ?sum ?')


model=Addition()
model.goal.set('add 3 6 4 7 None None None')
model.run()

