from ccm.lib.actr.pm import ProceduralSubModule
from ccm.production import Production
from ccm.pattern import Pattern

class CompiledProduction(Production):
    def __init__(self,pre,post,keep,retrieve,pre_bound,post_bound):
        self.name='%s-%s-%d'%(pre.name,post.name,id(self))
        self.system=pre.system
        self.base_utility=0
        self.bound=None

        code1=[]
        for k,v in pre_bound.items():
            code1.append(' %s=%s'%(k,repr(v)))
        code1.append(' if True:  # compiled from %s'%pre.name)
        added_line = False
        for line in pre.code.splitlines():
            for k in keep:
                if line.strip().startswith(k):
                    code1.append('  '+line)
                    added_line = True
                    break
        if not added_line:
            code1.append('  pass')

        code1='\n'.join(code1)
        for k,v in pre_bound.items():
            code1=code1.replace('?'+k,v)



        code2=[]
        for k,v in post_bound.items():
            code2.append(' %s=%s'%(k,repr(v)))
        code2.append(' if True:  # compiled from %s'%post.name)
        for line in post.code.splitlines():
            if len(line.strip())>0:
                code2.append('  '+line)

        code2='\n'.join(code2)
        for k,v in post_bound.items():
            code2=code2.replace('?'+k,v)

        self.code='if True:\n%s\n%s'%(code1,code2)

        self.func=compile(self.code,'<production-%s>'%self.name,'exec')


        keys=list(pre.keys)
        patterns={}
        for buf,pat in pre.pattern_specs.items():
            for k,v in pre_bound.items():
                pat=pat.replace('?'+k,v)
            patterns[buf]=pat

        for m in post.keys:
            if m==retrieve: pass
            elif m not in keys:
                keys.append(m)
                pat=post.pattern_specs[m]
                for k,v in post_bound.items():
                    pat=pat.replace('?'+k,v)
                patterns[buf]=pat

        self.keys=keys
        self.pattern_specs=patterns
        self.pattern=Pattern(patterns)





class PMCompile(ProceduralSubModule):
    def __init__(self,keep,request,retrieve):
        if not isinstance(keep,(list,tuple)): keep=(keep,)
        self.keep=keep
        self.request=request
        self.retrieve=retrieve
        self.log=None
        self.pre=[]
        self.post=[]
        self._previous=None
        self.compiled={}
    def create(self,prod,parents=None):
        if self.retrieve in prod.keys:
            for m in prod.keys:
                if m not in self.keep and m!=self.retrieve:
                    break
            else:
                self.post.append(prod)

        code=prod.code
        good=False
        for line in code.splitlines():
            line=line.strip()
            if len(line)>0:
                keep=False
                if line.startswith(self.request):
                    good=True
                    continue
                for k in self.keep:
                    if line.startswith(k):
                        keep=True
                        break
                if keep:
                    continue
                else:
                    good=False
                    break
        if good:
            self.pre.append(prod)
    def firing(self,prod):
        if self._previous is not None and prod in self.post:
            self.compile(self._previous,self._previousBound,prod,prod.bound)
        self._previous=None
        if prod in self.pre:
            self._previous=prod
            self._previousBound=dict(prod.bound)

    def compile(self,pre,pre_bound,post,post_bound):
        id=(pre,post,tuple(sorted(pre_bound.items())),tuple(sorted(post_bound.items())))
        p=self.compiled.get(id,None)
        if p is None:
            p=CompiledProduction(pre,post,self.keep,self.retrieve,pre_bound,post_bound)
            self.compiled[id]=p
            #print p.name
            #print p.code

            for a in self.parent._adaptors:
                a.create(p,parents=[pre,post])
            self.parent._productions.append(p)

