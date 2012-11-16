

import math
import numpy
import ccm.lib.nef

# DxD discrete fourier transform matrix            
def discrete_fourier_transform(D):
    m=[]
    for i in range(D):
        row=[]
        for j in range(D):            
            row.append(complex_exp((-2*math.pi*1.0j/D)*(i*j))/math.sqrt(D))
        m.append(row)
    return m

# DxD discrete inverse fourier transform matrix            
def discrete_fourier_transform_inverse(D):
    m=[]
    for i in range(D):
        row=[]
        for j in range(D):            
            row.append(complex_exp((2*math.pi*1.0j/D)*(i*j))/math.sqrt(D))
        m.append(row)
    return m

# formula for e^z for complex z
def complex_exp(z):
    a=z.real
    b=z.imag
    return math.exp(a)*(math.cos(b)+1.0j*math.sin(b))



def complex_multiply(x):
    a=x[0]+x[1]*1j
    b=x[2]+x[3]*1j
    c=a*b
    return numpy.array([c.real,c.imag])


def make_convolution(a,b,c,noise=0,scale=1):
    N=a.dimensions
    
    fftm=numpy.array(discrete_fourier_transform(N))
    ifftm=numpy.array(discrete_fourier_transform_inverse(N))
    convolver=[]
    for i in range(N):
        wr=fftm[:,i].real
        wi=fftm[:,i].imag
        z=numpy.zeros(N)
        
        conv=ccm.lib.nef.VectorNode(4,noise=noise,min=-0.1,max=0.1)
        a.connect(conv,weight=scale*numpy.vstack([wr,wi,z,z]))
        b.connect(conv,weight=scale*numpy.vstack([z,z,wr,wi]))
        convolver.append(conv)

        w=numpy.vstack([ifftm[:,i].real,-ifftm[:,i].imag])
        conv.connect(c,func=complex_multiply,weight=w.T)

    return convolver
    
def make_invert(N):
    invert=numpy.eye(N)
    order=numpy.arange(0,N)
    order=order[::-1]
    order=numpy.hstack((order[-1],order[:-1]))
    return invert[order]


def make_deconvolution(a,b,c,noise=0,scale=1):
    N=a.dimensions
    
    invert=make_invert(N)
    
    fftm=numpy.array(discrete_fourier_transform(N))
    ifftm=numpy.array(discrete_fourier_transform_inverse(N))
    convolver=[]
    for i in range(N):
        wr=fftm[:,i].real
        wi=fftm[:,i].imag
        z=numpy.zeros(N)
        
        conv=ccm.lib.nef.VectorNode(4,noise=noise)
        a.connect(conv,weight=scale*numpy.vstack([wr,wi,z,z]))
        b.connect(conv,weight=scale*numpy.dot(numpy.vstack([z,z,wr,wi]),invert))
        convolver.append(conv)

        w=numpy.vstack([ifftm[:,i].real,-ifftm[:,i].imag])
        conv.connect(c,func=complex_multiply,weight=w.T)
    return convolver

