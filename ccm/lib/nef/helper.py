import numpy
from numpy import sqrt

def rms(x):
    return numpy.sqrt(numpy.mean((x)**2))
def plot_error(x,x_hat,title=''):
    import pylab
    
    pylab.figure()
    pylab.plot(x,x)
    pylab.plot(x,x_hat)
    pylab.twinx()
    pylab.plot(x,x_hat-x)
    pylab.title(title+' RMSE: %f'%rms(x-x_hat))
    

def hypersphere_volume(n):
    return numpy.pi**(n/2.0)/gamma(n/2.0+1)


# Gamma Function code from http://mail.python.org/pipermail/python-list/2000-June/039873.html
gammln_cof = [76.18009173, -86.50532033, 24.01409822,-1.231739516e0, 0.120858003e-2, -0.536382e-5]
gammln_stp = 2.50662827465
def gammln(xx):
	"""Logarithm of the gamma function."""
	x = xx - 1.
	tmp = x + 5.5
	tmp = (x + 0.5)*numpy.log(tmp) - tmp
	ser = 1.
	for j in range(6):
		x = x + 1.
		ser = ser + gammln_cof[j]/x
	return tmp + numpy.log(gammln_stp*ser)
	
def gamma(x):
    return numpy.exp(gammln(x))

def recode(node,values,noise=None):
    try:
        array=numpy.array(values)
    except:
        array=numpy.array([self.value_to_array(value) for value in values])
    curr=node.arrays_to_currents(array)
    curr=curr.T+node.Jbias    
    actv=node.current_to_activity(curr.T)
    if noise is not None:
        actv=node.add_activation_noise(actv,noise=noise)
    array=node.activity_to_array(actv)
    return array.T

def get_tuning_curves(node,dx=0.005,apply_sign=False):
    x=numpy.arange(node.min,node.max,dx)
    alpha=node.alpha
    if apply_sign:
        sign=numpy.sign(node.basis[:,0])
        sign.shape=sign.shape[0]
        alpha=alpha*sign
            
    J=numpy.outer(alpha,x).T+node.Jbias
    
    actv=node.current_to_activity(J.T)
    return x,actv.T

def tuning_usage(node,threshold=0):
    usage=numpy.zeros(node.neurons)
    node.sample_generator.reset()
    count=node.sample_count
    while count>0:
        s=min(count,node.sample_step_size)
        if not node.sample_generator.can_continue(node.dimensions): s=count
        samples=node.sample_generator.get(s)
        count-=s

        actv=node.array_to_activity(samples)
        actv[actv<=threshold]=0
        actv[actv>threshold]=1
        usage+=numpy.sum(actv,1)
    return usage
    
    
def make_local_basis(dim,N,striping=False):
    span1=int(sqrt(dim))
    count=N/dim
    span2=int(sqrt(count))
    basis=[]
    eye=numpy.eye(dim)
        
    for i in range(span1):
        for j in range(span2):
            for k in range(span1):
                for m in range(span2):
                    dir=1
                    if striping:
                        if m%2==1: dir=-1
                    basis.append(dir*eye[i*span1+k])    
    return basis
    
    
def make_sofm_basis(dim,neurons,distance=5,row_count=None,repeat=5):
    from ccm.lib.kohonen import SOFM
    from ccm.lib.nef.generate import Sphere
    
    distance=distance*distance
    if row_count is None:
        row_count=int(sqrt(neurons))
        
    def nHood(x):
            r=[]
            b,a=x/row_count,x%row_count
            for y in range(neurons):
                i,j=y/row_count,y%row_count
                if (a-i)**2+(b-j)**2<distance:
                    r.append(y)
            return r

    k=SOFM()
    k.setNeighbourhoodFunc(nHood)
    random=numpy.random.RandomState()
    generator=Sphere(dim,random.randint(0x7FFFFFFF),{})
    
    initial=generator.generate(neurons,generator.dimensions,generator.random).T
    for x in range(neurons):
       k.addOutputNode(x,initial[x])

    for i in range(repeat):
        data=generator.generate(neurons,generator.dimensions,generator.random).T
        for b in data:
            k.train(b)
    
    basis=numpy.array([k.weights[i] for i in range(neurons)])
    basis=[x/numpy.linalg.norm(x) for x in basis]
    
    return basis
    

