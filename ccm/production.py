from __future__ import generators

import model
import inspect
import re
import pattern

try:
    Set=set
except:
    from sets import Set

class ProductionException(Exception):
    pass

class Production:
    def __init__(self,system,name,func):
        self.system=system
        self.name=name
        self.base_utility=0
        a,va,hk,d=inspect.getargspec(func)
        self.keys=a
        patterns={}
        for i,name in enumerate(a[:]):
          if name=='utility': 
            self.base_utility=d[i]
            del a[i]
          else:
            patterns[name]=d[i]
        self.pattern_specs=patterns
        self.pattern=pattern.Pattern(patterns)
        self.bound=None
        
        self.original_func=func
        code=inspect.getsource(func)
        m=re.match(r'[^(]+\([^(]*\):',code)
        self.code=code[m.end():]
        code='if True:'+code[m.end():]
        self.func=compile(code,'<production-%s>'%self.name,'exec')
        
    def match(self,obj):
        b=self.pattern.match(obj)
        if b is None: return False
        self.bound=b
        return True
    
    def fire(self,context):
        self.system.sch.bound=self.bound
        exec self.func in context,self.bound
            
      
class ProductionSystem(model.Model):
    production_time=0.05
    production_match_delay=0
    _auto_run_start=False
    def _convert_info(self,objects,methods):
        self._productions=[]
        self._initializers=[]
        self._keys_used=Set()
        for k,v in methods.items():
            a,va,hk,d=inspect.getargspec(v)
            if va is None and hk is None:
              if d is None and len(a)==0:
                p=Production(self,k,v)
                self._initializers.append(p)
              if d is not None and a is not None and len(a)==len(d):
                p=Production(self,k,v)
                self._keys_used.update(p.keys)
                self._productions.append(p)
        self.sch.add(self._process_productions)
    
    def _calc_context(self):
        context={}
        keys=Set(self._keys_used)
        if 'self' in keys: keys.remove('self')
        if len(keys)==0: top=self
        m=self
        while m is not None:
            for k,v in m.__dict__.items():
                if k not in context and k[0]!='_' and k!='parent' and isinstance(v,object) and not isinstance(v,model.MethodWrapper):
                    context[k]=v
                    if k in keys: 
                        keys.remove(k)
                        if len(keys)==0: top=m
            if 'top' in keys: top=m            
            m=m.parent
            
        if 'top' in keys: keys.remove('top') 
        if len(keys)>0:
            raise ProductionException("Production is matching on an unknown module '%s'"%(keys))

        #TODO: rethink this. top should refer to the highest level in the tree.
        # but it would be nice if we had something to refer to the highest level
        # that could cause a matching change, to optimize the yield._top.changes
        # call.  This was the original idea and may impact the logic calculating
        # top above.  However, any fix to this should make sure not to break the
        # rock paper scissors tutorials.
        while hasattr(top,'parent') and top.parent is not None: top=top.parent
        
        context['self']=self
        context['top']=top
        self._top=top
        self._context=context
    
    def _process_productions(self):
        self._calc_context()          
        for i in self._initializers:
            i.fire(self._context)
        while True:
          if self.production_match_delay>0: yield self.production_match_delay  
          match=[p for p in self._productions if p.match(self._context)]
          if len(match)==0:
            yield self._top.changes
          else:
            choice=self.random.choice(match)
            self.log.production=choice.name
            yield self.production_time-self.production_match_delay
            self.log.production=None
            choice.fire(self._context)
            
        
                          
            
            
        
