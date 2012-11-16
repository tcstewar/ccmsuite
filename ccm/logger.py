import atexit
import time
import bisect
import sys
import random
import os

using_java=False
try:
    from java.io import File
    using_java=True
except:
    pass

def file_exists(filename):
    if hasattr(os,'access'):
        return os.access(filename,os.F_OK)
    elif using_java:
        return File(filename).exists()


class Trace:
    def __init__(self):
        self.data=dict(time=[(0,0.0)])
        self.index=1
        self.type={}
    def add(self,key,value):
        if not isinstance(value,(bool,int,float,basestring,type(None))):
            value=repr(value)
        if type(value)==str:
            if value.startswith('<'): return
        if not self.data.has_key(key):
            self.data[key]=[]

        self.data[key].append((self.index,value))
        self.index+=1
            
    def keys(self):
        return self.data.keys()
    def fixed_keys(self):
        return [k for k,v in self.data.items() if len(v)==1]

    def get_final(self,key):
        return self.data[key][-1][1]
    def get_pts(self,vars):
        pts=[]
        for v in vars:
            for i,val in self.data[v]:
                if i not in pts: pts.append(i)
        pts.sort()
        return pts    

    def merge_pts(self,pts,key):
        times=[x[0] for x in self.data[key]]
        i=0
        for t in times:
            if i>=len(pts) or t<pts[i]: continue
            while i<len(pts)-1 and pts[i+1]<t:
                del pts[i]
            i+=1
        while i<len(pts)-1:
            del pts[i]

    def group_pts(self,pts,key):
        times=[x[0] for x in self.data[key]]
        group=[]
        i=0
        for p in pts:
            if i>=len(times) or p<times[i]: group.append(p)
            else:
                if len(group)>0: yield group
                group=[p]
                while i<len(times) and p>=times[i]:
                    i+=1
        if len(group)>0: yield group  

    def get_at(self,name,time):
        d=self.data[name]
        i=bisect.bisect(d,(time+0.5,))-1
        if i<0: return None
        if i>=len(d)-1: i=-1
        return d[i][1]

    def __nonzero__(self):
        return self.index!=1



class Log:
    def __init__(self):
        self.do_screen=True
        self.do_html=False
        self.do_summary=False
        self.do_data=False
        self.directory=sys.argv[0]
        self.using_default_directory=True
        if self.directory.endswith('.py'): self.directory=self.directory[:-3]
        
        self.start_time=time.time()
        self.last_flush=self.start_time
        
        self.reset()
        
    def use_directory(self,dir):
        self.directory=dir
        self.using_default_directory=False    
        

    def set(self,key,value):
        if key=='time': self.time=value
        if self.do_screen:
            self.display_value(key,value)
        if self.do_data or self.do_summary:
            self.data[key]=value
        if self.do_html:    
            self.trace.add(key,value)

    def display_value(self,key,value):
        if key!='time':
            print '%8.3f %s %s'%(self.time,key,value)
    def display_all(self):
        if self.time>0:
            print 'Total time: %8.3f'%self.time
        items=self.data.items()
        items.sort()
        for k,v in items:
            if k!='time':
                print ' %s %s'%(k,v)

    def get_time_code(self):
        t=time.strftime('%Y%m%d-%H%M%S',time.localtime(self.start_time))
        return '%s-%s'%(t,self.id)
        
    def ensure_directory_exists(self):
        if not file_exists(self.directory+'/'): os.makedirs(self.directory)
        
    def reset(self):
        self.trace=Trace()
        self.data={}
        self.time=0
        self.id='%08x'%int(random.randrange(0x7FFFFFFF))
  


class DummyLog:
  def set(self,key,value):
    pass
  def __nonzero__(self):
    return False
  def __setattr__(self,key,value):
    pass
  def __getattr__(self,key):
    if key[0]!='_': return self
    else: raise AttributeError(key)
  def __setitem__(self,key,value):
    pass
  def __getitem__(self,key):
    return self
dummy=DummyLog()    


class LogProxy:
  def __init__(self,log,prefix=''):
    self._log=log
    if prefix.startswith('.'): prefix=prefix[1:]
    self._prefix=prefix
    self._sub={}
  def __setattr__(self,key,value):
    if key.startswith('_'):
      if key=='_': self._set(value)
      else: self.__dict__[key]=value
    else:
      getattr(self,key)._set(value)  

  def __getattr__(self,key):
    if key.startswith('_'):
        if key=='_': return self
        if key in self.__dict__: return self.__dict__[key]
        raise AttributeError(key)
    else:
      s=LogProxy(self._log,'%s.%s'%(self._prefix,key))
      self.__dict__[key]=s
      return s
        
  def __setitem__(self,key,value):
      self[key]._set(value)  
  
  def __getitem__(self,key):
      s=self._sub.get(key,None)
      if s is not None: return s
      s=LogProxy(self._log,'%s[%s]'%(self._prefix,key))
      self._sub[key]=s
      return s

  def _set(self,value):
    try:  
      if not isinstance(value,(int,float,bool,basestring,tuple,list,dict)):
        value=`value`
    except TypeError:
        value=`value`
    self._log.set(self._prefix,value)  
  
  def __nonzero__(self):
    return True




singleton_log=Log()
log_proxy=LogProxy(singleton_log)
def log(screen=None,html=None,data=None,summary=None,directory=None):
    if screen is not None: singleton_log.do_screen=screen
    if html is not None: singleton_log.do_html=html
    if data is not None: singleton_log.do_data=data
    if summary is not None: singleton_log.do_summary=summary
    if directory is not None: singleton_log.use_directory(directory)
    return log_proxy


pending_output=[]
def finished(flush=True):
    log=singleton_log
    has_data=log.data or log.trace
    
    if has_data:
        if log.do_summary:
            log.display_all()
        if log.do_data:
            log.ensure_directory_exists()
            fn='%s/%s.data'%(log.directory,log.get_time_code())
            pending_output.append((fn,log.data))
        if log.do_html:
            log.ensure_directory_exists()
            from ccm.ui.htmltrace import HTMLTrace
            html=HTMLTrace(log.trace)
            html.generate('%s/%s.html'%(log.directory,log.get_time_code()))

    if flush or time.time()-log.last_flush>10:
        for fn,data in pending_output:
            f=file(fn,'w')
            items=data.items()
            items.sort()
            for k,v in items:
                f.write('%s=%s\n'%(k,v))
            f.close()
        del pending_output[:]
        log.last_flush=time.time()        
    log.reset()
    
    

atexit.register(finished,flush=True)   

