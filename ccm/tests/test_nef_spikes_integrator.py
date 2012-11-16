import unittest

from ccm.lib import nef
import numpy

class TestNEF(unittest.TestCase):
    def test_spike_integrator(self):
        n1=nef.ScalarNode()
        n1.configure(neurons=30,t_ref=0.002,t_rc=0.02)
        n1.configure_spikes(pstc=0.02,dt=0.001)
        n2=nef.ScalarNode()

        n0=nef.ScalarNode()
        n0.connect(n1,weight=0.02*3.1415*2)

        n1.connect(n1)
        n1.connect(n2)


        t=numpy.arange(1000)*n1.dt
        input=numpy.cos(3.1415*t*2)
        vv=[]
        for i in xrange(1000):
            n0.set(input[i])
            n1.tick()
            vv.append(n2.value())
            #if i%50==0: print i,n1.value(),n2.value()

        self.assertTrue(vv[250]>0.8)
        self.assertTrue(abs(vv[500])<0.2)
        self.assertTrue(vv[750]<-0.8)
        self.assertTrue(abs(vv[999])<0.2)
        
        import pylab
        pylab.plot(t,vv)
        pylab.plot(t,input)
        pylab.show()


        
    
if __name__ == '__main__':
    unittest.main()     
    
  
