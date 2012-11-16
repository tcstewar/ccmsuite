import random

class QLearn:
  def __init__(self,actions,epsilon=0.1,alpha=0.2,gamma=0.9,initial=0.0):
    self.q={}

    self.epsilon=epsilon
    self.alpha=alpha
    self.gamma=gamma
    self.actions=actions
    self.initial=initial

  def getQ(self,state,action):
    return self.q.get((state,action),self.initial)
  def learnQ(self,state,action,value):
    oldv=self.q.get((state,action),None)
    if oldv==None:
      self.q[(state,action)]=value
    else:
      self.q[(state,action)]=oldv+self.alpha*(value-oldv)

  def chooseAction(self,state=None):
    if random.random()<self.epsilon:
      action=random.choice(self.actions)
    else:
      if isinstance(state,list): state=tuple(state)
      q=[self.getQ(state,a) for a in self.actions]
      maxQ=max(q)
      count=q.count(maxQ)
      if count>1:
        best=[i for i in range(len(self.actions)) if q[i]==maxQ]
        i=random.choice(best)
      else:
        i=q.index(maxQ)

      action=self.actions[i]
    return action

  def learn(self,state1,action1,reward,state2):
    if isinstance(state1,list): state1=tuple(state1)
    if isinstance(state2,list): state2=tuple(state2)
    maxqnew=max([self.getQ(state2,a) for a in self.actions])
    self.learnQ(state1,action1,reward+self.gamma*maxqnew)




