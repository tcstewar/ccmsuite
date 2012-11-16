from __future__ import generators

import ccm.logger as logger

import os
import random
import re
import time

using_java=False
try:
    from java.io import File
    using_java=True
except:
    pass

def file_exists(filename):
    if hasattr(os,'access'):
        return os.access(filename,os.F_OK)
    elif using_java:
        return File(filename).exists()
        
    


def parse_code(lines):
    code=''
    defaults={}
    params=[]
    for i,line in enumerate(lines):
        line=line.strip()
        if len(line)==0: continue
        elif line.startswith('#'): continue
        elif '=' in line:
            k,v=line.split('=',2)
            params.append(k)
            defaults[k]=v
        elif '__future__' in line and 'generators' in line:
            continue
        else:
            code=''.join(lines[i:])
            break
    return params,defaults,code

def make_param_code(params,defaults,settings):
    p=[]
    for pp in params:
        v=defaults[pp]
        if pp in settings: v=fix_setting(settings[pp])
        p.append('%s=%s'%(pp,v))
    return '\n'.join(p)

def make_param_text(params,defaults,settings):
    p=[]
    for pp in params:
        if pp in settings and '%s'%settings[pp]!='%s'%defaults[pp]:
            v=settings[pp]
            p.append('%s(%s)'%(pp,v))
    if len(p)==0: return 'default'        
    return ' '.join(p)


def fix_setting(v):
    if not isinstance(v,(int,float)): 
        v=`v`
    return v


def make_settings_combinations(settings,keys=None):
    if keys is None: keys=settings.keys()
    if len(keys)==0: 
        yield {}
        return
    
    k=keys.pop()
    v=settings[k]
    for setting in make_settings_combinations(settings,keys):
        if type(v) is list:
            for vv in v:
                setting[k]=vv
                yield setting
        else:
            setting[k]=v
            yield setting

def ensure_backup(fn,lines):
    name=fn[:-3]+'/code.py'
    if not file_exists(fn[:-3]+'/'): os.makedirs(fn[:-3])
    if not file_exists(name):
        f=file(name,'w')
        f.write(''.join(lines))
        f.close()
    else:
        f=file(name)
        if lines!=f.readlines():
            f.close()
            t=os.stat(name).st_mtime
            text=time.strftime('%Y%m%d-%H%M%S',time.localtime(t))
            name2='%s/code-%s.py'%(fn[:-3],text)
            
            os.rename(name,name2)
            f=file(name,'w')
            f.write(''.join(lines))
            f.close()
    

run_external=None
def run_with(script):
    global run_external
    run_external=script
    


def run(_filename,_iterations=1,**settings):
    if not _filename.endswith('.py'): _filename+='.py'
    if not file_exists(_filename):
        raise 'Could not find file: %s'%_filename
    
    lines=file(_filename).readlines()
    params,defaults,core_code=parse_code(lines)
    
    ensure_backup(_filename,lines)
    
    
    f=None
    fname='.ccmtmp%08x.py'%random.randrange(0,0x70000000)

    for i in xrange(_iterations):
      for setting in make_settings_combinations(settings):
        param_code=make_param_code(params,defaults,setting)
        param_text=make_param_text(params,defaults,setting)
        
        if 'ccm.log' not in core_code:
            core_code='import ccm\nccm.log()\n'+core_code

        code='%s\n%s'%(param_code,core_code)
        code=code.replace('\r\n','\n')
        logline='ccm.log(data=True,screen=False,directory="%s/%s")'%(_filename[:-3],param_text)
        code=re.sub(r'ccm\.log\([^)]*\)',logline,code)
                
        print _filename,'%d/%d'%(i,_iterations),param_text
        
        f=file(fname,'w')
        f.write(code)
        f.flush()
        
        if run_external is None:
            compiled=compile(code,fname,'exec')
            exec compiled in {}
            logger.finished()
        else:
            os.system('%s %s'%(run_external,fname))    
        f.close()
    os.remove(fname)
        


if __name__=='__main__':
    run()
  

        

