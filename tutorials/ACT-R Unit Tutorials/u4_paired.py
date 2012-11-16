import ccm
from ccm.lib.actr import *
log=ccm.log(html=True)

size=1
trials=10
display_time=5

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
      log.scores=scores
      log.times=times      
   
  def key_pressed(self,key):
    self.key=key      
        
        
      

    
      
      
class Paired(ACTR):
  goal=Buffer()
  retrieve=Buffer()
  memory=Memory(retrieve,threshold=-2,latency=0.35)
  DMBaseLevel(memory)
  DMNoise(memory,noise=0.5)
  
  visual=Buffer()
  location=Buffer()
  vision=Vision(visual,location)    
  
  motor=Motor()
  
  def attendProbe(goal='state:start',vision='busy:False',location='?x ?y'):
    vision.examine('?x ?y')
    goal.modify(state='attendingProbe')
    location.clear()
    
  def detectStudyItem(goal='state:readStudyItem word:?w!None',vision='busy:False',location='?x ?y'):
    vision.examine('?x ?y')
    goal.modify(state='attendingTarget')
    location.clear()
    
  def associate(goal='state:attendingTarget word:?word!None num:?num',visual='type:Number text:?text'):
    memory.add('word:?word num:?text')
    visual.clear()
    goal.set('state:start word:None num:None')
    
  def readProbe(goal='state:attendingProbe word:None',visual='type:Text text:?word'):
    memory.request('word:?word')
    goal.modify(state='testing',word=word)
    visual.clear()
    
  def recall(goal='state:testing word:?word',retrieve='word:?word num:?num',motor='busy:False'):
    motor.press(num)
    goal.modify(state='readStudyItem')
    
  def cannotRecall(goal='state:testing word:?word',memory='error:True'):
    goal.modify(state='readStudyItem')
    
    
    
    
    
    

env=PairedExperiment()
env.model=Paired()
ccm.log_everything(env)
env.model.goal.set('state:start word:None num:None')
ccm.display(env)
env.run()


