import numpy

dtype=numpy.dtype('float32')

class Generator:
    def __init__(self,dimensions,seed,args):
        self.random=numpy.random.RandomState(seed=seed)
        self.seed=seed
        self.dimensions=dimensions
        self.args=args
        self.scale=None
        self.offset=None
    def reset(self):
        self.random.seed(self.seed)
    def get(self,N,scale=None,offset=None,dtype=numpy.dtype('float32')):
        if scale is None: scale=self.scale
        if offset is None: offset=self.offset
        data=self.generate(N,self.dimensions,self.random,*self.args)
        if data.dtype!=dtype:
            data=numpy.array(data,dtype=dtype)
        if scale is not None: data*=scale
        if offset is not None: data+=offset
        return data
    def can_continue(self,dim):
        return True

class Grid(Generator):
    def generate(N,dim,random):
        if dim == 1:
            r=numpy.linspace(-1.0,1.0,N)
            r.shape=1,N
            return r
        elif dim == 2:
            num=int(numpy.sqrt(N))
            if num*num<N: num+=1
            edge=numpy.linspace(-1,1,num)
            X,Y=numpy.meshgrid(edge,edge)
            return numpy.array([numpy.ravel(X),numpy.ravel(Y)])
        else:
            raise Exception('Cannot do grid of more than 2 dimensions')
    generate=staticmethod(generate)
    def can_continue(self,dim):
        return False

class Sphere(Generator):
    def generate(N,dim,random,clustering=None):
        samples=random.randn(dim,N)

        if clustering is not None and clustering>0:
            if clustering>0.999: return Aligned.generate(N,dim,random)
            ratio=numpy.tan((0.5+clustering/2)*numpy.pi/2)
            axes=random.randint(0,dim,N)
            samples[axes,numpy.r_[0:N]]*=ratio

        norm=numpy.linalg.norm
        sphere=numpy.apply_along_axis(lambda x: x/norm(x),0,samples)

        return sphere
    generate=staticmethod(generate)

class Cube(Generator):
    def generate(N,dim,random):
        return random.uniform(-1,1,(dim,N))
    generate=staticmethod(generate)

class Ball(Generator):
    def generate(N,dim,random,clustering=None):
        samples=Sphere.generate(N,dim,random,clustering=clustering)

        scale=random.uniform(0,1,N)**(1.0/dim)
        samples*=scale

        return samples
    generate=staticmethod(generate)
       
class DefaultSampling(Generator):
    def generate(N,dim,random):
        if dim<=2: return Grid.generate(N,dim,random)
        else: return Cube.generate(N,dim,random)
    generate=staticmethod(generate)
    def can_continue(self,dim):
        return dim>2

class Aligned(Generator):
    def generate(N,dim,random,flip=True):
        align=numpy.zeros((dim,N),dtype=dtype)
        dirs=random.randint(0,dim,N)
        if flip:
            neg=random.randint(0,2,N)*2-1
            align.T[numpy.r_[0:N],dirs]=neg
        else:
            align.T[numpy.r_[0:N],dirs]=1            
        return align
    generate=staticmethod(generate)

class OrderedAligned(Generator):
    def generate(N,dim,random):
        align=numpy.zeros((dim,N),dtype=dtype)
        dirs=numpy.arange(dim)
        dirs=numpy.resize(dirs,N)
        align.T[numpy.r_[0:N],dirs]=1            
        return align
    generate=staticmethod(generate)
    
        

def makeGenerator(code,dimensions,seed):
    args={}
    if isinstance(code,(list,tuple)):
        args=code[1:]
        code=code[0]
    klass=globals().get(code,None)
    if klass is None or not issubclass(klass,Generator):
        raise Exception('Unknown generator code: %s'%code)
        
    return klass(dimensions,seed,args)

