import unittest

import ccm


class ProdTest(ccm.ProductionSystem):
  x=1
  def test(self='x:1'):
      self.x=2

class Prod(ccm.ProductionSystem):
  class Module1(ccm.Model):
     a=1
     def set(self,value):
         self.a=value
  class Module2(ccm.Model):
     b=2
     def set(self,value):
         self.b=value
  state='swap'
  def swap(self='state:swap',Module1='a:?a',Module2='b:?b'):
      Module1.set(b)
      Module2.set(a)
      self.state=None



class TestProduction(unittest.TestCase):
  def test_self(self):
    p=ProdTest()
    p.run()
    self.assertEqual(p.x,2)
    

  def test_multi(self):
      p=Prod()
      p.run()
      self.assertEqual(p.Module1.a,'2')
      self.assertEqual(p.Module2.b,'1')
  
    
    
    
    


if __name__ == '__main__':
  unittest.main()     
