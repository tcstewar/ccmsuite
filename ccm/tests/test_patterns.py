import unittest

from ccm.pattern import Pattern,PatternException

class Obj:
  def __init__(self,**keys):
    for k,v in keys.items():
      self.__dict__[k]=v
      
      
def makePattern(text):
  return Pattern(dict(self=text))
      

class TestPattern(unittest.TestCase):
  def test_exact(self):
    obj={'self':Obj(a=1,b=2,c=3)}
    p=Pattern(dict(self='a:1 b:2 c:3'))
    self.assertEqual(p.match(obj),{})
    obj['self'].c=2
    self.assertEqual(p.match(obj),None)
    self.assertEqual(Pattern(dict(self='a:1 a:2')).match(obj),None)
    self.assertEqual(p.match({'self':None}),None)
    self.assertEqual(Pattern(dict(self=None)).match({'self':None}),{})
    
    
  def test_notexact(self):
    obj={'self':Obj(a=1,b=2,c=3)}
    p=makePattern('a:!2 b:2')
    self.assertEqual(p.match(obj),{})
    obj['self'].a=2
    self.assertEqual(p.match(obj),None)
    
  def test_vars(self):
    obj={'self':Obj(a=1,b=2,c=1)}
    
    self.assertEqual(makePattern('a:?x').match(obj),{'x':'1'})
    self.assertEqual(makePattern('a:?x c:?x').match(obj),{'x':'1'})
    self.assertEqual(makePattern('a:?x b:?x').match(obj),None)
    self.assertEqual(makePattern('a:?x b:?y').match(obj),{'x':'1','y':'2'})
    self.assertEqual(makePattern('a:?x b:!?x').match(obj),{'x':'1'})
    self.assertEqual(makePattern('a:?x c:!?x').match(obj),None)
    
  def test_unnamed_slot(self):
    obj={'self':[1,2,1]}

    self.assertEqual(makePattern('?x').match(obj),{'x':'1'})
    self.assertEqual(makePattern('?x ? ?x').match(obj),{'x':'1'})
    self.assertEqual(makePattern('?x ?x').match(obj),None)
    self.assertEqual(makePattern('?x ?y').match(obj),{'x':'1','y':'2'})
    self.assertEqual(makePattern('?x !?x').match(obj),{'x':'1'})
    self.assertEqual(makePattern('?x ? !?x').match(obj),None)
        
    self.assertEqual(makePattern('?x 1:?y').match(obj),{'x':'1','y':'2'})
    self.assertEqual(makePattern('?x 2:?x').match(obj),{'x':'1'})
    self.assertRaises(PatternException,makePattern,('a:1 2'))
  
    
  def test_str(self):
    obj={'self':dict(a=True,b=False,c=None)}
    
    self.assertEqual(makePattern('a:True').match(obj),{})
    self.assertEqual(makePattern('b:False').match(obj),{})
    self.assertEqual(makePattern('c:None').match(obj),{})
    
    self.assertEqual(makePattern('a:False').match(obj),None)
    self.assertEqual(makePattern('b:None').match(obj),None)
    self.assertEqual(makePattern('c:False').match(obj),None)
    
  def test_group(self):
    obj={'a':dict(a=1,b=None),'c':dict(d=2,e=1)}
    
    self.assertEqual(Pattern(dict(c='d:2 e:1')).match(obj),{})
    self.assertEqual(Pattern(dict(a='a:?x',c='d:2 e:?x')).match(obj),{'x':'1'})
    self.assertEqual(Pattern(dict(a='b:!?x',c='d:!?x e:?x')).match(obj),{'x':'1'})
    self.assertEqual(Pattern(dict(a='a:!?x b:!?x',c='d:!?x e:?x')).match(obj),None)
  
  def test_lambda(self):
    obj={'self':Obj(a=1,b=2,c=1)}

    self.assertEqual(makePattern(lambda x,b: x.a+x.b+x.c==4).match(obj),{})
    self.assertEqual(makePattern(lambda x,b: x.a+x.b+x.c==3).match(obj),None)      
    self.assertEqual(makePattern(['a:?z',lambda x,b: x.a+x.b+x.c-int(b['z'])==3]).match(obj),{'z':'1'})
    self.assertEqual(makePattern(['a:?z',lambda x,b: x.a+x.b+x.c+int(b['z'])==3]).match(obj),None)
    
if __name__ == '__main__':
  unittest.main()     
    
  