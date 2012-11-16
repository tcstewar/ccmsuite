size=10
trials=10
display_time=3

import ccm
from ccm.lib.actr import *
log=ccm.log(data=True)


class PairedExperiment(ccm.Model):
  word=ccm.Model(visible=False,x=0.5,y=0.5,font='Arial 20',type='Text')
  number=ccm.Model(visible=False,x=0.5,y=0.5,font='Arial 20',type='Number')
  
  def start(self):
      pairs=[('bank','0'),('card','1'),('dart','2'),('face','3'),
             ('game','4'),('hand','5'),('jack','6'),('king','7'),
             ('lamb','8'),('mask','9'),('neck','0'),('pipe','1'),
             ('quip','2'),('rope','3'),('sock','4'),('tent','5'),
             ('vent','6'),('wall','7'),('xray','8'),('zinc','9')]
      items=self.random.sample(pairs,size)      
      scores=[]
      times=[]
      for i in range(trials):
        score=0
        time=0
        self.random.shuffle(items)
        for w,n in items:
          self.word.text=w
          self.word.visible=True
          start=self.now()
          self.key=None
          yield self.key_pressed,display_time
          self.word.visible=False
          
          if self.key==n:
            score+=1
            time+=self.now()-start
          self.number.text=n
          self.number.visible=True
          yield display_time
          self.number.visible=False
        scores.append(score)
        times.append(time)
      for i in range(1,trials):
        log.score[i]=scores[i]
        if scores[i]>0: times[i]=times[i]/scores[i]
        log.time[i]=times[i]
   
  def key_pressed(self,key):
    self.key=key      
        
        
      

    
      
    
    
    
    
    
    

env=PairedExperiment()
ccm.display(env)
env.run()


