from __future__ import generators
import ccm

class ACTR(ccm.ProductionSystem):
    production_time_sd=None
    production_threshold=None
    
    def __init__(self,log=None):
        ccm.ProductionSystem.__init__(self,log=log)
        self._adaptors=[]
    
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
                activations=[self.get_activation(p) for p in match]
                a=max(activations)
                
                threshold=self.production_threshold
                if callable(threshold): threshold=threshold()
                
                if threshold is not None and a<threshold:
                    for a in self._adaptors: a.below_threshold()
                    yield self._top.changes
                    continue    
                options=[p for (i,p) in enumerate(match) if activations[i]==a]
                choice=self.random.choice(options)
                
                for a in self._adaptors: a.selecting(choice)
                #self.log.selected=choice.name
                self.log.production=choice.name
                
                t=self.production_time
                if callable(t): t=t()
                if self.production_time_sd is not None:
                    t=t+self.random.gauss(0,self.production_time_sd)
                t-=self.production_match_delay
                if t<0: t=0
                yield t
                
                if not choice.match(self._context):
                  #self.log.change_detected='before firing '+choice.name
                  self.log.production='(changed before firing)'
                else:  
                  for a in self._adaptors: a.firing(choice)
                  self.log.production=None
                  #self.log.firing=choice.name
                  choice.fire(self._context)
                  yield dict(delay=0,priority=-1000)      # delay so we don't try to match again until after the result of production firing has had a chance to occur
    
    def add_adaptor(self,module):
        self._adaptors.append(module)
        for p in self._productions:
            module.create(p)
            
    def reward(self,value):
        for a in self._adaptors:
            a.reward(value)
    def success(self):
        self.reward(1)
    def failure(self):
        self.reward(-1)            
                
                

    def get_activation(self,production=None):
        if production is None:
            r={}
            for p in self._productions:
                r[p.name]=self.get_activation(p)
            return r
        elif isinstance(production,str):
            for p in self._productions:
                if p.name==production:
                    return self.get_activation(p)
            return None
        else:
            activation=production.base_utility
            for a in self._adaptors:
                activation+=a.utility(production)
            return activation
            
       
