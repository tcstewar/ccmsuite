import unittest

import ccm
from ccm.lib.actr import *


class Basic(ACTR):
    goal=Buffer()
    retrieval=Buffer()
    memory=Memory(retrieval)
    
    def init():
        goal.set('test')
        memory.add('hello world')
        
    def test(goal='test'):
        memory.request('hello ?')
        goal.set('test2')
    
    def test2(goal='test2',retrieval='hello ?x'):
        goal.set('?x')    
        self.stop()


class TwoWords(ACTR):
    goal=Buffer()
    retrieval=Buffer()
    memory=Memory(retrieval)
    
    def init():
        goal.set('test')
        memory.add('hello world')
        memory.add('bye world')
        
    def test(goal='test'):
        memory.request('? ?')
        goal.set('test2')
    
    def test2(goal='test2',retrieval='?a ?x'):
        goal.set('?x')    
        self.stop()
        

class TestACTRMemory(unittest.TestCase):
    def test_basic(self):
        p=Basic()
        #ccm.log_everything(p)
        p.run()
        self.assertEqual(p.goal[0],'world')
        self.assertAlmostEqual(p.now(),0.15)
            
    def test_two(self):
        p=TwoWords()
        #ccm.log_everything(p)
        p.run()
        self.assertEqual(p.goal[0],'world')
        self.assertAlmostEqual(p.now(),0.15)
        
    def test_lambda(self):
        class LambdaTest(ACTR):
            focal=Buffer()
            retrieval=Buffer()
            memory=Memory(retrieval)
            def init():
                focal.set('test')
                memory.add('x:30 y:50 text:A')
                memory.add('x:80 y:50 text:B')
            def test(focal='test'):
                memory.request(['y:50',lambda obj,b:int(obj['x'])<50])
                focal.set('test2')
            def test2(focal='test2',retrieval='text:?text'):
                focal.set('?text')
                self.stop()
        p=LambdaTest()
        p.run()
        self.assertEqual(p.focal.chunk[0],'A')


if __name__ == '__main__':
  unittest.main()     
