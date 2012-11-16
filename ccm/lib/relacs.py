import random
from math import exp

log=None

def calcExpectedPayoff(experiment,n=1000):
  data=[random.choice(experiment()) for i in range(n)]
  avg=sum(data)/float(n)
  
  totalDiff=0.0
  for d in data: 
    totalDiff+=abs(d-avg)
    
  return avg,totalDiff/n
  
def chooseBestIndex(values):
  bestValue=None
  for i,v in enumerate(values):  
    if bestValue==None or v>bestValue:
      bestValue=v
      best=[i]
    elif v==bestValue:
      best.append(i)
  return random.choice(best)    
  
def chooseWeighted(values):
  total=sum(values)
  choice=random.random()*total
  i=0
  while i<len(values)-1 and choice-values[i]>0:
    choice-=values[i]
    i+=1
  return i  
  

class FastBestReply:
  def __init__(self,expectedPayoff,beta,**args):
    self.expectedPayoff=expectedPayoff
    self.beta=beta
    self.recent={}
    
  def choose(self,options):
    for o in options:
      if o not in self.recent: 
        self.recent[o]=self.expectedPayoff
        if log: log.fbr.r[o]=self.recent[o]

    choice=chooseBestIndex([self.recent[o] for o in options])
    return options[choice]
    
  def feedback(self,info,chosen):
    for j,v in info:
      r=self.recent
      b=self.beta
      if j not in r: 
        r[j]=self.expectedPayoff
        if log: log.fbr.r[j]=r[j]
      r[j]=r[j]*(1-b)+v*b
      if log: log.fbr.r[j]=r[j]

class SlowBestReply:
  def __init__(self,expectedPayoff,expectedPayoffDifference,alpha,lambd,**args):
    self.expectedPayoff=expectedPayoff
    self.alpha=alpha
    self.lambd=lambd
    self.weight={}
    self.variability=expectedPayoffDifference
    self.lastValue={}
    
  def choose(self,options):
    W=self.weight
    S=self.variability
    L=self.lambd
    for j in options:
      if j not in W: W[j]=self.expectedPayoff
    
    try:
      weights=[exp(W[j]*L/S) for j in options]
      choice=chooseWeighted(weights)
    except (OverflowError,ZeroDivisionError):
      choice=chooseBestIndex([W[j] for j in options])
    return options[choice]
    
  def feedback(self,info,chosen):
    W=self.weight
    a=self.alpha
    for j,v in info:
      self.lastValue[j]=v
      if j==chosen: value=v
      if j not in W: W[j]=self.expectedPayoff
    
    for j,v in info:
      W[j]=W[j]*(1-a)+v*a

    if len(self.lastValue)>1:
      self.variability=self.variability*(1-a)+abs(value-max(self.lastValue.values()))*a
      
      
    
class LossAversion:
  def __init__(self,kappa,**args):
    self.kappa=kappa
    self.values={}
    self.trials=[]
    
  def choose(self,options):
    assert len(options)==2
  
    for o in options:
      if o not in self.values: self.values[o]=[]
    for o in options:
      if len(self.values[o])==0: return random.choice(options)
    
    all=self.values[options[0]]+self.values[options[1]]
    if min(all)==max(all):  
      return random.choice(options)
    
    guess=self.recallOutcome(options)
    
    others=[self.recallOutcome(options) for i in range(self.kappa)]
    
    losses={}
    totalLosses={}
    
    for o in options:
      losses[o]=0
      totalLosses[o]=0
    for g in [guess]+others:
      best=self.getBest(g)
      for o in options:
        if o!=best:  
          losses[o]+=1
          totalLosses[o]+=g[best]-g[o]
    
    best=self.getBest(guess)
    if best==options[0]: other=options[1]
    else: other=options[0]
    
    if losses[best]>losses[other] and totalLosses[best]>totalLosses[other]:
      best=other
      
    return best  
   
    
  def getBest(self,guess):
    o1,o2=guess.keys()
    v1,v2=guess[o1],guess[o2]
    if v1>v2: return o1
    else: return o2
         
  def recallOutcome(self,options):
   while True:   
    trial=random.choice(self.trials)
    
    guess={options[0]:None,options[1]:None}
    for j,v in trial:
      guess[j]=v
    if None in guess.values():
      for k,v in guess.items():
        if v==None:
          guess[k]=random.choice(self.values[k])
        
    if min(guess.values())!=max(guess.values()):    
      return guess    
           
         
    
  def feedback(self,info,chosen):
    for j,v in info:
      if j not in self.values: self.values[j]=[]
      self.values[j].append(v)
    self.trials.append(info)  
    

class RELACS:
  def __init__(self,meta_random=False,no_fbr=False,no_la=False,no_sbr=False,**args):
    self.strategies=[]
    if not no_fbr: self.strategies.append(FastBestReply(**args))
    if not no_la: self.strategies.append(LossAversion(**args))
    if not no_sbr: self.strategies.append(SlowBestReply(**args))
    
    #print self.strategies
    
    if meta_random:
      self.meta=Dummy(**args)
    else:
      self.meta=SlowBestReply(**args)  

    self.lastChosen=None
  def choose(self,options):
    strategy=self.meta.choose(self.strategies)
    self.lastChosen=strategy
    return strategy.choose(options)
  def feedback(self,info,chosen):
    for s in self.strategies:
      s.feedback(info,chosen)
    if self.lastChosen is not None:
      for j,v in info:
        if j==chosen:
          self.meta.feedback([[self.lastChosen,v]],self.lastChosen)
    
    

class Dummy:
  def __init__(self,**args):
    pass
  def choose(self,options):
    return random.choice(options)  
  def feedback(self,info,chosen):
    pass  
