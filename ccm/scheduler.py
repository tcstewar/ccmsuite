
try:
    import heapq
except ImportError:
    import ccm.legacy.heapq as heapq
import copy

import logger

class Trigger:
    def __init__(self,name=''):
        self.name=name
    def __str__(self):
        return '<Trigger "%s">'%self.name    

class Event:
  generator=False
  def __init__(self,func,time,args=[],keys={},priority=0):    
    self.name=getattr(func,'func_name',None)

    try:
       code=func.func_code
    except AttributeError:
       try:
          code=func.__call__.im_func.func_code   
       except:
          code=None   
    if code and code.co_flags&0x20==0x20:    # check for generator
        func=func(*args,**keys).next
        args=[]
        keys={}
        self.generator=True

    self.func=func
    self.args=args
    self.keys=keys
    self.time=time
    self.priority=priority
    self.group=()
    self.cancelled=False
    self.parent=None
  def __cmp__(self,other):
    return cmp((self.time,-self.priority),(other.time,-other.priority))
  def __repr__(self):
    return '<%s %x %5.3f>'%(self.name,id(self.func),self.time)
    
class SchedulerError(Exception):
    pass

class Scheduler:
    def __init__(self):
        self.queue=[]
        self.to_be_added=[]
        self.triggers={}
        self.time=0.0
        self.stop_flag=False
        self.log=logger.log_proxy
    def extend(self,other):
        for k,v in other.triggers.items():    
            if k not in self.triggers:
                self.triggers[k]=v
            else:
                self.triggers[k].extend(v)
        if len(other.queue)>0:
            self.queue.extend(other.queue)
            heapq.heapify(self.queue)            
    def trigger(self,key,priority=None):
        if 'OpenGL' in key.name:
          print key.name
          print key in self.triggers
        if key in self.triggers:
            for event in self.triggers[key]:
                event.time=self.time
                if priority is not None:
                   event.priority=priority
                self.add_event(event)
            del self.triggers[key][:]
    def add_event(self,event):
        heapq.heappush(self.queue,event)
    def add(self,func,delay=0,args=[],keys={},priority=0,thread_safe=False):
        if thread_safe:
          self.to_be_added.append((func,delay,args,keys,priority))
        else:  
          ev=Event(func,self.time+delay,args=args,keys=keys,priority=priority)
          self.add_event(ev)
          return ev
        
    def run(self):
        self.stop_flag=False
        while not self.stop_flag and len(self.queue)>0:
            next=self.queue[0].time
            if next>self.time:
                self.time=next
                self.log.time=next
            self.do_event(heapq.heappop(self.queue))    
            while self.to_be_added:
              self.add(*self.to_be_added.pop())
        
    def handle_result(self,result,event):
        if isinstance(result,(int,float)):
            event.time=self.time+result
            self.add_event(event)
        elif isinstance(result,dict):
            event.time=self.time+result.get('delay',0)
            event.priority=result.get('priority',event.priority)
            self.add_event(event)
        elif isinstance(result,(str,Trigger)):
            event.time=None
            if result not in self.triggers:
                self.triggers[result]=[event]
            else:
                self.triggers[result].append(event)
        elif isinstance(result,(list,tuple)):
            events=[copy.copy(event) for r in result]
            for e in events: e.group=events
            for i,r in enumerate(result):
                self.handle_result(r,events[i])
        elif result is None:
            if event.parent is not None:
                event.parent.time=self.time
                self.add_event(event.parent)
        elif isinstance(result,Event):
            if result.generator and event.generator:
                result.parent=event
        elif hasattr(result,'default_trigger'):
          self.handle_result(result.default_trigger,event)        
        else:
            raise SchedulerError("Incorrect 'yield': %s"%(result))
                
            
            
    def do_event(self,event):
        assert self.time==event.time

        if event.cancelled: return
        for e in event.group: e.cancelled=True
        event.cancelled=False

        try:
          result=event.func(*event.args,**event.keys)
        except StopIteration:
          result=None
          
        self.handle_result(result,event)
        
                               
            
            
          
        
    
    def stop(self):    
      self.stop_flag=True  
