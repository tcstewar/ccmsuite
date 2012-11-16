import unittest

from ccm.lib import nef
import numpy

class TestNEF(unittest.TestCase):
    def _test_spike_rate(self):
        n=nef.ScalarNode()
        n.configure(neurons=1,t_ref=0.002,t_rc=0.02)
        n.alpha[:]=3.34179049952
        n.Jbias[:]=1.46335060944
        n.basis[:]=1
        n.configure_spikes()
        
        n.set(1)
        total=0
        for i in range(10000):
            n.tick()
            if n._output[0]>=0:
                total+=1 
        self.assertEqual(40,total)
        
    def _test_spike_represent(self):
        n=nef.VectorNode(2)
        n.configure(neurons=20,apply_noise=False)
        n.configure_spikes()
        n2=nef.VectorNode(2)
        n2.configure(neurons=20,apply_noise=False)
        n.set([-0.1,0.8])
        n2.set([-0.1,0.8])
        
        v=0
        for i in range(1000):
            n.tick()
            n2.tick()
            v+=n.value()
            #if i%100==99: print (i+1),v/(i+1),n2.value()
        self.assertAlmostEqual(v[0]/1000,n2.value()[0],1)
        self.assertAlmostEqual(v[1]/1000,n2.value()[1],1)
           
    def _test_spike_connect_s_d(self):
        n=nef.VectorNode(2)
        n.configure(neurons=20,apply_noise=False)
        n.configure_spikes(pstc=0.06)
        n2=nef.VectorNode(2)
        n.set([-0.9,0.2])
        n.connect(n2)
        
        N=2000
        v=0
        for i in range(N):
            n.tick()
            v+=n.value()
            #if i%100==99: print (i+1),v/(i+1),n2.value()
        self.assertAlmostEqual(v[0]/N,n2.value()[0],1)
        self.assertAlmostEqual(v[1]/N,n2.value()[1],1)

    def _test_spike_connect_d_s_d(self):
        a=nef.ScalarNode(noise=0)
        b=nef.ScalarNode()
        c=nef.ScalarNode(noise=0)
        
        b.configure(neurons=30,apply_noise=False)
        b.configure_spikes(pstc=0.03)
        
        a.set(-0.3)
        a.connect(b)
        b.connect(c)

        N=2000
        for i in range(N):
            b.tick()
            if i%100==99: print (i+1),c.value()
        self.assertAlmostEqual(a.value(),c.value(),1)
        self.assertAlmostEqual(a.value(),c.value(),1)

    def test_spike_connect_d_s_s_d(self):
        a=nef.ScalarNode(noise=0)
        b=nef.ScalarNode()
        c=nef.ScalarNode()
        d=nef.ScalarNode(noise=0)
        
        b.configure(neurons=30,apply_noise=False)
        b.configure_spikes(pstc=0.03)

        c.configure(neurons=30,apply_noise=False)
        c.configure_spikes(pstc=0.03)
        
        a.set(0.7)
        a.connect(b)
        b.connect(c)
        c.connect(d)

        N=2000
        for i in range(N):
            b.tick()
            #if i%100==99: print (i+1),d.value()
        self.assertAlmostEqual(a.value(),d.value(),1)
        self.assertAlmostEqual(a.value(),d.value(),1)


        
    
if __name__ == '__main__':
    unittest.main()     
    
  
