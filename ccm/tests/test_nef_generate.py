import unittest

from ccm.lib.nef.generate import makeGenerator
import numpy


class TestNEFSamples(unittest.TestCase):
    def test_aligned(self):
        s=makeGenerator('Aligned',5,None).get(10)
        for v in s.T:
            self.assertEqual(numpy.linalg.norm(v),1)
            self.assertEqual(numpy.max(numpy.abs(v)),1)
    
    def test_sphere(self):
        s=makeGenerator('Sphere',200,None).get(20)
        for v in s.T:
            self.assertAlmostEqual(numpy.linalg.norm(v),1,5)

    def test_ball(self):
        s=makeGenerator('Ball',100,None).get(100)
        for v in s.T:
            self.assert_(numpy.linalg.norm(v)<1)

    def test_grid(self):
        s=makeGenerator('Grid',2,None).get(121)
        vals=[-1.0,-0.8,-0.6,-0.4,-0.2,0,0.2,0.4,0.6,0.8,1.0]
        i=0
        j=0
        for v in s.T:
            x,y=v
            self.assertAlmostEqual(x,vals[i])
            self.assertAlmostEqual(y,vals[j])
            i+=1
            if i>=len(vals):
                i=0
                j+=1
            

    def test_cube(self):
        s=makeGenerator('Cube',3,None).get(1000)
        for v in s.T:
            x,y,z=v
            self.assert_(-1<x<1)
            self.assert_(-1<y<1)
            self.assert_(-1<z<1)
            
    def test_repeatability(self):
        r1=makeGenerator('Sphere',10,1)
        r2=makeGenerator('Sphere',10,2)
        s11=r1.get(10)
        s12=r1.get(10)
        r1.reset()
        s11a=r1.get(10)
        s2=r2.get(10)

        self.assertNotEqual(s11.data,s12.data)
        self.assertEqual(s11.data,s11a.data)
        self.assertNotEqual(s11.data,s2.data)
        
            
            
            
    """
    def test_ball_graphed(self):
        import pylab
        for r in [0]:#0,0.2,0.4,0.6,0.8,0.9,0.95,1]:
            s=generate(('ball',r),1000,2)
            pylab.figure()
            pylab.scatter(s[0],s[1])
            pylab.title('ratio=%f'%r)
        pylab.show()
    """
    
    """
    def test_sphere_graphed(self):
        import pylab
        for r in [0]:#0,0.2,0.4,0.6,0.8,0.9,0.95,1]:
            s=generate(('sphere',r),100,2)
            pylab.figure()
            pylab.scatter(s[0],s[1])
            pylab.title('ratio=%f'%r)
        pylab.show()
    """

    
if __name__ == '__main__':
    unittest.main()     
    
  
