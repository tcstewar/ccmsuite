import shelve
import os

import numpy
from bootstrapci import bootstrapci                

statistics={
    'mean':numpy.mean,
    'sd':numpy.std,
    'median':numpy.median,
    }


class Summary:
    def __init__(self,data,stats,measure):
        self.stats=stats
        self.measure=measure
        self.data=data
        
        raw=self.stats.get_raw(measure)
        
        self.data['N']=len(raw)
    
    def get_stat(self,stat,bootstrap_samples=1000,confidence=0.95):    
        code=(stat,bootstrap_samples,confidence)
        if code not in self.data:
            if stat in statistics:            
                raw=self.stats.get_raw(self.measure)
                skeys=statistics.keys()
                cis=bootstrapci(raw,[statistics[k] for k in skeys],n=bootstrap_samples,p=confidence)
                for i in range(len(skeys)):
                    self.data[(skeys[i],bootstrap_samples,confidence)]=cis[i]
            
            self.stats.summary[self.measure]=self.data
        
        return self.data.get(code,(None,(None,None)))
    
            
        
    def getN(self):
        return self.data['N']
        

def parse_value(x):
    if type(x) is str:
        if x.startswith('[') and x.endswith(']'):
            return [parse_value(s) for s in x[1:-1].split(', ')]
        if x.startswith('(') and x.endswith(')'):
            return [parse_value(s) for s in x[1:-1].split(', ')]
        if x.startswith('"') and x.endswith('"'):
            return x[1:-1]
        if x.startswith("'") and x.endswith("'"):
            return x[1:-1]
        try:
            return int(x)
        except:
            try: 
                return float(x)
            except:
                pass
    return x                 

class Stats:
    def __init__(self,dir):
        self.dir=dir
        self.raw=None
        self.valid=True
        try:
            self.summary=shelve.open('%s/summary'%self.dir)
            self.N=self.summary.get('_N',0)
            self.check_for_new()
        except:
            self.summary=dict(_N=0,_measures=[],_name=[])
            self.valid=False
            
        
    def check_for_new(self):
        found_new=False
        names=self.summary.get('_name',[])
        for fn in os.listdir(self.dir):
            if fn.endswith('.data') and fn not in names:
                self.add(fn)
                found_new=True
        if found_new:                 
            self.summary.sync()        
        
    def load_raw(self):    
        if not self.valid: return
        self.raw=shelve.open('%s/rawdata'%self.dir)
        
    def add(self,name):    
        if self.raw is None: self.load_raw()
        new=self.load_from_name(name)
        new['_name']=name
        
        keys=self.raw.keys()
        
        for k in new.keys():            
            if k not in keys: 
                if self.N==0: self.raw[k]=[]
                self.raw[k]=[None]*self.N
        for k in keys:
            if k not in new: new[k]=None
        for k in new.keys():
            v=self.raw[k]
            v.append(new[k])
            self.raw[k]=v
            
        self.summary.clear()
        self.summary['_name']=self.raw['_name']
        self.N=len(self.raw['_name'])
        self.summary['_N']=self.N
        self.summary['_measures']=[k for k in self.raw.keys() if k[0]!='_']
    
    def load_from_name(self,name):
        fn='%s/%s'%(self.dir,name)
        d={}
        for line in file(fn).readlines():
            k,v=line.strip().split('=',1)
            v=parse_value(v)
            d[k]=v
        return d    
    
    def measures(self):
        return self.summary['_measures']
    
    def get_raw(self,m):
        if not self.valid: return []
        if self.raw is None: self.load_raw()            
        return self.raw[m]
        
    
    def measure(self,m):
        if not self.summary.has_key(m):        
            self.summary[m]={}
        return Summary(self.summary[m],self,m)    
            
        
    
        
