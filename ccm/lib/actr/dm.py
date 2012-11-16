from __future__ import generators
import ccm
import math

__all__=['Memory','MemorySubModule','DMNoise','DMBaseLevel','DMSalience','DMSpreading','DMFixed',
         'Partial','BlendingMemory','DMAssociate','DMInhibition']

from ccm.lib.actr.buffer import Chunk,Buffer
from ccm.pattern import Pattern

class Memory(ccm.Model):
  def __init__(self,buffer,latency=0.05,threshold=0,maximum_time=10.0,finst_size=4,finst_time=3.0):
    ccm.Model.__init__(self)
    self._buffer=buffer
    self.dm=[]
    self.error=False
    self.busy=False
    self.adaptors=[]
    self.latency=latency
    self.threshold=threshold
    self.maximum_time=maximum_time
    self.partials=[]
    self.finst=Finst(self,size=finst_size,time=finst_time)
    self.record_all_chunks=False
    self._request_count=0
    
  def clear(self):
    del self.dm[:]
    
  def add(self,chunk,record=None,**keys):
    if self.error: self.error=False
    if isinstance(chunk,Buffer):
      chunk=Chunk(chunk.chunk)
    else:
      bound=None
      if hasattr(self,'sch'):
        bound=getattr(self.sch,'bound',None)
      chunk=Chunk(chunk,bound)
    for c in self.dm:
      if chunk==c:
        for a in self.adaptors: a.merge(c,**keys)
        break
    else:
      for a in self.adaptors: a.create(chunk,**keys)
      self.dm.append(chunk)
    chunk.record=record

      
  def find_matching_chunks(self,pattern,threshold=None):
     bound=getattr(self.sch,'bound',None)
     pattern=Pattern(pattern,bound)
     matches=[x for x in self.dm if pattern.match(x) is not None]
     if threshold is not None:
       matches=[x for x in matches if self.get_activation(x)>=threshold]
     return matches  
        
      
  def request(self,pattern,partial=None,require_new=False):
     if partial is None and len(self.partials)>0: partial=self.partials[0]
     self.busy=True
     if self.error: self.error=False
     self._request_count+=1
     b=getattr(self.sch,'bound',None)
     pattern=Pattern(pattern,b,partial=partial)
     
     all=self.dm
     if require_new: all=[x for x in all if not self.finst.contains(x)]
     
     matches=[x for x in all if pattern.match(x) is not None]
     
     #for x in matches: print `x`,self.get_activation(x)
     
       
     for a in self.adaptors: a.matched(matches)
     if len(matches)==0:
         self.fail(self._request_count)
     else:
         maximum=None    
         for chunk in matches:
             chunk.activation=self.get_activation(chunk)
             if partial is not None:
               chunk.activation+=chunk._partial
             if maximum is None or chunk.activation>maximum:
               maximum=chunk.activation
         if maximum<self.threshold:
             self.fail(self._request_count)
         else:    
             best=[x for x in matches if x.activation==maximum]
             
             choice=self.random.choice(best)
             self.recall(choice,matches=matches,request_number=self._request_count)
     
  def fail(self,request_number):
     if self.threshold is None: 
         time=self.maximum_time
     else:
         time=self.latency*math.exp(-self.threshold)
         if time>self.maximum_time: time=self.maximum_time 
     yield time
     if request_number!=self._request_count: return
     
     self.error=True
     self._buffer.clear()
     self.busy=False
  
  def recall(self,chunk,matches,request_number):
     self.finst.add(chunk)
     time=self.latency*math.exp(-chunk.activation)
     if time>self.maximum_time: time=self.maximum_time
     yield time
     if request_number!=self._request_count: return
     self._buffer.set(chunk)
     for a in self.adaptors: a.recalled(chunk)
     self.busy=False
     
  
  def get_activation(self,chunk):
     if not isinstance(chunk,Chunk):
         try:
           chunk=Chunk(chunk,self.sch.bound)
         except AttributeError:
           chunk=Chunk(chunk,None)           
         for c in self.dm:
             if chunk==c:
                 chunk=c
                 break
         else:
             raise Exception('No such chunk found')        
     act=0
     for a in self.adaptors:
        act+=a.activation(chunk)
     if self.record_all_chunks or chunk.record is True:
         self.log[str(chunk)]=act 
     return act   
                
  def add_adaptor(self,a):
     self.adaptors.append(a)

class Finst:
  def __init__(self,parent,size=4,time=3.0):
    self.parent=parent
    self.size=size
    self.time=time
    self.obj=[]
  def contains(self,o):
    return o in self.obj
  def add(self,o):
    if self.size==0: return
    self.obj.append(o)
    if len(self.obj)>self.size:
      self.remove(self.obj[0])
    self.parent.sch.add(self.remove,args=[o],delay=self.time)
  def remove(self,o):
    if o in self.obj: self.obj.remove(o)          
      
    
class MemorySubModule:
  def __init__(self,parent):
    self.parent=parent
    if parent is not None:
      parent.add_adaptor(self)
  def create(self,chunk,**keys):
    pass
  def merge(self,chunk,**keys):
    pass
  def matched(self,chunks):
    pass  
  def activation(self,chunk):
    return 0
  def recalled(self,chunk):
    pass
  def now(self):
    if self.parent is None or not self.parent._is_converted(): return 0
    else: return self.parent.now()

class DMNoise(MemorySubModule):
  def __init__(self,memory,noise=0.3,baseNoise=0.0):
    MemorySubModule.__init__(self,memory)
    self.noise=noise
    self.baseNoise=baseNoise  
  def create(self,chunk,**keys):
    chunk.baseNoise=self.logisticNoise(self.baseNoise)
  def activation(self,chunk):
    return chunk.baseNoise+self.logisticNoise(self.noise)
  def logisticNoise(self,s):
    try:
      x=self.parent.random.random()
    except AttributeError:
      import random
      x=random.random()
    return s*math.log(1.0/x-1.0)
      


class DMBaseLevel(MemorySubModule):
  def __init__(self,memory,decay=0.5,limit=None):
    MemorySubModule.__init__(self,memory)
    self.decay=decay
    self.limit=limit
  
  def create(self,chunk,time=0.0,baselevel=None,**keys):
    chunk.creation=self.now()
    chunk.times=[chunk.creation-time]
    chunk.count=1
    if baselevel is not None and baselevel!='calculate':
      chunk.baselevel=baselevel
    
  def merge(self,chunk,time=0.0,baselevel=None,**keys):
    chunk.times.append(self.now()-time)
    chunk.count+=1
    if self.limit is not None and len(chunk.times)>self.limit:
      if self.limit==0: del chunk.times[:]
      else: chunk.times=chunk.times[-self.limit:]
    if baselevel is not None:
      if baselevel=='calculate': del chunk.baselevel
      else: chunk.baselevel=baselevel
    
  def activation(self,chunk):
    if hasattr(chunk,'baselevel'):
      return chunk.baselevel
    if self.decay==None: 
      return 0
    d=self.decay
    now=self.now()
    t=[now-time for time in chunk.times]
    t=[max(L,0.005) for L in t]
    
    exact=0.0
    approx=0.0
    if len(t)>0:
      exact=sum([math.pow(time,-d) for time in t])
    if self.limit is not None:
      n=chunk.count
      k=len(chunk.times)
      if n>k:
        tn=now-chunk.creation
        if k>0:
          tk=now-chunk.times[0]
        else:
          tk=0.0
        approx=(n-k)/(1-d)*(math.pow(tn,1-d)-math.pow(tk,1-d))/(tn-tk)
    
    B=math.log(exact+approx)
    return B

class DMSpacing(MemorySubModule):
  def __init__(self,memory,decayScale=0.0,decayIntercept=0.5):
    MemorySubModule.__init__(self,memory)
    self.decayScale=decayScale
    self.decayIntercept=decayIntercept  
  
  def create(self,chunk,time=0.0,**keys):
    chunk.times=[(self.actr.time-time,self.decayIntercept)]
        
  def merge(self,chunk,time=0.0,**keys):
    t=self.now()-time
    m=self.activation(chunk)
    d=self.decayScale*math.exp(m)+self.decayIntercept
    chunk.times.append((t,d))
    
  def activation(self,chunk):
    now=self.now()
    total=0.0
    for time,d in chunk.times:
      total+=math.pow(now-time,-d)
    B=math.log(total)
    return B

class DMInhibition(MemorySubModule):
    def __init__(self,memory,decayScale=1.0,timeScale=5.0):
        MemorySubModule.__init__(self,memory)
        self.decayScale=decayScale
        self.timeScale=timeScale
    def create(self,chunk,time=0.0,**keys):
        chunk.mostRecentTime=time
    def merge(self,chunk,time=0.0,**keys):
        chunk.mostRecentTime=self.now()
    def activation(self,chunk):
        tn=self.now()-chunk.mostRecentTime
        I=-math.log(1+math.pow(tn,-self.decayScale)/self.timeScale)
        return I


class DMSalience(MemorySubModule):
  def __init__(self,memory):
    MemorySubModule.__init__(self,memory)
    self.histogram={}
    self.weight={}
    self.memory=memory
  
  def weights(self,**weights):
    self.histogram={}
    self.weight={}
    for k,v in weights.items():
      if k.startswith('_'): k=int(k[1:])
      self.weight[k]=float(v)
      self.histogram[k]={}
    
  def context(self,pattern):
    pat=Pattern(pattern)
    chunks=[x for x in self.memory.dm if pat.match(x) is not None]
    for k,hist in self.histogram.items():
      hist.clear()
    if len(chunks)==0: raise Exception('No chunks match salience pattern: "%s"'%pattern)
    dw=1.0/len(chunks)
    for c in chunks:
      for k,hist in self.histogram.items():
        val=c.get(k,None)
        if val not in hist: hist[val]=dw
        else: hist[val]+=dw
        
  def activation(self,chunk):
    act=0.0
    for k,hist in self.histogram.items():
      val=chunk.get(k,None)
      p=hist[val]
      w=self.weight[k]
      act+=math.log(1.0/p,2)*w
#    if self.log: self.log.act[`chunk`]=act
    return act  
      
      
class DMSpreading(MemorySubModule):
  def __init__(self,memory,*buffers):
    MemorySubModule.__init__(self,memory)
    self.strength=1
    self.buffers=buffers
    self.weight={}
    for b in buffers: 
      self.weight[b]=1
    self.slots={}
    
  def create(self,chunk,**keys):
    for slot in chunk.values():
      if slot in self.slots:
        self.slots[slot].append(chunk)
      else:
        self.slots[slot]=[chunk]
  def activation(self,chunk):
    values=chunk.values()
  
    total=0.0
    for b in self.buffers:
     ch=b.chunk 
     if ch is not None:
      w=self.weight[b]
      for key,slot in ch.items():
        if slot in values:
          s=self.strength-math.log(len(self.slots[slot])+1)
          total+=w*s
    return total      
        
class DMFixed(MemorySubModule):
  def __init__(self,memory,default=0):
    MemorySubModule.__init__(self,memory)
    self.default=default
  def create(self,chunk,fixed=None,**keys):
    if fixed is None: fixed=self.default
    chunk.fixed=fixed
  def merge(self,chunk,fixed=0,**keys):
    chunk.fixed+=fixed
  def activation(self,chunk):
    return chunk.fixed


class Associated:
  def __init__(self,a,b):
    self.a=a
    self.b=b

class DMAssociate(MemorySubModule):
  def __init__(self,memory,buffer,weight=1,decay=0.5,limit=None):
    MemorySubModule.__init__(self,memory)
    self._buffer=buffer
    self._mem={}
    self._bl=DMBaseLevel(None,decay=decay,limit=limit)
    self.weight=weight
  def set_association(self,pre,post,baselevel):
    c=self._mem.get((pre,post),None)
    if c==None:
      c=Associated(pre,post)
      self._bl.create(c)
      self._mem[(pre,post)]=c
    c.baselevel=baselevel  
    
  def recalled(self,chunk):
    prechunk=self._buffer.chunk
    if prechunk is None: return
    for pk,pv in prechunk.items():
      for k,v in chunk.items():
        c=self._mem.get((pv,v),None)
        if c==None:
          c=Associated(pv,v)
          self._bl.create(c)
          self._mem[(pv,v)]=c
        else:
          self._bl.merge(c)
  def activation(self,chunk):
    act=0
    prechunk=self._buffer.chunk
    if prechunk is None: return 0
    for pk,pv in prechunk.items():
      for k,v in chunk.items():
        c=self._mem.get((pv,v),None)
        if c is not None:         
          act+=self._bl.activation(c)
    return act*self.weight
        
        
        
        
    
          
    
class Partial:
  def __init__(self,memory,strength=1.0,limit=-1.0):
    self._memory=memory
    self.limit=limit
    self.strength=strength
    self.sims={}
    memory.partials.append(self)
    
  def similarity(self,a,b,value):
    self.sims[a,b]=value
    self.sims[b,a]=value
  
  def request(self,pattern):
    self._memory.request(pattern,partial=self)
    
  def match(self,key,a,b):
    m=self.sims.get((a,b),self.limit)
    p=self.strength
    return p*m
    
      
class BlendingMemory(Memory):
  def recall(self,chunk,matches,request_number):
    keys=list(sorted(chunk.keys()))
    if not hasattr(chunk,'_blend_keys'):
      bk=[]
      for k in keys:
        try:
          v=float(chunk[k])
          bk.append(k)
        except:
          pass
      chunk._blend_keys=tuple(bk)
    bk=chunk._blend_keys
    if len(bk)>0:
      a=chunk.activation
      chunk=Chunk(chunk)
      chunk.activation=a
      
      for b in bk: chunk[b]=0
      total_activation=0
      for m in matches:
        m.exp_activation=math.exp(m.activation)
        k=list(sorted(m.keys()))
        if k==keys:
          blend={}
          try:            
            for b in bk:
              blend[b]=float(m[b])
          except ValueError:
            continue
          for b in bk:
            chunk[b]+=blend[b]*m.exp_activation
          total_activation+=m.exp_activation
      for b in bk:
        chunk[b]/=total_activation
    for m in Memory.recall(self,chunk,matches,request_number):
      yield m
      
    
  
  
