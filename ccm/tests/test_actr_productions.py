import unittest

import ccm
from ccm.lib.actr import *


class Basic(ACTR):
    def init():
        self.x=1
        
    def p1(self='x:1'):
        self.x=2    


class UtilLearn(ACTR):
    x=1
    c1=0
    c2=0
    def p1(self='x:1'):
        self.success()
        self.c1+=1
    def p2(self='x:1'):
        self.failure()
        self.c2+=1


class UtilSetting(ACTR):
    x=0
    def p1(self='x:0',utility=0.3):
        self.x=1
    def p2(self='x:0',utility=0.6):
        self.x=2
    



class TestACTRProduction(unittest.TestCase):
    def test_basic(self):
        p=Basic()
#        ccm.log_everything(p)
        p.run()
        self.assertEqual(p.x,2)
    
    def test_utillearn(self):
        for Rule in PMPGC,PMNew,PMPGCSuccessWeighted,PMPGCMixedWeighted,PMQLearn,PMTD,PMNew:
          p=UtilLearn()
          p.pm=Rule()
#          ccm.log_everything(p)
          p.run(limit=1)
          self.assertTrue(p.c1 in [17,18,19])
  
    
    def test_setting_utility(self):
        p=UtilSetting()
        p.run()
        self.assertEqual(p.x,2)
    
    
    


if __name__ == '__main__':
  unittest.main()     
