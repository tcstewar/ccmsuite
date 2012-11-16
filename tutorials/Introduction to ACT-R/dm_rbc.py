repeat=100             # number of repeated choices
noise=0.25             # noise in declarative memory
threshold=0            # declarative memory retrieval threshold (None for no threshold)
initialvalue=None      # place a value in DM to encourage exploration


import ccm
log=ccm.log(html=True) 

# an environment presenting repeated choices.  One choice gives the high
# reward with probability prob (and the low reward otherwise), while the
# other always gives the medium reward.

class Env(ccm.Model):
    waiting=False    # whether we are currently waiting for a response
    
    def start(self):
        self.countA=0
        self.countB=0
        for i in range(repeat):
            self.waiting=True
            yield self.choice   # wait for a response
            self.waiting=False
            yield 1             # show the reward for 1 second before continuing
            self.reward=None
        self.p=self.countA/float(repeat)

    # determine reward when a choice is made
    def choice(self,option):
        if option=='A':
            if self.random.random()<self.prob: 
                self.reward=self.high
            else: 
                self.reward=self.low
            self.countA+=1
        elif option=='B':
            self.reward=self.medium
            self.countB+=1





from ccm.lib.actr import *

class BlendingModel(ACTR):
    goal=Buffer()
    imaginal=Buffer()
    retrieval=Buffer()
    memory=BlendingMemory(retrieval,threshold=threshold)
    DMNoise(memory,noise=noise)
    DMBaseLevel(memory)

    def initialize():
        goal.set('wait X')    
        imaginal.set('A:None B:None')
        if initialvalue is not None:
            memory.add('A %d'%initialvalue)
            memory.add('B %d'%initialvalue)
    
    def recallA(goal='wait X',top='waiting:True',imaginal='A:None',memory='busy:False error:False'):
        memory.request('A ?')
        goal.set('wait A')
    def recallB(goal='wait X',top='waiting:True',imaginal='B:None',memory='busy:False error:False'):
        memory.request('B ?')
        goal.set('wait B')
    def storeA(goal='wait A',top='waiting:True',imaginal='A:None B:?B',retrieval='A ?reward'):
        #memory.add(retrieval)
        retrieval.clear()
        imaginal.set('A:?reward B:?B')
        goal.set('wait X')
    def storeB(goal='wait B',top='waiting:True',imaginal='B:None A:?A',retrieval='B ?reward'):
        #memory.add(retrieval)
        retrieval.clear()
        imaginal.set('B:?reward A:?A')
        goal.set('wait X')

    def norecallA(goal='wait A',top='waiting:True',memory='error:True'):
        goal.set('choose A')
    def norecallB(goal='wait B',top='waiting:True',memory='error:True'):
        goal.set('choose B')


    def doEqualA(goal='wait',top='waiting:True',imaginal='A:?X!None B:?X'):
        goal.set('choose A')
    def doEqualB(goal='wait',top='waiting:True',imaginal='A:?X!None B:?X'):
        goal.set('choose B')

    def doUnEqual(goal='wait',top='waiting:True',imaginal='A:?A!None B:?B!None!?A'):
        if float(A)<float(B): goal.set('choose B')
        else: goal.set('choose A')

    def choose(goal='choose ?X',top='waiting:True'):
        top.choice(X)
        goal.set('reward ?X')

    def doReward(goal='reward ?X',top='reward:?reward!None'):
        memory.add('?X ?reward')
        goal.set('wait X')
        imaginal.set('A:None B:None')


class SequentialModel(ACTR):
    goal=Buffer()
    goal.set('wait X')    

    imaginal=Buffer()
    imaginal.set('A:None B:None')

    history=Buffer()
    history.set('None None')

    retrieval=Buffer()
    memory=BlendingMemory(retrieval,threshold=threshold)
    DMNoise(memory,noise=noise)
    DMBaseLevel(memory)

    if initialvalue is not None:
      for h in ['A A','A B','B A','B B']:
        memory.add('%s A %d'%(h,initialvalue))
        memory.add('%s B %d'%(h,initialvalue))
    
    def recallA(goal='wait X',top='waiting:True',imaginal='A:None',memory='busy:False error:False',history='?a ?b'):
        memory.request('?a ?b A ?')
        goal.set('wait A')
    def recallB(goal='wait X',top='waiting:True',imaginal='B:None',memory='busy:False error:False',history='?a ?b'):
        memory.request('?a ?b B ?')
        goal.set('wait B')
    def storeA(goal='wait A',top='waiting:True',imaginal='A:None B:?B',retrieval='? ? A ?reward'):
        #memory.add(retrieval)
        retrieval.clear()
        imaginal.set('A:?reward B:?B')
        goal.set('wait X')
    def storeB(goal='wait B',top='waiting:True',imaginal='B:None A:?A',retrieval='? ? B ?reward'):
        #memory.add(retrieval)
        retrieval.clear()
        imaginal.set('B:?reward A:?A')
        goal.set('wait X')

    def norecallA(goal='wait A',top='waiting:True',memory='error:True'):
        goal.set('choose A')
    def norecallB(goal='wait B',top='waiting:True',memory='error:True'):
        goal.set('choose B')


    def doEqualA(goal='wait',top='waiting:True',imaginal='A:?X!None B:?X'):
        goal.set('choose A')
    def doEqualB(goal='wait',top='waiting:True',imaginal='A:?X!None B:?X'):
        goal.set('choose B')

    def doUnEqual(goal='wait',top='waiting:True',imaginal='A:?A!None B:?B!None!?A'):
        if float(A)<float(B): goal.set('choose B')
        else: goal.set('choose A')

    def choose(goal='choose ?X',top='waiting:True'):
        top.choice(X)
        goal.set('reward ?X')

    def doReward(goal='reward ?X',top='reward:?reward!None',history='?a ?b'):
        memory.add('?a ?b ?X ?reward')
        goal.set('wait X')
        imaginal.set('A:None B:None')
        history.set('?b ?X')
        
        
    

def doTest(high,prob,low,medium):
    p=[]
    for i in range(1):
        e=Env(high=high,prob=prob,low=low,medium=medium)
        e.m=SequentialModel()
        ccm.log_everything(e)
        e.run()
        p.append(e.p)
    return sum(p)/len(p)

print doTest(high=10,prob=0.5,low=1,medium=2)
        
        
