import unittest

from ccm.lib import nef
import numpy

class TestNEF(unittest.TestCase):

    def test_connection(self):
        n1=nef.ScalarNode(noise=0)
        n2=nef.ScalarNode(noise=0)
        n1.connect(n2)
        n1.set(0.3)
        n1.tick()
        n1.tick()
        self.assertEqual(n2.value(),0.3)
        n1.set(-0.7)
        n1.tick()
        n1.tick()
        self.assertEqual(n2.value(),-0.7)

        n1=nef.VectorNode(2,noise=0)
        n2=nef.VectorNode(2,noise=0)
        n1.connect(n2,weight=0.1)
        n1.set([0.3,-0.7])
        n1.tick()
        n1.tick()
        self.assertAlmostEqual(n2.value()[0],0.03)
        self.assertAlmostEqual(n2.value()[1],-0.07)

        n1=nef.VectorNode(2,noise=0)
        n2=nef.VectorNode(2,noise=0)
        n1.connect(n2,weight=numpy.array([[0,1],[1,0]]))
        n1.set([0.3,-0.7])
        n1.tick()
        n1.tick()
        self.assertEqual(n2.value()[0],-0.7)
        self.assertEqual(n2.value()[1],0.3)
        

    def test_collection(self):
        n=nef.CollectionNode(nef.ScalarNode(),nef.VectorNode(3),nef.ScalarNode(),noise=0)
        v1=[0.3,[0.2,0.1,-0.5],-1.0]
        n.set(v1)
        n.tick()
        v2=n.value()
        self.assertEqual(v1[0],v2[0])
        self.assertEqual(v1[1][0],v2[1][0])
        self.assertEqual(v1[1][1],v2[1][1])
        self.assertEqual(v1[1][2],v2[1][2])
        self.assertEqual(v1[2],v2[2])
    
if __name__ == '__main__':
    unittest.main()     
    
  
