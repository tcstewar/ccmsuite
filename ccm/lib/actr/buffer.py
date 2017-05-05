import ccm

try:
    from UserDict import UserDict
except:
    from collections import UserDict


class Chunk(UserDict):
  def __init__(self,contents,bound=None):
    UserDict.__init__(self)
    if isinstance(contents,Chunk):
      self.update(contents)
    elif isinstance(contents,str):
      for i,x in enumerate(contents.split()):
        if ':' in x:
          i,x=x.split(':',1)
        if x.startswith('?'):
          key=x[1:]
          x=bound[key]
        self[i]=x
    elif hasattr(contents,'__dict__'):  
      for k,v in contents.__dict__.items():
        if type(v) in [str,float,int,bool]:
          self[k]=v
    else:
      try:
        self.update(contents)
      except:  
        raise Exception('Unknown contents for chunk:',contents)      
  def __repr__(self):
    r=[]
    keys=self.keys()
    i=0
    while i in keys:
      r.append('%s'%self[i])      
      keys.remove(i)
      i+=1
    keys.sort()
    for k in keys:
      if k[0]!='_':
        r.append('%s:%s'%(k,self[k]))
    return ' '.join(r)  
      

class Buffer(ccm.Model):
  def __init__(self):
    self.chunk=None
  def set(self,chunk):
    try:
      self.chunk=Chunk(chunk,self.sch.bound)
    except AttributeError:
      self.chunk=Chunk(chunk,{})  
  def modify(self,**args):
    for k,v in args.items():
      if k.startswith('_'): k=int(k[1:])
      if k not in self.chunk:
        raise Exception('No slot "%s" to modify to "%s"'%(k,v))
      self.chunk[k]=v
      self.chunk=self.chunk
  def __getitem__(self,key):
    return self.chunk[key]
  def clear(self):
    self.chunk=None  
  def __eq__(self,other):
    return self.chunk==other
  def __hash__(self):
    return id(self)
  def __len__(self):
    if self.chunk is None: return 0
    return len(self.chunk)  def isEmpty(self):
    return len(self)==0
