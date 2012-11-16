# Interface to Nengo neural simulator
#   http://sourceforge.net/projects/nengo/

from ccm.model import Model

import java
from ca.nengo.model import *
from ca.nengo.model.impl import *
from ca.nengo.model.nef.impl import *
from ca.nengo.model.neuron.impl import *
from ca.nengo.math.impl import *
from ca.nengo.util import *
from ca.nengo.util.impl import *
from ca.nengo.sim.impl import *
from ca.nengo.sim import *


class CCMBaseNode(Node,Probeable):
    _name="CCMNode"
    def __init__(self):
        self.listeners=[]
        self._origins={}
        self._terminations={}
        self._states=java.util.Properties()
        self.setMode(SimulationMode.DEFAULT)

    def reset(self,randomize=False):
        pass
        
    def getName(self):
        return self._name
    def setName(self,name):
        VisiblyMutableUtils.nameChanged(self, self.getName(), name, self.listeners)
        self._name=name

    def addChangeListener(self,listener):
        self.listeners.append(listener)
    def removeChangeListener(self,listener):
        self.listeners.remove(listener)

    def run(self):
        pass

    def getOrigins(self):
        return self._origins.values()
    def getOrigin(self,name):
        return self._origins[name]
    def addOrigin(self,origin):
        self._origins[origin.name]=origin
        self._states.setProperty(origin.name,"CCMSuite data")

    def getTerminations(self):
        return self._terminations.values()
    def getTermination(self,name):
        return self._terminations[name]
    def addTermination(self,termination):
        self._terminations[termination.name]=termination

    def getDocumentation(self):
        return ""

    def clone(self):
        raise java.lang.CloneNotSupportedException()

    def setMode(self,mode):
        self._mode=mode
    def getMode(self):
        return self._mode

    def listStates(self):
        return self._states

        






class CCMSimulator(LocalSimulator):
    def __init__(self,model_class):
        LocalSimulator.__init__(self)
        self._model_class=model_class
        self.model=self._model_class()
        self.model.run(limit=0)

    def initialize(self,network):
        self._network=network
        LocalSimulator.initialize(self,network)

    def resetNetwork(self,randomize=False):
        java.lang.System.out.println('resetting')
        self.model=self._model_class()
        self.model.run(limit=0)
        LocalSimulator.resetNetwork(self,randomize)

    def run(self,startTime,endTime,stepSize):
        for it in self.probes:
            it.reset()

        self.fireSimulatorEvent(SimulatorEvent(0,SimulatorEvent.Type.STARTED))
        time=startTime
        thisStepSize=stepSize

        c=0
        while time<endTime:
            c+=1
            if c%100==99: java.lang.System.out.println("Step %d %f"%(c+1,min(endTime,time+thisStepSize)))
            if time+1.5*thisStepSize>endTime:
                thisStepSize=endTime-time
            self.step(time,time+thisStepSize)

            currentProgress=(time-startTime)/(endTime-startTime)
            self.fireSimulatorEvent(SimulatorEvent(currentProgress,SimulatorEvent.Type.STEP_TAKEN))
            time+=thisStepSize
            

        self.fireSimulatorEvent(SimulatorEvent(1.0,SimulatorEvent.Type.FINISHED))

    def step(self,start,end):
        self.model.run(limit=end-self.model.now())

        for p in self._network.projections:
            p.termination.values=p.origin.values
        
        for n in self._network.nodes:
            n.run(start,end)

        for p in self.probes:
            p.collect(end)

class CCMTermination(Termination):
    def __init__(self,name,node,tau):
        self._name=name
        self._node=node
        self._tau=tau
        self._modulatory=False
        self._values=[0]

    def getName(self):
        return self._name
    def getDimensions(self):
        return 1
    def getNode(self):
        return self._node
    def getTau(self):
        return self._tau
    def setTau(self,tau):
        self._tau=tau
    def getModulatory(self):
        return self._modulatory
    def setModulatory(self,modulatory):
        self._modulatory=modulatory

    def setValues(self,values):
        self._values=values.values
    def getOutput(self):
        return self._values[0]

class CCMVectorTermination(CCMTermination):
    def __init__(self,name,node,tau,dimensions):
        self._dimensions=dimensions
        CCMTermination.__init__(self,name,node,tau)
    def getDimensions(self):
        return self._dimensions
    def setValues(self,values):
        self._values=values.values
    def getOutput(self):
        return self._values
    
    
        

class CCMNode(CCMBaseNode):
    def __init__(self,name,simulator,path):
        CCMBaseNode.__init__(self)
        self._name=name
        self._simulator=simulator
        self._path=path

        #self._integrator=LinearSynapticIntegrator(0.0005,Units.UNK)
        #self._integrator.node=self

        self._mainOrigin=BasicOrigin(self,'origin',self.checkDimension(),Units.UNK)
        self.addOrigin(self._mainOrigin)

    def makeTermination(self,name,tauPSC):
        #t=self._integrator.addTermination(name,[1],tauPSC,False)
        t=CCMTermination(name,self,tauPSC)
        self.addTermination(t)

    def checkDimension(self):
        v=self._simulator.model
        for p in self._path: v=getattr(v,p)
        if isinstance(v,(int,float)): return 1
        else: return len(v)
        
        
    def run(self,start,end):
        v=self._simulator.model
        for p in self._path[:-1]: v=getattr(v,p)        
        
        if len(self._terminations)>0:
            #self._integrator.run(start,end)
            value=0
            for t in self._terminations.values():
                value+=t.getOutput()
            setattr(v,self._path[-1],value)
        else:
            value=getattr(v,self._path[-1])
        if isinstance(value,tuple):
            value=list(value)
        if not isinstance(value,list):
            value=[value]
            
        self._mainOrigin.values=RealOutputImpl(value,Units.UNK,v.now())

    def getHistory(self,name):
        origin=self.getOrigin(name)
        values=origin.values
        return TimeSeriesImpl([self._simulator.model.now()],[values.values],[values.units]*len(values.values))
        

        
            
class ModelNetwork(NetworkImpl):
    def __init__(self,simulator,path):
        NetworkImpl.__init__(self)
        self._simulator=simulator
        self._path=path
        self._translatedOrigins={}
        self._translatedTerminations={}
        self._states=java.util.Properties()
    def createTermination(self,name,translator):
        termination=CCMVectorTermination(name,self,1,translator.getDimensions())
        self.exposeTermination(termination,name)
        self._translatedTerminations[name]=(translator,termination)
    def createOrigin(self,name,translator):
        origin=BasicOrigin(self,name,translator.getDimensions(),Units.UNK)
        self.exposeOrigin(origin,name)
        self._translatedOrigins[name]=(translator,origin)
    def run(self,start,end):
        model=self._simulator.model
        for p in self._path: model=getattr(model,p)        
        for (trans,origin) in self._translatedOrigins.values():
            origin.setValues(start,end,trans.convertToVector(model))
        NetworkImpl.run(self,start,end)
        for (trans,termination) in self._translatedTerminations.values():
            trans.applyVector(model,termination.getOutput())
                
        

    def listStates(self):
        states=NetworkImpl.listStates(self)
        for name in self._translatedOrigins.keys():
            states.setProperty(name,"translated model")
        return states

    def getHistory(self,name):
        if name in self._translatedOrigins:
            trans,origin=self._translatedOrigins[name]
            values=origin.values
            return TimeSeriesImpl([self._simulator.model.now()],[values.values],[values.units]*len(values.values))
        else:
            return NetworkImpl.getHistory(self,name)
        
            
            
    


        
class CCMModelNetwork(NetworkImpl):
    def __init__(self,model_class):
        NetworkImpl.__init__(self)        
        self._simulator=CCMSimulator(model_class)
        self.setName(model_class.__name__)
        self.build(self)
    def getSimulator(self):
        return self._simulator

    def build(self,network,model=None,path=[]):
        if model is None:
            model=self._simulator.model
        for k,v in model.__dict__.items():
            if k[0]=='_': continue
            if isinstance(v,(int,float)):
                node=CCMNode(name=k,simulator=self.simulator,path=path+[k])
                network.addNode(node)
            elif isinstance(v,(tuple,list)) and len(v)>0 and isinstance(v[0],(int,float)):
                node=CCMNode(name=k,simulator=self.simulator,path=path+[k])
                network.addNode(node)
            elif isinstance(v,Model) and k not in ['parent']:
                node=ModelNetwork(self._simulator,path+[k])
                node.name=k
                self.build(node,v,path+[k])
                network.addNode(node)

def create(model_class):
    return CCMModelNetwork(model_class)
