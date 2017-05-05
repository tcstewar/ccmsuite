import unittest

from ccm.lib import nef
import numpy

class TestNEF(unittest.TestCase):

    def test_highdim(self):
        D=50
        N=100
        n1=nef.VectorNode(D)
        n1.configure(neurons=N,code='n1',use_hd=True,apply_noise=False)

        n2=nef.VectorNode(D)
        n2.configure(neurons=N,code='n2',use_hd=False,apply_noise=False)


        for x in [[0,0,0],[0,0,1],[0.5,0.5,0.5]]:
            if len(x)<D:
                x.extend([0.0]*(D-len(x)))
            print(x)
            n1.set(x)
            n1.tick()
            print(1,n1.value())

            n2.set(x)
            n2.tick()
            print(2,n2.value())


            #self.assertAlmostEqual(n1.value()[0],n2.value()[0],1)
            #self.assertAlmostEqual(n1.value()[1],n2.value()[1],1)
            #self.assertAlmostEqual(n1.value()[2],n2.value()[2],1)






if __name__ == '__main__':
    unittest.main()


