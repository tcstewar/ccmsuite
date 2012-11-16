import numpy


array_class=numpy.array(0).__class__

class Connection:
    def __init__(self,pop1,pop2,func=None,weight=None,tau=None):
        if pop1._all_nodes is not None:
            for n in pop1._all_nodes:
                n._all_nodes=None
        if pop2._all_nodes is not None:
            for n in pop2._all_nodes:
                n._all_nodes=None

        if tau is None:
            tau=getattr(pop1,'pstc',None)
            if tau is None: tau=0
        self.tau=tau

        self.pop1=pop1
        pop1.outputs.append(self)
        self.pop2=pop2
        pop2.inputs.append(self)
        self.func=func

        if weight is None or isinstance(weight,(float,int)):
            self.weight=weight
            self.weight_is_matrix=False
        else:
            self.weight_is_matrix=True
            if not hasattr(weight,'shape'): weight=numpy.array(weight)
            if len(weight.shape)==1: weight.shape=weight.shape[0],1
            self.weight=weight
        
        
        
    def type(self):
        return '%s_%s'%(self.pop1.mode,self.pop2.mode)


    def apply_weight(self,x):
        if self.weight is not None:
            if self.weight_is_matrix:
                x=numpy.dot(self.weight,x)
            else:
                x=x*self.weight
        return x
    
    def apply_func(self,x):
        if x is None: x=numpy.zeros(self.pop1.dimensions)
        if self.func is not None:
            v=self.pop1.array_to_value(x)
            v=self.func(v)
            if not isinstance(v,array_class):
                x=self.pop2.value_to_array(v)
            else:
                x=v
        return x
        
    def apply_func_weight(self,x):
        x=self.apply_func(x)
        x=self.apply_weight(x)
        return x



        
def connect(x,y,func=None,weight=None,tau=None):
    if func is not None and not callable(func):
        print func
        raise Exception('connection function is invalid')
    return Connection(x,y,func=func,weight=weight,tau=tau)
