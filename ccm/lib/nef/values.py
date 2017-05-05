from ccm.lib.nef.activity import ActivityNode
from ccm.lib.nef.spikes import SpikingNode
from ccm.lib.nef.core import ArrayNode
import numpy

Node=SpikingNode
#Node=ActivityNode
#Node=ArrayNode

from ccm.lib.hrr import HRR
class HRRNode(Node):
    def __init__(self,size,min=None,max=None,**keys):
        if min is None: min=-numpy.sqrt(1.0/size)
        if max is None: max=numpy.sqrt(1.0/size)
        Node.__init__(self,size,min=min,max=max,**keys)
    def value_to_array(self,value):
        if isinstance(value,int): return [value]
        return value.v
    def array_to_value(self,array):
        return HRR(data=array)


class ScalarNode(Node):
    def __init__(self,**keys):
        Node.__init__(self,1,**keys)
    def value_to_array(self,value):
        if not isinstance(value,(float,int)):
            raise Exception('Invalid value for scalar node: %s'%value)
        return numpy.array([value],dtype=numpy.float)
    def array_to_value(self,array):
        if len(array.shape)==0: return array
        else: return array[0]


class VectorNode(Node):
    def value_to_array(self,value):
        return numpy.array(value,dtype=numpy.float)
    def array_to_value(self,array):
        return array


class CollectionNode(Node):
    def __init__(self,*components,**keys):
        Node.__init__(self,sum([c.dimensions for c in components]),**keys)
        self.components=components
    def value_to_array(self,value):
        assert isinstance(value,(list,tuple))
        arrays=[c.value_to_array(value[i]) for i,c in enumerate(self.components)]
        return numpy.concatenate(arrays)
    def array_to_value(self,array):
        v=[]
        print(v)
        i=0
        for c in self.components:
            v.append(c.array_to_value(array[i:i+c.dimensions]))
            i+=c.dimensions
        print(v)
        return v


