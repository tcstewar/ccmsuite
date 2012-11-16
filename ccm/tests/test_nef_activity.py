import unittest

from ccm.lib import nef
import numpy

class TestNEF(unittest.TestCase):
    
    def test_aligned(self):
        n=nef.VectorNode(10)
        n.configure(neurons=20,basis_style='Aligned')
        for b in n.basis:
            self.assertEqual(numpy.abs(b).max(),1)
            self.assertAlmostEqual(numpy.linalg.norm(b),1,5)
    
        n=nef.VectorNode(10)
        n.configure(neurons=20,basis_style='Sphere')
        for b in n.basis:
            self.assertNotEqual(numpy.abs(b).max(),1)
            self.assertAlmostEqual(numpy.linalg.norm(b),1,5)

    def test_representation(self):
        n1=nef.ScalarNode()
        n1.configure(neurons=150,activation_noise=0.01)
        n1.set(0.3)
        n1.tick()
        self.assertAlmostEqual(n1.value(),0.3,2)

        n2=nef.VectorNode(2)
        n2.configure(neurons=200,activation_noise=0)
        n2.set([0.3,-0.5])
        n2.tick()
        self.assertAlmostEqual(n2.value()[0],0.3,1)
        self.assertAlmostEqual(n2.value()[1],-0.5,1)


    def test_connection(self):
        modes=['direct','rate']
        for m1 in modes:
            for m2 in modes:
                #print m1,m2
                n1=nef.ScalarNode()
                if m1=='rate': n1.configure(neurons=150,activation_noise=0.01)
                n2=nef.ScalarNode()
                if m2=='rate': n2.configure(neurons=150,activation_noise=0.01)
                n1.connect(n2)
                n1.set(0.3)
                n1.tick()
                n1.tick()
                #print 0.3,n2.value()
                self.assertAlmostEqual(n2.value(),0.3,1)
                n1.set(-0.7)
                n2.tick()
                n2.tick()
                #print -0.7,n2.value()
                self.assertAlmostEqual(n2.value(),-0.7,1)

                n1=nef.VectorNode(2,noise=0)
                if m1=='rate': n1.configure(neurons=300,activation_noise=0.01,basis_style='Aligned')
                n2=nef.VectorNode(2,noise=0,min=-0.5,max=0.5)
                if m2=='rate': n2.configure(neurons=300,activation_noise=0.01,basis_style='Aligned')
                n1.connect(n2,weight=0.5)
                n1.set([0.3,-0.7])
                n2.tick()
                n2.tick()
                #print [0.15,-0.35],n2.value()
                self.assertAlmostEqual(n2.value()[0],0.15,2)
                self.assertAlmostEqual(n2.value()[1],-0.35,2)

                n1=nef.VectorNode(2,noise=0)
                if m1=='rate': n1.configure(neurons=300,activation_noise=0.01,basis_style='Aligned')
                n2=nef.VectorNode(2,noise=0)
                if m2=='rate': n2.configure(neurons=300,activation_noise=0.01,basis_style='Aligned')
                n1.connect(n2,weight=numpy.array([[0,1],[1,0]]))
                n1.set([0.3,-0.7])
                n1.tick()
                n1.tick()
                #print [-0.7,0.3],n2.value()
                self.assertAlmostEqual(n2.value()[0],-0.7,1)
                self.assertAlmostEqual(n2.value()[1],0.3,1)
        
    def test_many_connections1(self):
        out=nef.ScalarNode(noise=0)
        N=10
        n=[nef.ScalarNode(noise=0) for i in range(N)]
        for i in range(N):
            n[i].configure(neurons=150,activation_noise=0.01)
            if i+1<N:
                n[i].connect(n[i+1])
            n[i].connect(out)
        n[0].set(1)

        out.tick()
        for i in range(N):
            out.tick()   
            self.assertAlmostEqual(out.value(),i+1,0)
        out.tick()
        self.assertAlmostEqual(out.value(),N,0)
       
 
    def test_accuracy(self):
        n=nef.ScalarNode(noise=0)
        n.configure(neurons=150,activation_noise=0.01,apply_noise=False)
        
        vals=numpy.arange(30)/15.0-1
        for v in vals:
            n.set(v)
            n.tick()
            #print v,n.value()
            self.assertAlmostEqual(n.value(),v,1)
    
    def test_add(self):
        samples=None
        a=nef.ScalarNode()
        b=nef.ScalarNode()
        c=nef.ScalarNode()
        a.configure(neurons=150,activation_noise=0.1,apply_noise=False,sample_count=samples)
        b.configure(neurons=150,activation_noise=0.1,apply_noise=False,sample_count=samples)
        c.configure(neurons=150,activation_noise=0.1,apply_noise=False,sample_count=samples)
        
        a.connect(c)
        b.connect(c)

        
        ab=nef.VectorNode(2)
        a.connect(ab,weight=numpy.array([1,0]))
        b.connect(ab,weight=numpy.array([0,1]))
        ab.configure(neurons=300,activation_noise=0.1,apply_noise=False,sample_count=samples)
        
        c2=nef.ScalarNode()
        c2.configure(neurons=150,activation_noise=0.1,apply_noise=False,sample_count=samples)
        ab.connect(c2,func=lambda x: x[0]+x[1])
        
        n=[-0.4,-0.3,-0.1,0,0.1,0.3,0.4]
        for x in n:
            for y in n:
                a.set(x)
                b.set(y)
                c.tick()
                c.tick()
                c.tick()
                self.assertAlmostEqual(x+y,c.value(),1)
                self.assertAlmostEqual(x+y,c2.value(),1)
    
    
    def test_many_connections2(self):
        out=nef.ScalarNode(noise=0)
        out.configure(neurons=150,activation_noise=0.1,apply_noise=False)
        N=10
        n=[nef.ScalarNode(noise=0) for i in range(N)]
        for i in range(N):
            n[i].configure(neurons=150,activation_noise=0.1,apply_noise=False)
            if i+1<N:
                n[i].connect(n[i+1])
            n[i].connect(out,weight=1.0/N)
        n[0].set(1)

        out.tick()
        for i in range(N):
            out.tick()   
            self.assertAlmostEqual(out.value()*N,i+1,0)
        out.tick()
        self.assertAlmostEqual(out.value()*N,N,0)
    
    
if __name__ == '__main__':
    unittest.main()     
    
  
