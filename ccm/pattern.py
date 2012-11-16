import re

class PatternException(Exception):
    pass

def get(obj,name,key):    
  if name is None: a=obj
  else:
      a=obj[name]

  while type(key)==str and '.' in key:
      key1,key=key.split('.',1)
      try:
        a=a[key1]
      except AttributeError:
        a=getattr(a,key1)

  try:
      x=a[key]
  except AttributeError:    
      x=getattr(a,key)
  if isinstance(x,float): x='%g'%x    
  if not isinstance(x,str): x=`x`
  return x

def partialmatch(obj,name,key,b,value):
  if type(key)==str and key[0]=='?':
      key=b[key[1:]]
  v=get(obj,name,key)
  if v==value: return True

  # fix for early Python versions where True and False are actually 1 and 0
  if value in ['True','False'] and type(True)==int:
      if v==str(bool(value)): return True
      
  pm=b.get('_partial',None)
  if pm is not None:
    x=pm.match(key,value,v)
    obj._partial+=x
    return True
  else:
    return False
    


class Pattern:
    def __init__(self,patterns,bound=None,partial=None):
        self.funcs=parse(patterns,bound)
        self.partial=partial
        
    def match(self,obj):
        b={}
        b['_partial']=self.partial
        if self.partial is not None:
          obj._partial=0.0
        try:
            for f in self.funcs:
                if f(obj,b)==False:  return None
        except (AttributeError,TypeError,KeyError):
            return None
        del b['_partial']    
        return b    
            


        
        
def parse(patterns,bound=None):
    if not hasattr(patterns,'items'):
      patterns={None:patterns} 
    funcs=[]
    vars={}
    funcs2=[]
    for name,pattern in patterns.items():
        if not isinstance(pattern,(list,tuple)): pattern=[pattern]
        for p in pattern:
            if p is None:
                if name is None: funcs.append(lambda x,b: x==None)
                else:            funcs.append(lambda x,b,name=name: x[name]==None or len(x[name])==0)
            elif callable(p):
                if name is None:
                  def callfunc(x,b,name=name,p=p):
                    return p(x,b)
                else:
                  def callfunc(x,b,name=name,p=p):
                    return p(x[name],b)
                funcs2.append(callfunc)        
            elif isinstance(p,basestring):
                namedSlots=False
                for j,text in enumerate(p.split()):
                    key=j
                    m=re.match('([?]?[\w\.]+):',text)
                    if m!=None:
                        key=m.group(1)
                        try:
                            key=int(key)
                        except ValueError:
                            pass
                        text=text[m.end():]
                        if len(text)==0:
                            raise PatternException("No value for slot '%s' in pattern '%s'"%(key,pattern))
                        namedSlots=True          
                    else:
                        if namedSlots!=False:
                            raise PatternException("Found unnamed slot '%s' after named slot in pattern '%s'"%(text,pattern))
                    if text=='?': continue
                    while len(text)>0:
                        m=re.match('([\w\.-]+)',text)
                        if m!=None:
                            text=text[m.end():]
                            t=m.group(1)
                            funcs.append(lambda x,b,name=name,key=key,t=t: partialmatch(x,name,key,b,t))
                            continue

                        m=re.match('!([\w\.-]+)',text)
                        if m!=None:
                            text=text[m.end():]
                            t=m.group(1)
                            funcs.append(lambda x,b,name=name,key=key,t=t: get(x,name,key)!=t)
                            continue
        
                        m=re.match('\?(\w+)',text)
                        if m!=None:
                            text=text[m.end():]
                            v=m.group(1)
                            if bound is not None and v in bound:
                                funcs.append(lambda x,b,name=name,key=key,t=bound[v]: partialmatch(x,name,key,b,t))
                            elif v in vars:
                                funcs2.append(lambda x,b,name=name,key=key,v=v: partialmatch(x,name,key,b,b[v]))
                            else:    
                                vars[v]=(name,key)
                                def setfunc(x,b,name=name,key=key,v=v):
                                  b[v]=get(x,name,key)
                                  return True
                                funcs.append(setfunc)
                            continue
        
                        m=re.match('!\?(\w+)',text)
                        if m!=None:
                            text=text[m.end():]
                            v=m.group(1)
                            if bound is not None and v in bound:
                                funcs.append(lambda x,b,name=name,key=key,t=bound[v]: get(x,name,key)!=t)
                            else:
                                funcs2.append(lambda x,b,name=name,key=key,v=v: get(x,name,key)!=b[v])
                            continue

                        raise PatternException("Unknown text '%s' in pattern '%s'"%(text,pattern))  
    return funcs+funcs2                        
        

        
        
        
        
