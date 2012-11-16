import ccm
import math

__all__=['ProceduralSubModule','PMNoise','PMPGC',
         'PMPGCSuccessWeighted','PMPGCMixedWeighted',
         'PMQLearn','PMTD','PMNew']

class ProceduralSubModule(ccm.Model):
  def start(self):
    self.parent.add_adaptor(self)
  def create(self,prod):
    pass
  def firing(self,prod):
    pass
  def selecting(self,prod):
    pass
  def reward(self,prod):
    pass
  def utility(self,prod):
    return 0      
  def below_threshold(self):
    pass  
       

class PMNoise(ProceduralSubModule):
  def __init__(self,noise=0,baseNoise=0.0):
    self.noise=noise
    self.baseNoise=baseNoise
  def create(self,prod,parents=None):
    prod.baseNoise=self.logisticNoise(self.baseNoise)
  def utility(self,prod):
    return prod.baseNoise+self.logisticNoise(self.noise)
  def logisticNoise(self,s):
    x=self.random.random()
    return s*math.log(1.0/x -1.0)
    
class PMPGC(ProceduralSubModule):
  def __init__(self,goal=20):
    self.history=[]
    self.goal=goal
    self._clearFlag=False
  def create(self,prod,parents=None):
    #todo: modify this to do the PGC estimate based on parents if there are any
    prod.successes=1
    prod.failures=0
    prod.time=self.parent.production_time
    if callable(prod.time): prod.time=prod.time()
    prod.lock_pgc=False
  def selecting(self,prod):
    if self._clearFlag:
      del self.history[:]
      self._clearFlag=False
    self.history.append((prod,self.now()))  
  def reward(self,value):
    now=self.now()
    for p,t in self.history:
        if not p.lock_pgc:
          dt=now-t
          p.time+=dt
          if value>=0: p.successes+=value
          else: p.failures-=value
    self._clearFlag=True  
  def utility(self,prod):
    p=prod.successes/(prod.successes+prod.failures)
    c=prod.time/(prod.successes+prod.failures)
    g=self.goal
    return p*g-c
  def set(self,prod,successes=None,failures=None,time=None,lock=None):
    if not isinstance(prod,Production):
        prod=self.parent._productions[prod]
    if successes is not None: prod.successes=successes
    if failures is not None: prod.failures=failures
    if time is not None: prod.time=time
    if lock is not None: prod.lock_pgc=lock
    
    
      

class PMPGCSuccessWeighted(PMPGC):
  def utility(self,prod):
    p=1.0
    c=prod.time/(prod.successes)
    g=self.goal
    return p*g-c
class PMPGCMixedWeighted(PMPGC):
  def utility(self,prod):
    p=prod.successes/(prod.successes+prod.failures)
    c=prod.time/(prod.successes)
    g=self.goal
    return p*g-c
  
import ccm.lib.qlearn as qlearn
class PMQLearn(ProceduralSubModule):
  def __init__(self,alpha=0.2,gamma=0.9,initial=0):
    self.q=qlearn.QLearn(actions=[],alpha=0.2,gamma=0.9,initial=initial)
    self.history=[]
  def currentState(self):
    return None  
  def selecting(self,prod):
    if prod not in self.q.actions: self.q.actions.append(prod)
    self.history.append((self.currentState(),prod))
  def reward(self,value):
    state2=self.currentState()
    while len(self.history)>0:
      state1,action=self.history.pop(-1)
      self.q.learn(state1,action,value,state2)
      state2=state1
      value=0
  def utility(self,prod):
    state=self.currentState()
    return self.q.getQ(state,prod)    


# From (Fu & Anderson, 2004)
class PMTD(ProceduralSubModule):
    def __init__(self,alpha=0.1,discount=1,cost=0.05):
        self.alpha=alpha
        self.discount=discount
        self.last_prod=None
        self.last_time=None
        self.this_reward=0
        self.cost=cost
    def create(self,prod,parents=None):
        prod.td_u=0
        prod.cost=self.cost
    def firing(self,prod):
        if self.last_prod is not None:
            d=self.now()-self.last_time
            k=self.discount
            r=self.this_reward-self.last_prod.cost+prod.td_u/(1+k*d)
            td=r-self.last_prod.td_u
            self.last_prod.td_u+=self.alpha*td
        self.last_prod=prod
        self.last_time=self.now()
        self.this_reward=0

    def reward(self,value):
        self.this_reward+=value

    def utility(self,prod):
        return prod.td_u



       
                       
class PMNew(ProceduralSubModule):
  def __init__(self,alpha=0.2):
    self.history=[]
    self.alpha=alpha
    self.clearFlag=False
  def create(self,prod,parents=None):
    prod.util=0
  def selecting(self,prod):
    if self.clearFlag:
      del self.history[:]
      self.clearFlag=False
    self.history.append((prod,self.now()))  
  def reward(self,value):
    now=self.now()
    for p,t in self.history:
      dt=now-t
      r=value-dt
      p.util+=self.alpha*(r-p.util)
    self.clearFlag=True  
  def utility(self,prod):
    return prod.util
            
