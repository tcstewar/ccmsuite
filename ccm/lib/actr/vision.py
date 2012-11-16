import ccm

from ccm.pattern import Pattern
from ccm.lib.actr.dm import Finst
from ccm.lib.actr.buffer import Chunk

class Vision(ccm.Model):
  def __init__(self,visual,location):
    ccm.Model.__init__(self)
    self._visual=visual
    self._location=location
    self.busy=False
    self.lastLocationPattern=Pattern('')
    self.tracking=None
    self.timeAppeared={}
    self.visualOnsetSpan=0.5
    self.finst=Finst(self)   
    
  def start(self):
    self.environmentUpdate()
    
  def isNew(self,object):
    if not getattr(object,'visible',True): return
    time=self.timeAppeared.get(object,None)
    if time==None:
      self.timeAppeared[object]=self.now()
      return True
    return self.now()<time+self.visualOnsetSpan
    
  def environmentUpdate(self):
   while True:    
    if self._location.isEmpty():
    
      r=[]
      for o in self.parent.parent.get_children():
        if not getattr(o,'visible',True):
            if o in self.timeAppeared.keys(): del self.timeAppeared[o] 
            continue
        if o not in self.timeAppeared:
          if hasattr(o,'x') and hasattr(o,'y'):  
            #if self.lastLocationPattern.match(o)!=None:
              r.append(o)
      if len(r)>0:
        obj=self.random.choice(r)    
        self.log._='Vision stuffed obj at (%g,%g)'%(obj.x,obj.y)
        self._location.set('%g %g'%(obj.x,obj.y))
    
    #print 'checking tracking',self.tracking  
    #if self.tracking!=None and (self.tracking not in self.parent.parent.get_children() or not getattr(self.tracking,'visible',True)):
    #  print '...lost'
    #  self.sch.add(self.lostTrack,delay=0.085)
    for o in self.parent.parent.get_children():    
      self.isNew(o)      
      
    yield self.parent.parent.changes,self.lostTrack
   
  def lostTrack(self):
    if self.tracking is not None:
      self.tracking=None
      self.log._='Object disappeared'
      self._visual.clear()
      #self._location.clear()

    
  def attendToUnattended(self,pattern=''):
    self.attendTo(pattern=pattern,unattended=True)
  def attendToNew(self,pattern=''):
    self.attendTo(pattern=pattern,new=True)

  def attendTo(self,pattern,unattended=False,new=False):
    if isinstance(pattern, str) and ':' not in pattern and pattern.count(' ')==1:
        pattern='x:%s y:%s'%tuple(pattern.split(' '))
  
    self.lastLocationPattern=Pattern(pattern,self.sch.bound)
    r=[]
    for obj in self.parent.parent.get_children():
      if new==True and not self.isNew(obj): continue
      if unattended==True and self.finst.isIn(obj): continue
      if hasattr(obj,'x') and hasattr(obj,'y') and getattr(obj,'visible',True):
        if self.lastLocationPattern.match(obj)!=None:
          r.append(obj)
    if len(r)>0:
      obj=self.random.choice(r)    
      self.log._='Vision found obj at (%g,%g)'%(obj.x,obj.y)
      self._location.set('%g %g'%(obj.x,obj.y))

  def isClose(self,a,b):
      return abs(a-b)<0.01

  def examine(self,pat):
    if isinstance(pat, str) and ':' not in pat and pat.count(' ')==1:
        pat='x:%s y:%s'%tuple(pat.split(' '))
    
    self.lastExamine=Pattern(pat,self.sch.bound)
    
    pat=self.lastExamine

    for obj in self.parent.parent.get_children():
     if hasattr(obj,'x') and hasattr(obj,'y') and getattr(obj,'visible',True):   
      if pat.match(obj) is not None:
      #if self.isClose(obj.x,float(pat[0])) and self.isClose(obj.y,float(pat[1])):        
        self.busy=True
        yield 0.085
        self.busy=False
        if obj in self.parent.parent.get_children():
          self.tracking=obj
          self.log._='Vision sees %s'%Chunk(obj)
          self._visual.set(obj)
          self.finst.add(obj)
        else:
          self.tracking=None  
          self.log._='Vision sees nothing'
          self._visual.clear()
        break  

