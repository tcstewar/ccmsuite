from __future__ import generators
import ccm

class Timer(ccm.Model):
    def __init__(self,startpulse=0.011,a=1.1,b=0.015):
        self.startpulse=startpulse
        self.a=a
        self.b=b
        
        self.count=0
        self.t=self.startpulse    
        self.start()
    def reset(self):
        yield self.startpulse
        self.count=0
        self.t=self.startpulse    
    def start(self):
        while True:
            self.t=self.random.gauss(self.a*self.startpulse,self.a*self.startpulse*self.b)
            self.count+=1
            yield self.t,reset.finished

