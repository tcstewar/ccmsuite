import unittest

import ccm
from ccm.lib.actr import *


class Basic(ACTR):
    buffer1=Buffer()
    def init():
        buffer1.set('hello world')
        
    def bye(buffer1='hello world'):
        buffer1.set('goodbye world')
        
    def quit(buffer1='goodbye world'):
        self.stop()

class Vars(ACTR):
    buffer1=Buffer()
    def init():
        buffer1.set('hello world')
        
    def bye(buffer1='hello ?text'):
        buffer1.set('goodbye ?text')
        
    def quit(buffer1='goodbye ?'):
        self.stop()


class TestACTRProduction(unittest.TestCase):
    def test_basic(self):
        p=Basic()
#        ccm.log_everything(p)
        p.run()
        self.assertEqual(p.buffer1[0],'goodbye')
        self.assertEqual(p.now(),0.1)
            
    def test_vars(self):
        p=Vars()
#        ccm.log_everything(p)
        p.run()
        self.assertEqual(p.buffer1[0],'goodbye')
        self.assertEqual(p.now(),0.1)
    
    def test_chunk_setting(self):
        from ccm.lib.actr.buffer import Chunk
        c=Chunk(dict(a=1,b=2))
        self.assertEqual(c['a'],1)
        self.assertEqual(c['b'],2)
      
    
    


if __name__ == '__main__':
  unittest.main()     
