import ccm
log=ccm.log()

from ccm.lib.actr import *

class Env(ccm.Model):
  result=[]
  def say(self,x):
    self.result.append(x)
    log.x=x

class Grouped(ACTR):
  focus=Buffer()
  retrieval=Buffer()
  memory=Memory(retrieval,threshold=-0.5,latency=1)
  noise=DMNoise(memory,0.15)
  partial=Partial(memory)
  partial.similarity('first','second',-0.5)
  partial.similarity('second','third',-0.5)
  result=[]
  
  def init():
    memory.add('name:group1 parent:list position:first')
    memory.add('parent:group1 name:1 position:first')
    memory.add('parent:group1 name:2 position:second')
    memory.add('parent:group1 name:3 position:third')
    memory.add('name:group2 parent:list position:second')
    memory.add('parent:group2 name:4 position:first')
    memory.add('parent:group2 name:5 position:second')
    memory.add('parent:group2 name:6 position:third')
    memory.add('name:group3 parent:list position:third')
    memory.add('parent:group3 name:7 position:first')
    memory.add('parent:group3 name:8 position:second')
    memory.add('parent:group3 name:9 position:third')
    focus.set('start list')
    
  def recall_first_group(focus='start ?list'):
    focus.set('group first ?list')
    memory.request('parent:?list position:first')
    
  def start_recall_of_group(focus='group ?gpos ?list',retrieval='name:?groupname'):
    memory.request('parent:?groupname position:first')
    focus.set('item pos:first groupname:?groupname gpos:?gpos list:?list')
    retrieval.clear()
    
  def harvest_first_item(focus='item pos:first groupname:?groupname',retrieval='name:?x'):
    self.parent.say(x)
    focus.modify(pos='second')
    memory.request('parent:?groupname position:second')
    retrieval.clear()

  def harvest_second_item(focus='item pos:second groupname:?groupname',retrieval='name:?x'):
    self.parent.say(x)
    focus.modify(pos='third')
    memory.request('parent:?groupname position:third')
    retrieval.clear()

  def harvest_third_item(focus='item pos:third groupname:?groupname',retrieval='name:?x'):
    self.parent.say(x)
    focus.modify(pos='fourth')
    memory.request('parent:?groupname position:fourth')
    retrieval.clear()
    
  def second_group(focus='item gpos:first list:?list',memory='error:True'):
    memory.request('parent:?list position:second')
    focus.set('group second ?list')
    retrieval.clear()
    
  def third_group(focus='item gpos:second list:?list',memory='error:True'):
    memory.request('parent:?list position:third')
    focus.set('group third ?list')
    retrieval.clear()
    
env=Env()
env.m=Grouped()
env.run()      
log.result=env.result        
    
    
    
  
