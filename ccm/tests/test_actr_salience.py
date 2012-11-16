import unittest

import ccm
from ccm.lib.actr import *


class Basic(ACTR):
    goal=Buffer()
    retrieval=Buffer()
    memory=Memory(retrieval)
    salience=DMSalience(memory)
    
    def init():
        goal.set('test')
        memory.add('id:1 color:blue shape:X')
        memory.add('id:2 color:blue shape:X')
        memory.add('id:3 color:blue shape:X')
        memory.add('id:4 color:blue shape:X')
        memory.add('id:5 color:blue shape:O')
        memory.add('id:6 color:red shape:X')
        salience.context('')
        
    def test(goal='test'):
        memory.request('')
        goal.set('test2')
    
    def test2(goal='test2',retrieval='id:?id color:?color shape:?shape'):
        goal.set('id:?id color:?color shape:?shape')
        self.stop()



class TestACTRMemory(unittest.TestCase):
    def test_basic(self):
        p=Basic()
        p.salience.weights(color=1)
        p.run()
        self.assertEqual(p.goal['id'],'6')
            
        p=Basic()
        p.salience.weights(shape=1)
        p.run()
        self.assertEqual(p.goal['id'],'5')


if __name__ == '__main__':
  unittest.main()     
