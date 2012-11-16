import numpy
from scipy.special import gamma
from numpy import pi,sqrt,sum,dot

def calc_gamma_moments(node,radius=1.0,dr=0.02,weight=0):
    N=node.neurons
    D=node.dimensions
    EUV=node.basis
    
    Cmatrix=numpy.zeros((N,N),dtype='float32')
    r=numpy.arange(-radius,radius+dr,dr)
    r2=r**2
    r3=r**3
    
    Y,X=numpy.meshgrid(r,r)
    R2=X**2+Y**2
    index=numpy.where(R2<=radius**2)
    X=X[index]
    Y=Y[index]
    R2=R2[index]
    
    d=float(D+weight)
    KD=pi**(d/2)/gamma(d/2+1)
    KD_1=pi**((d-1)/2)/gamma((d-1)/2+1)
    KD_2=pi**((d-2)/2)/gamma((d-2)/2+1)
    hsVolD=KD*radius**d
    MD=sqrt(pi)*(gamma((d)/2)/gamma((d+1)/2)-gamma((d+2)/2)/gamma((d+3)/2))
    F0=(dr/hsVolD)*KD_1*(radius**2-r2)**((d-1)/2)
    F1=(dr/hsVolD)*KD_2*MD*(radius**2-r2)**((d+1)/2)
    Fg=(dr**2/hsVolD)*KD_2*(radius**2-R2)**((d-2)/2)

    # cheating fix to stop the last value from being undefined
    F0[-1]=F0[0]
    F1[-1]=F1[1]


    F01=F0*r
    F02=F0*r2
    Moments=[[] for i in range(4)]
    for n in range(N):
        if node.lif:
            Rthres=(1-node.Jbias[n])/node.alpha[n]
        else:
            Rthres=(-node.Jbias[n])/node.alpha[n]
        Rthres=(1-node.Jbias[n])/node.alpha[n]
    
        index2=numpy.where(r>Rthres)
        an2_curr=node.alpha[n]*r[index2]+node.Jbias[n]

        an2=node.current_to_activity(an2_curr)
        Moments[0].append(sum(an2*F0[index2]))
        Moments[1].append(sum(an2*F01[index2]))
        Moments[2].append(sum(an2*F02[index2]))
        Moments[3].append(sum(an2*F1[index2]))
        
        index=numpy.where(X>Rthres)
        Xt=X[index]
        Yt=Y[index]
        
        an_curr=node.alpha[n]*Xt+node.Jbias[n]
        an=node.current_to_activity(an_curr)
        anp=an*Fg[index]
        Cmatrix[n,n]=dot(an,anp)
        for m in range(n+1,N):
            Ux=dot(EUV[n],EUV[m])
            Uy=sqrt(1-Ux**2)
            Rvalues=Ux*Xt+Uy*Yt
            am_curr=node.alpha[m]*Rvalues+node.Jbias[m]
            am=node.current_to_activity(am_curr)
            index=numpy.where(am>0)
            Cmatrix[n,m]=dot(am[index],anp[index])
            Cmatrix[m,n]=Cmatrix[n,m]
    Moments=numpy.array(Moments,dtype='float32')
    return Cmatrix,Moments

