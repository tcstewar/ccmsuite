import numpy
from ccm.lib.nef.activity import ActivityNode
from ccm.lib.nef.core import ArrayNode
from numpy import dot


class SpikingNode(ActivityNode):
    _set_current=None
    
    def configure_spikes(self,dt=0.001,pstc=0.02,current_noise=None):
        self.dt=dt
        self.pstc=pstc
        if pstc is not None:
            for conn in self.outputs: 
                if conn.tau is None or conn.tau==0:
                    conn.tau=pstc
        self.voltage=numpy.zeros(self.neurons)
        self.spikes=numpy.zeros(self.neurons)
        self.refractory_time=numpy.zeros(self.neurons)
        self.Jm_prev=None
        self.mode='spike'
        self.current_noise=current_noise


    def set(self,value,calc_output=True):
        ActivityNode.set(self,value,calc_output=False)
        if self.mode=='spike':
            if value is None:
                self._set_current=None            
            else:    
                c=self.array_to_current(self._set_array)+self.Jbias
                self._set_current=c
        if calc_output: self._calc_output()


    def _calc_output(self):
        if self.mode!='spike': return ActivityNode._calc_output(self)
        if self._set_current is not None:
            curr=self._set_current
        else:
            curr=self.array_to_current(self.accumulator.value())+self.Jbias    
            
            
        if self.current_noise is not None:
            curr=self.add_current_noise(curr)
        self._output=self.calc_spikes(curr)
  

    def array(self):
        if self._array is None:
            if self.mode!='spike': return ActivityNode.array(self)
            self._array=self.activity_to_array(self._output/self.dt)
        return self._array




    def _transmit_spike_direct(self,conn,dt):
        x=self.activity_to_array(self._output,decoder=self.get_decoder(conn.func))/dt
        conn.pop2.accumulator.add(conn.apply_weight(x),conn.tau,dt)
    def _transmit_spike_spike(self,conn,dt):
        if self._output is not None:
            x=self.activity_to_array(self._output,decoder=self.get_decoder(conn.func))/dt
        else:            
            x=self.activity_to_array(None,decoder=self.get_decoder(conn.func))
        conn.pop2.accumulator.add(conn.apply_weight(x),conn.tau,dt)
        
    def _transmit_direct_spike(self,conn,dt):
        conn.pop2.accumulator.add(conn.apply_func_weight(self._output),conn.tau,dt)

    

    def add_current_noise(self,curr):
        noise=self.current_noise
        if noise>0:
            curr=numpy.random.normal(curr,noise)
            #curr=numpy.maximum(0,curr)            
        return curr

    
    def calc_spikes(self,current):
        Jm=current
        dt=self.dt
        if self.Jm_prev is None: self.Jm_prev=Jm
        v=self.voltage

        # Euler's method
        dV=dt/self.t_rc*(self.Jm_prev-v)

        self.Jm_prev=Jm
        v+=dV
        v=numpy.maximum(v,0)


        # do accurate timing for when the refractory period ends
        self.refractory_time-=dt
        post_ref=1.0-self.refractory_time/dt  
        v=numpy.where(post_ref>=1,v,v*post_ref) # scale by amount of time outside of refractory period
        v=numpy.where(post_ref<=0,0,v)  # set to zero during refactory period
        
        self.spikes[:]=0
        V_threshold=self.J_threshold
        for i in numpy.where(v>V_threshold):
            overshoot=(v[i]-V_threshold)/dV[i]
            spiketime=dt*(1.0-overshoot)
            self.refractory_time[i]=spiketime+self.t_ref
            self.spikes[i]=1
            v[i]=0
        self.voltage=v
        
        return self.spikes    
