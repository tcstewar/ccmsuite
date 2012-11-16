import numpy
from numpy.fft import fft,ifft
from numpy.linalg import norm

def set_random_seed(seed):
    numpy.random.seed(seed)

class HRR:
    def __init__(self,N=None,data=None):
        if data is not None:
            self.v=numpy.array(data)
        elif N is not None:
            self.randomize(N)
        else:
            raise Exception('Must specify size or data for HRR')
    def length(self):
        return norm(self.v)        
    def normalize(self):
        nrm=norm(self.v)
        if nrm>0: self.v/=nrm
    def __str__(self):
        return str(self.v)
    def randomize(self,N=None):
        if N is None: N=len(self.v)
        sd=1.0/N
        self.v=numpy.random.randn(N)*sd
        self.normalize()
    def __add__(self,other):
        return HRR(data=self.v+other.v)
    def __iadd__(self,other):
        self.v+=other.v
        return self
    def __neg__(self):
        return HRR(data=-self.v)    
    def __sub__(self,other):
        return HRR(data=self.v-other.v)
    def __isub__(self,other):
        self.v-=other.v
        return self
    def __mul__(self,other):
        if isinstance(other,HRR):
            x=ifft(fft(self.v)*fft(other.v)).real
            x=x/norm(x)
            return HRR(data=x)
        else:
            return HRR(data=self.v*other)
    def convolve(self,other):
        x=ifft(fft(self.v)*fft(other.v)).real
        return HRR(data=x)
    def __rmul__(self,other):
        if isinstance(other,HRR):
            x=ifft(fft(self.v)*fft(other.v)).real
            x=x/norm(x)
            return HRR(data=x)
        else:
            return HRR(data=self.v*other)
    def __imul__(self,other):
        self.v=ifft(fft(self.v)*fft(other.v))
        return self
    def compare(self,other):
        scale=norm(self.v)*norm(other.v)
        if scale==0: return 0
        return numpy.dot(self.v,other.v)/(scale)
    def dot(self,other):
        return numpy.dot(self.v,other.v)
    def distance(self,other):
        return 1-self.compare(other)
    def __invert__(self):
        return HRR(data=self.v[numpy.r_[0,len(self.v)-1:0:-1]])
    def __len__(self):
        return len(self.v)
    def copy(self):
        return HRR(data=self.v)
    def mse(self,other):
        err=0
        for i in range(len(self.v)):
            err+=(self.v[i]-other.v[i])**2
        return err/len(self.v)

    def sparcify_probability(self,prob):
        r=numpy.random.random(self.v.shape)
        while numpy.all(r>prob): r=numpy.random.random(self.v.shape)
        self.v=numpy.where(r>prob,0,self.v)
    def sparcify_threshold(self,threshold):
        self.v=numpy.where(self.v<threshold,0,self.v)

class Cleanup:
    def __init__(self,limit=None):
        self.vectors=None
        self.hrrs=None
        self.size=None
        self.count=0
        self.limit=limit
    def add(self,hrr):
        if self.vectors is None:
            self.size=len(hrr)
            self.vectors=numpy.array([hrr.v])
            self.hrrs=[hrr]
        else:
            if self.size!=len(hrr):
                raise Exception('Added HRR of inconsistent size to cleanup memory')
            self.hrrs.append(hrr)
            self.vectors=numpy.append(self.vectors,[hrr.v],axis=0)
        self.count+=1
    def clean(self,hrr):
        if len(self.vectors)==0:
            raise Exception('No vectors in cleanup memory')
        best=None
        best_v=None
        for v in self.hrrs:
            c=hrr.compare(v)
            if self.limit is not None and c<self.limit: continue
            if best is None or c>best:
                best=c
                best_v=v
        return best_v
    def all(self,hrr):
        r=[]
        for h in self.hrrs:
            r.append((hrr.compare(h),h))
        return r


class Mapper:
    def __init__(self,limit=None):
        self.cleanup=Cleanup(limit=limit)
        self.map={}
    def add(self,input,output):
        self.map[input]=output
        self.cleanup.add(input)
    def do(self,input):
        v=self.cleanup.clean(input)
        if v is not None:
            v=self.map[v]
        return v
    def all(self,input):
        r=[]
        for c,v in self.cleanup.all(input):
            r.append((c,self.map[v]))
        return r
        
        

        
                       
                       
from math import sin,pi,acos
class Vocabulary:
    def __init__(self,dimensions,randomize=True):
        self.dimensions=dimensions
        self.randomize=randomize
        self.hrr={}
        ident=[0]*dimensions
        ident[0]=1.0
        self.hrr['I']=HRR(data=ident)
    def __getitem__(self,key):
        if key not in self.hrr:
            if self.randomize:    
                self.hrr[key]=HRR(self.dimensions)
            else:
                v=[0]*self.dimensions
                v[len(self.hrr)]=1.0
                self.hrr[key]=HRR(data=v)    
        return self.hrr[key]        
    def parse(self,text):
        return eval(text,{},self)
        
    def text(self,v):
        matches=[]
        
        names=self.hrr.keys()
        names.sort()
        names.remove('I')

        for i in range(len(names)):        
            k=names[i]
            val=self.hrr[k]
            c=val.compare(v)
            if c>0: matches.append((c,k))
            for j in range(i+1,len(names)):
                k2=names[j]
                val2=self.hrr[k2]
                c=(val*val2).compare(v)                
                if c>0: matches.append((c,'%s*%s'%(k,k2)))
        matches.sort()
        matches.reverse()
        r=[]
        for m in matches:
            if m[0]>0.3: r.append(m)
            elif len(r)<2: r.append(m)
            else: break
        return '+'.join(['%s(%0.2f)'%(k,c) for (c,k) in r])
         
         
        
    def prob_cleanup(self,compare,vocab_size,steps=10000):
        # see http://yamlb.wordpress.com/2008/05/20/why-2-random-vectors-are-orthogonal-in-high-dimention/ 
        #  for argument that the probability af two random vectors being a given angle apart is
        #  proportional to sin(angle)^(D-2)
        def prob_func(angle): 
            return sin(angle)**(self.dimensions-2)
        angle=acos(compare)
        num=0
        dnum=angle/steps
        denom=0
        ddenom=pi/steps
        for i in range(steps):
            num+=prob_func(pi-angle+dnum*i)
            denom+=prob_func(ddenom*i)
        num*=dnum
        denom*=ddenom    
        perror1=num/denom    
        pcorrect=(1-perror1)**vocab_size
        return pcorrect
        
        
