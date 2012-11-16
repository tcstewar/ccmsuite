from __future__ import generators
import ccm
import math

from ccm.lib.actr.buffer import Chunk


class ImaginalModule(ccm.Model):
  def __init__(self,buffer,delay=0.2,delay_sd=None):
    ccm.Model.__init__(self)
    self._buffer=buffer
    self.busy=False
    self.delay=delay
    self.delay_sd=delay_sd

  def delay_time(self):
      t=self.delay
      if callable(t): t=t()
      if self.delay_sd is not None:
          t=math.gauss(t,self.delay_sd)
      return t

  def set(self,chunk):
      if self.busy: return
      self.busy=True

      try:
          chunk=Chunk(chunk,self.sch.bound)
      except AttributeError:
          chunk=Chunk(chunk,{})        
      yield self.delay_time()

      self._buffer.chunk=chunk
      self.busy=False

  def modify(self,**args):
      if self.busy: return
      self.busy=True
      yield self.delay_time()
      self._buffer.modify(**args)
      self.busy=False

  def clear(self,**args):
      if self.busy: return
      self.busy=True
      yield self.delay_time()
      self._buffer.clear()
      self.busy=False

      
    
