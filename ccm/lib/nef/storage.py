import os
import numpy
import random

base_path='nef_data'

class Storage:
    def __init__(self,node,seed=None,code=None,force_new=False):
        self.node=node
        self.code=code
        if seed is None and not force_new:
            seed=self.find_seed()
        if seed is None:
            try:
                seed=int(random.getrandbits(31))
            except AttributeError:   # for py2.3
                seed=random.randint(0,0x7fffffff)
        self.seed=seed
        if not os.access(self.path(),os.F_OK):
            os.makedirs(self.path())
        

    def path(self,key=None):
        p=base_path
        if self.code:
            p=os.path.join(p,self.code)
        p=os.path.join(p,self.make_identifier())
        if key:
            p=os.path.join(p,key)
        return p
      
    def set(self,key,array):
        f=file(self.path(key),'wb')
        f.write(array)
        f.close()
        
    def get(self,key,shape):
        try:
            array=numpy.fromfile(self.path(key),dtype='float32')
        except IOError,e:
            return None
        try:
            if shape[1]==-1:
                assert array.size%shape[0]==0
                shape=shape[0],array.size/shape[0]
        except TypeError:
            pass
        array.shape=shape
        return array

    def find_seed(self):
        ident=self.make_identifier(with_seed=False)+'~'
        p=base_path
        if self.code: p=os.path.join(p,self.code)
        if os.access(p,os.F_OK):
            for f in os.listdir(p):
                if f.startswith(ident):
                    seed=int(f[len(ident):],16)
                    return seed

    def make_identifier(self,with_seed=True):
        node=self.node
        ident='%d_%d'%(node.neurons,node.dimensions)
        if not node.lif: ident+='L'

        for s,p,v,r in identifier_info:
            val=getattr(node,p)
            if val!=v:
                if isinstance(val,(tuple,list)):
                    val='&'.join(['%s'%vv for vv in val])
                ident+='_%s=%s'%(s,r%val)
        if node.dimensions<10:        
            if node.sample_count!=node.dimensions*500:
                ident+='_sc=%d'%node.sample_count
        else:        
            if node.sample_count!=5000:
                ident+='_sc=%d'%node.sample_count
        if node.data_basis!=None:
            ident+='_basis=%08x'%hash(tuple(tuple(x) for x in node.data_basis))
        if node.data_thresholds!=None:
            ident+='_threshs=%08x'%hash(tuple(node.data_thresholds))
        if node.data_saturations!=None:
            ident+='_sats=%08x'%hash(tuple(node.data_saturations))

        if with_seed:
            ident+='~%08x'%self.seed

        return ident

    
identifier_info=[        
  ('sat','saturation_range',(200,300),'(%s)'),
  ('trf','t_ref',0.001,'%5.3f'),
  ('trc','t_rc',0.01,'%5.3f'),
  ('Jth','J_threshold',1,'%5.3f'),
  ('n','activation_noise',0.1,'%5.3f'),
  ('b','basis_style','Sphere','%s'),
  ('s','sample_style','DefaultSampling','%s'),
  ('min','min',-1.0,'%4.3f'),
  ('max','max',1.0,'%4.3f'),
  ('tc','threshold_coverage',0.9,'%4.3f'),
  ('tmin','threshold_min',None,'%4.3f'),
  ('tmax','threshold_max',None,'%4.3f'),
  ('hd','use_hd',False,'%d'),
    ]
        
