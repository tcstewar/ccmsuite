import unittest

from ccm.lib import nef
import numpy

class TestNEF(unittest.TestCase):

    def test_linear_weights(self):
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


        for w in [-1,-10,0,0.5,0.2]:
            n1=nef.ScalarNode(noise=0)
            n2=nef.ScalarNode(noise=0)
            n1.connect(n2,weight=w)
            n1.set(0.3)
            n1.tick()
            n1.tick()
            self.assertEqual(n2.value(),0.3*w)
            n1.set(-0.7)
            n1.tick()
            n1.tick()
            self.assertEqual(n2.value(),-0.7*w)
            

    def test_linear_weights_n(self):
        n1=nef.ScalarNode()
        n1.configure(neurons=200,activation_noise=0.01)
        n2=nef.ScalarNode()
        n1.configure(neurons=200,activation_noise=0.01)
        n1.connect(n2)
        n1.set(0.3)
        n1.tick()
        n1.tick()
        self.assertAlmostEqual(n2.value(),0.3,1)
        n1.set(-0.7)
        n1.tick()
        n1.tick()
        self.assertAlmostEqual(n2.value(),-0.7,1)

    
if __name__ == '__main__':
    unittest.main()     
    
  
