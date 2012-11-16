import unittest

from ccm.lib.actr import *

class MyModel(ACTR):
  focus=Buffer()
  retrieve=Buffer()
  dm=Memory(retrieve)
  pgc=PMPGC()
  compiler=PMCompile(keep='focus',request='dm.request',retrieve='retrieve')
  
  def init():
    dm.add('pattern a 7')
    dm.add('pattern b 3')
 
  def prod1(focus='see ?x'):
    dm.request('pattern ?x ?')
    focus.set('remember ?x')
 
  def prod2(focus='remember ?x',retrieve='pattern ?x ?y'):
    focus.set('say ?y')
    self.success()
    self.stop()
    
    
class TestScheduler(unittest.TestCase):
  def setUp(self):
    pass

  def test_compile(self):
        m=MyModel()

        m.focus.set('see a')
        m.run()
        self.assertEqual(str(m.focus.chunk),'say 7')
        self.assertAlmostEqual(m.now(),0.15)
    
        m.focus.set('see a')
        m.run()
        self.assertEqual(str(m.focus.chunk),'say 7')
        self.assertAlmostEqual(m.now(),0.20)

        m.focus.set('see b')
        m.run()
        self.assertEqual(str(m.focus.chunk),'say 3')
        self.assertAlmostEqual(m.now(),0.35)
    
        m.focus.set('see b')
        m.run()
        self.assertEqual(str(m.focus.chunk),'say 3')
        self.assertAlmostEqual(m.now(),0.40)

    
if __name__ == '__main__':
  unittest.main()     
