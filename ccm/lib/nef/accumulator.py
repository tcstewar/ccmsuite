import numpy
from math import exp

class SpecificAccumulator:
    def __init__(self,dimensions,tau):
        self.tau=tau
        self.value=numpy.zeros(dimensions)
    def add(self,value,dt):
        if self.tau<dt or dt is None:
            self.value+=value
        else:
            self.value+=value*(dt/self.tau)
    def tick(self,dt):
        if self.tau<dt or dt is None:
            self.value[:]=0
        else:
            self.value-=self.value*(dt/self.tau)
        


class Accumulator:
    def __init__(self,dimensions):
        self.accs={}
        self.dimensions=dimensions
    def add(self,value,tau,dt):
        acc=self.accs.get(tau,None)
        if acc is None:
            acc=SpecificAccumulator(self.dimensions,tau)
            self.accs[tau]=acc
        acc.add(value,dt)
    def tick(self,dt):
        for a in self.accs.values(): a.tick(dt)
    def value(self):
        v=None
        for a in self.accs.values():
            if v is None: v=numpy.array(a.value)
            else: v+=a.value
        if v is None: v=numpy.zeros(self.dimensions)
        return v
        


