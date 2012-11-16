from __future__ import generators
import ccm
from ccm.pattern import Pattern

class SOSVision(ccm.Model):
  def __init__(self,buffer,delay=0.0,log=None,delay_sd=None):
    self._buffer=buffer
    self.delay=delay
    self.delay_sd=delay_sd
    self.error=False
    self.busy=False
  
  def request(self,pattern=''):
    if self.busy: return

    matcher=Pattern(pattern)
      
    self.error=False
    r=[]
    for obj in self.parent.parent.get_children():
      if matcher.match(obj)!=None:
        if not hasattr(obj,'salience') and not hasattr(obj,'visible'):
          continue
        
        if hasattr(obj,'salience'):
          if self.random.random()>obj.salience:
            continue
        if hasattr(obj,'visible'):
          if obj.visible==False:
            continue
        if hasattr(obj,'value'):
          if obj.value==None:
            continue
        r.append(obj)

    self.busy=True
    d=self.delay
    if self.delay_sd is not None:
        d=max(0,self.random.gauss(d,self.delay_sd))
    yield d
    self.busy=False

    if len(r)==0:
      self._buffer.clear()
      self.error=True
    else:
      obj=self.random.choice(r)
      if obj not in self.parent.parent.get_children():
        self._buffer.clear()
        self.error=True
      elif hasattr(obj,'visible') and obj.visible==False:
        self._buffer.clear()
        self.error=True
      else:
        self._buffer.set(obj)
      
      
      
        
