import numpy
from ccm.lib.nef.core import ArrayNode
from ccm.lib.nef.generate import makeGenerator
from ccm.lib.nef.storage import Storage
from ccm.lib.nef.highdimension import calc_gamma_moments

svd_limit=1e-15

class ActivityNode(ArrayNode):
    _set_activity=None
    decoder_size_warning=1000
    sample_step_size=500
    decoder_mode='NxN'
    decoder_noise_use_gamma=False
    decoder_noise_use_limit=False
    decoder_noise_use_activity=False


    lesion_size=0
    lesion_cells=None

    def configure(self,neurons,lif=True,saturation_range=(200,300),
                  t_ref=0.001,t_rc=0.01,J_threshold=1,activation_noise=0.1,apply_noise=False,
                  threshold_coverage=0.9,threshold_min=None,threshold_max=None,
                  basis_style='Sphere',sample_style='DefaultSampling',
                  sample_count=None,seed=None,code=None,force_new=False,use_hd=False,
                  basis=None,thresholds=None,saturations=None,alphas=None,Jbiases=None):
        self.neurons=neurons
        self.lif=lif
        self.saturation_range=saturation_range
        self.t_ref=t_ref
        self.t_rc=t_rc
        self.J_threshold=J_threshold
        self.basis_style=basis_style
        self.sample_style=sample_style
        self.threshold_coverage=threshold_coverage
        self.threshold_min=threshold_min
        self.threshold_max=threshold_max
        if sample_count is None:
            sample_count=self.dimensions*500
            if sample_count>5000: sample_count=5000
        self.sample_count=sample_count
        self.activation_noise=activation_noise
        self.apply_noise=apply_noise
        self.decoders={}
        self.use_hd=use_hd
        self.data_basis=basis
        self.data_thresholds=thresholds
        self.data_saturations=saturations
        self.data_alphas=alphas
        self.data_Jbiases=Jbiases

        self.storage=Storage(self,seed=seed,code=code,force_new=force_new)
        self.seed=self.storage.seed
        self.initialize_node()

        self.mode='rate'

        if self.sample_count<self.neurons:
            self.decoder_mode='NxS'
            self.decoder_noise_use_limit=True
        else:
            self.decoder_mode='NxN'
            self.decoder_noise_use_gamma=True



    def set(self,value,calc_output=True):
        ArrayNode.set(self,value,calc_output=False)
        if self.mode=='rate':
            if value is None:
                self._set_activity=None
            else:
                c=self.array_to_current(self._set_array)+self.Jbias
                self._set_activity=self.current_to_activity(c)
        if calc_output: self._calc_output()


    def array(self):
        if self._array is None:
            if self.mode!='rate': return ArrayNode.array(self)
            self._array=self.activity_to_array(self._output)
        return self._array

    def _calc_output(self):
        if self.mode!='rate': return ArrayNode._calc_output(self)
        if self._set_activity is not None:
            out=self._set_activity
        else:
            out=self.current_to_activity(self.array_to_current(self.accumulator.value())+self.Jbias)
        if self.apply_noise:
            out=self.add_activation_noise(out)
        self._output=out

    def _transmit_rate_direct(self,conn,dt):
        x=self.activity_to_array(self._output,decoder=self.get_decoder(conn.func))
        conn.pop2.accumulator.add(conn.apply_weight(x),conn.tau,dt)
    def _transmit_rate_rate(self,conn,dt):
        x=self.activity_to_array(self._output,decoder=self.get_decoder(conn.func))
        conn.pop2.accumulator.add(conn.apply_weight(x),conn.tau,dt)
    def _transmit_direct_rate(self,conn,dt):
        conn.pop2.accumulator.add(conn.apply_func_weight(self._output),conn.tau,dt)


    def initialize_node(self):
        random=numpy.random.RandomState(seed=self.seed)

        if self.data_alphas is not None and self.data_Jbiases is not None:
            self.alpha=numpy.array([self.data_alphas[i%len(self.data_alphas)] for i in range(self.neurons)],dtype=numpy.dtype('float32'))
            self.Jbias=numpy.array([self.data_Jbiases[i%len(self.data_Jbiases)] for i in range(self.neurons)],dtype=numpy.dtype('float32'))
        else:
            if self.data_saturations is None:
                sr=self.saturation_range
                sat=random.uniform(sr[0],sr[1],(self.neurons,1))
            else:
                N=len(self.data_saturations)
                sat=numpy.array([[self.data_saturations[i%N] for i in range(self.neurons)]],dtype=numpy.dtype('float32')).T

            if self.data_thresholds is None:
                delta=(self.max-self.min)*(1-self.threshold_coverage)*0.5
                min_thresh=self.min+delta
                max_thresh=self.max-delta
                if self.threshold_min is not None: min_thresh=self.threshold_min
                if self.threshold_max is not None: max_thresh=self.threshold_max

                thresh=random.uniform(min_thresh,max_thresh,(self.neurons,1))
            else:
                N=len(self.data_thresholds)
                thresh=numpy.array([[self.data_thresholds[i%N] for i in range(self.neurons)]],dtype=numpy.dtype('float32')).T

            self.initialize_neurons(sat,thresh)

        if self.data_basis is None:
            g=makeGenerator(self.basis_style,self.dimensions,int(random.randint(0x7FFFFFFF)))
            self.basis=g.get(self.neurons).T
        else:
            N=len(self.data_basis)
            self.basis=numpy.array([self.data_basis[i%N] for i in range(self.neurons)],dtype=numpy.dtype('float32'))
            if len(self.basis.shape)==1:
                self.basis.shape=(self.neurons,self.dimensions)

        self.sample_generator=makeGenerator(self.sample_style,self.dimensions,int(random.randint(0x7FFFFFFF)))
        if self.min!=-1 or self.max!=1:
            scale=(self.max-self.min)/2.0
            if scale!=1.0: self.sample_generator.scale=scale
            offset=(self.max+self.min)/2.0
            if scale!=0.0: self.sample_generator.offset=offset





    def initialize_neurons(self,saturations,thresholds):
        saturations=numpy.array(saturations,dtype=numpy.float32)
        thresholds=numpy.array(thresholds,dtype=numpy.float32)
        x1,y1=thresholds,numpy.zeros((self.neurons,1),dtype=numpy.float32)
        x2,y2=self.max,saturations
        if not self.lif:
            m=(y1-y2)/(x1-x2)
            b=y1-m*x1
        else:
            numpy.seterr(divide='ignore')
            z1=numpy.where(y1<=0,1.0,1.0/(1-numpy.exp((self.t_ref-(1.0/y1))/self.t_rc)))
            z2=numpy.where(y2<=0,1.0,1.0/(1-numpy.exp((self.t_ref-(1.0/y2))/self.t_rc)))
            numpy.seterr(divide='warn')
            m=(z1-z2)/(x1-x2)
            b=z1-m*x1
        self.alpha,self.Jbias=m,b
        self.Jbias.shape=self.Jbias.shape[0]
        self.alpha.shape=self.alpha.shape[0]

    def current_to_activity(self,J):
        if not self.lif:
            return numpy.maximum(J,0)
        else:
            J=numpy.maximum(J,0)
            numpy.seterr(invalid='ignore',divide='ignore')
            G=self.t_ref-self.t_rc*numpy.log(1-self.J_threshold/J)
            G=numpy.where(G>0.001,1/G,0)
            numpy.seterr(invalid='warn',divide='warn')
            return G


    def array_to_current(self,array):
        b=self.basis
        phi_x=numpy.dot(b,array)
        J=self.alpha*phi_x
        return J

    def arrays_to_currents(self,arrays):
        b=self.basis
        phi_x=numpy.dot(b,arrays)
        J=self.alpha*phi_x.T
        return J.T


    def activity_to_array(self,activity,decoder=None):
        if activity is None: activity=numpy.zeros(self.neurons)
        if self.lesion_size>0:
            activity=activity[:]
            activity[:self.lesion_size]=0.0
        if self.lesion_cells is not None:
            activity[self.lesion_cells]=0.0
        if decoder is None:
            decoder=self.get_decoder()
        array=numpy.dot(activity.T,decoder)
        return array

    def add_activation_noise(self,actv,noise=None):
        if noise is None: noise=self.activation_noise
        if noise>0:
            actv=numpy.random.normal(actv,self.saturation_range[1]*noise)
            actv=numpy.maximum(0,actv)
        return actv



    def get_decoder(self,func=None,noise=None):
        if self.decoder_mode=='NxN':
            decoder=self.get_decoder_NxN
        elif self.decoder_mode=='NxS':
            decoder=self.get_decoder_NxS
        else:
            raise Exception('Unknown decoder mode: %s'%self.decoder_mode)
        return decoder(func=func,noise=noise)



    def get_decoder_NxN(self,func=None,noise=None):
        if noise is None: noise=self.activation_noise

        name='decoderNxN'
        name_gamma='gamma'
        name_gammainv='gammainv'
        name_upsilon='upsilon'
        if func:
            hash_info=make_hash_info(func)
            n='-%s-%08x'%(func.__name__,hash(tuple(hash_info)))#hash(tuple(func_id)))
            n=n.replace('<','_').replace('>','_')
            name_upsilon+=n
            name+=n
        name+='-%4.2f'%noise
        name_gammainv+='-%4.2f'%noise
        if noise>0:
            if self.decoder_noise_use_gamma:
                name+='g'
                name_gammainv+='g'
            if self.decoder_noise_use_limit:
                name+='l'
                name_gammainv+='l'
            if self.decoder_noise_use_activity:
                name+='a'
                name_gammainv+='a'
                name_upsilon+='-%4.2fa'%noise
                name_gamma+='-%4.2fa'%noise


        if name in self.decoders: return self.decoders[name]
        decoder=self.storage.get(name,(self.neurons,-1))
        if decoder is not None:
            self.decoders[name]=decoder
            return decoder


        warning=False
        if self.neurons>self.decoder_size_warning:
            warning=True
            print('Warning: calculating decoder for size %d neural group.  This may take a while.'%self.neurons)


        upsilon=None
        upsilon=self.storage.get(name_upsilon,(self.neurons,-1))

        need_gammainv=False
        need_gamma=False
        gamma_inv=self.storage.get(name_gammainv,(self.neurons,self.neurons))
        if gamma_inv is None:
            need_gammainv=True
            gamma=self.storage.get(name_gamma,(self.neurons,self.neurons))
            if gamma is None: need_gamma=True

        if need_gamma or upsilon is None:
          if self.dimensions>=3 and self.use_hd:
            gamma,moments=calc_gamma_moments(self,dr=0.01)
            gamma*=self.sample_count
            ups=self.basis*moments[1].reshape((moments[1].shape[0],1))*self.sample_count

          else:

            self.sample_generator.reset()
            count=self.sample_count
            ups=None
            while count>0:
                s=min(count,self.sample_step_size)
                if not self.sample_generator.can_continue(self.dimensions):
                    s=count
                if warning:
                    print('processing %d of %d samples (%d left)'%(s,self.sample_count,count))
                samples=self.sample_generator.get(s)
                count-=s

                curr=self.arrays_to_currents(samples)
                curr=curr.T+self.Jbias
                actv=self.current_to_activity(curr.T)
                if self.decoder_noise_use_activity:
                    actv=numpy.random.normal(actv,noise*self.saturation_range[1])
                    actv=numpy.maximum(0,actv)
                    actv=numpy.array(actv,dtype=numpy.float32)

                if need_gamma:
                    g=numpy.dot(actv,actv.T)
                    if gamma is None: gamma=g
                    else: gamma+=g

                if upsilon is None:
                    samples=samples.T
                    if func is not None:
                        if self.dimensions==1:
                            samples=samples[:,0]
                        samples=numpy.array([self.value_to_array(func(self.array_to_value(x))) for x in samples],dtype=numpy.float32)
                    u=numpy.dot(actv,samples)
                    if ups is None: ups=u
                    else: ups+=u
          if need_gamma:
                self.storage.set(name_gamma,gamma)
          if upsilon is None:
                upsilon=ups
                self.storage.set(name_upsilon,upsilon)

        error_flag=False
        if need_gammainv:
            if self.decoder_noise_use_gamma:
                if noise>0:
                    gamma+=numpy.identity(gamma.shape[0])*(((noise*self.saturation_range[1])**2)*self.sample_count)

            if warning:
                print('inverting %dx%d gamma matrix'%gamma.shape)

            w,v=numpy.linalg.eigh(gamma)
            limit=svd_limit*max(w)

            if self.decoder_noise_use_limit:
                if noise>0: limit=noise*noise*max(w)

            for i in range(len(w)):
                if w[i]<limit: w[i]=0
                else: w[i]=1.0/w[i]
            gamma_inv=numpy.dot(v,numpy.multiply(w[:,numpy.core.newaxis],v.T))
            self.storage.set(name_gammainv,gamma_inv)

        decoder=numpy.dot(gamma_inv,upsilon)
        if len(decoder.shape)==1:
            decoder.shape=decoder.shape[0],1

        self.decoders[name]=decoder
        self.storage.set(name,decoder)
        return decoder


    def get_decoder_NxS(self,func=None,noise=None):
        if noise is None: noise=self.activation_noise

        name='decoderNxS'
        name_Ainv='Ainv'
        name_B='B'
        if func:
            hash_info=make_hash_info(func)
            n='-%s-%08x'%(func.__name__,hash(tuple(hash_info)))#hash(tuple(func_id)))
            n=n.replace('<','_').replace('>','_')
            name_B+=n
            name+=n
        name+='-%4.2f'%noise
        name_Ainv+='-%4.2f'%noise
        if noise>0:
            if self.decoder_noise_use_limit:
                name+='l'
                name_Ainv+'l'
            if self.decoder_noise_use_activity:
                name+='a'
                name_Ainv+='a'
                name_B+='-%4.2fa'%noise





        if name in self.decoders: return self.decoders[name]
        decoder=self.storage.get(name,(self.neurons,-1))
        if decoder is not None:
            self.decoders[name]=decoder
            return decoder


        warning=False
        if self.neurons>self.decoder_size_warning:
            warning=True
            print('Warning: calculating decoder for size %d neural group.  This may take a while.'%self.neurons)


        B=self.storage.get(name_B,(self.sample_count,-1))
        Ainv=self.storage.get(name_Ainv,(self.sample_count,self.neurons))

        need_B=B is None
        need_A=Ainv is None

        if B is None or Ainv is None:
            self.sample_generator.reset()
            count=self.sample_count
            A=None
            while count>0:
                s=min(count,self.sample_step_size)
                if not self.sample_generator.can_continue(self.dimensions):
                    s=count
                if warning:
                    print('processing %d of %d samples (%d left)'%(s,self.sample_count,count))
                samples=self.sample_generator.get(s)
                count-=s

                curr=self.arrays_to_currents(samples)
                curr=curr.T+self.Jbias
                actv=self.current_to_activity(curr.T)
                if self.decoder_noise_use_activity:
                    actv=numpy.random.normal(actv,noise*self.saturation_range[1])
                    actv=numpy.maximum(0,actv)
                    actv=numpy.array(actv,dtype=numpy.float32)

                if need_A:
                    if A is None: A=actv
                    else:
                        A=numpy.hstack((A,actv))
                if need_B:
                    samples=samples.T
                    if func is not None:
                        if self.dimensions==1:
                            samples=samples[:,0]
                        samples=numpy.array([self.value_to_array(func(self.array_to_value(x))) for x in samples],dtype=numpy.float32)
                    if B is None: B=samples
                    else:
                        B=numpy.vstack((B,samples))
        if need_A:
            if warning:
                print('inverting %dx%d activity matrix'%A.shape)

            Ainv=numpy.linalg.pinv(A,rcond=noise*0.1)
            self.storage.set(name_Ainv,Ainv)
        if need_B:
            self.storage.set(name_B,B)



        decoder=numpy.dot(Ainv.T,B)
        if len(decoder.shape)==1:
            decoder.shape=decoder.shape[0],1

        self.decoders[name]=decoder
        self.storage.set(name,decoder)
        return decoder





def make_hash_info(obj):
    if isinstance(obj,(bool,type(None),int,float,str)):
        return [hash(obj)]

    r=[]
    if hasattr(obj,'func_code'):
        r.append(obj.__name__)
        r.append(obj.func_code)
        r.append(obj.func_code.co_names)
        for n in obj.func_code.co_names:
            if n in obj.func_globals:
                v=obj.func_globals[n]
                r.append((n,tuple(make_hash_info(v))))
                #print 'searching',n
        if hasattr(obj,'im_self'):
            r.append(('im_self',tuple(make_hash_info(obj.im_self))))
            #print 'searching im_self'
    else:
        if hasattr(obj,'__class__'):
            r.append(obj.__class__.__name__)
        elif hasattr(obj,'__name__'):
            r.append(obj.__name__)
        keys=dir(obj)
        keys.sort()
        for k in keys:
          if k[0]!='_':
            v=getattr(obj,k)
            if isinstance(v,(bool,type(None),int,float,str)):
                r.extend([k,hash(v)])
                #print 'adding',k,v
            elif isinstance(v,(tuple,list)):
                #print 'adding list',k,len(k)
                r.append((k,len(v)))
                for i in v: r.extend(make_hash_info(i))
    return r
