from ccm.ui import swi
import webbrowser
from ccm.ui.pytag import T
from ccm.stats import Stats
import ccm.runner
import os
import re
import matplotlib
matplotlib.use('Agg')
import pylab
import StringIO
import math


def convert_string_to_value(x):
    if x=='True': return True
    if x=='False': return False
    try:
        return int(x)
    except:
        try:
            return float(x)
        except:
            return x
                
            

def find_directories():
    for name in os.listdir('.'):
        if os.access('%s/code.py'%name,os.F_OK):
            yield name
def find_settings(dir):
    for name in os.listdir(dir):
        if ('(' in name and os.access('%s/%s/'%(dir,name),os.F_OK)) or name=='default':
            yield name
def parse_setting_name(name):
    s={}
    for m in re.findall(r'(\w+)\(([^)]*)\)',name):
        s[m[0]]=m[1]
    return s
def make_setting_name(dir,setting):
    fn='%s/code.py'%dir
    lines=file(fn).readlines()
    params,defaults,core_code=ccm.runner.parse_code(lines)
    return ccm.runner.make_param_text(params,defaults,setting)
    

    
def make_settings_table(dir):
    data=[]
    options={}
    fn='%s/code.py'%dir
    lines=file(fn).readlines()
    params,defaults,core_code=ccm.runner.parse_code(lines)
    for name in find_settings(dir):
        setting=parse_setting_name(name)
        d=[]
        for p in params:
            v=defaults[p]
            if p in setting: v=setting[p]                
            #v=convert_string_to_value(v)
            d.append(v)
            if p not in options: options[p]=[]
            if v not in options[p]: options[p].append(v)
        data.append((d,name))
    data.sort()
    return params,data,options,defaults        
            
def combine_args(args):
    r=[]
    for k,v in args.items():
        if type(v) is list:
            for vv in v:
                r.append('%s=%s'%(k,vv))
        elif v is not None and v is not '':
            r.append('%s=%s'%(k,v))
    return '&'.join(r)        
        
                    
        

def html(title,text):
    return T.html[
              T.head[T.title["CCMSuite: %s"%title]],
              T.body[
                T.h1[title],
                T.hr,
                text,
                T.hr,
                T.a(href='/')['home']]]

class Config:
    width='8'
    height='6'
    dpi='80'
    xlabel=''
    ylabel=''
    xtickrotation='0'
    b_left='0.1'
    b_bot='0.1'
    b_top='0.1'
    b_right='0.1'    
    index='0'
    ylim=''
    xlim=''
    def __init__(self,keys):
        for k,v in keys.items():
            setattr(self,k,v)

    def plot_axis_config(self):
        return T.div[
            T.div[
                T.label['Width:'],T.input(type='text',name='width',value=self.width),
                T.label['Height:'],T.input(type='text',name='height',value=self.height),
                T.label['DPI:'],T.input(type='text',name='dpi',value=self.dpi),
                ],
            T.div[
                T.label['Label X:'],T.input(type='text',name='xlabel',value=self.xlabel),
                T.label['Label Y:'],T.input(type='text',name='ylabel',value=self.ylabel),
                T.label['X-tick rotation:'],T.input(type='text',name='xtickrotation',value=self.xtickrotation),
                ],
            T.div[
                T.label['X Limits:'],T.input(type='text',name='xlim',value=self.xlim),
                T.label['Y Limits:'],T.input(type='text',name='ylim',value=self.ylim),
                ],
            T.div[
                T.label['Left:'],T.input(type='text',name='b_left',value=self.b_left),
                T.label['Right:'],T.input(type='text',name='b_right',value=self.b_right),
                T.label['Top:'],T.input(type='text',name='b_top',value=self.b_top),
                T.label['Bottom:'],T.input(type='text',name='b_bot',value=self.b_bot),
                ],
            ]
            
    def url_args(self,**keys):
        d=dict(self.__dict__)
        d.update(keys)
        return '&'.join(['%s=%s'%(k,v) for k,v in d.items() if v!=getattr(self.__class__,k,None) and k[0]!='_'])

    def index_bar(self,url,key,max):
        value=int(getattr(self,key))
        indexbar=T.div()
        d=dict()        
        if value>0:
            d[key]=value-1
            indexbar[T.a(href='%s?%s'%(url,self.url_args(**d)))['<<'],' ']
        else:
            indexbar['<<',' ']
            
        
        for i in range(max):
            if i!=value:
                d[key]=i
                indexbar[T.a(href='%s?%s'%(url,self.url_args(**d)))[i],' ']
            else:
                indexbar[i,' ']

        if value<max-1:
            d[key]=value+1
            indexbar[T.a(href='%s?%s'%(url,self.url_args(**d)))['>>']]
        else:
            indexbar['>>']

        return indexbar

class ArrayPlotConfig(Config):
    index='0'
    dt='1'
    overlay=''
    overlay_color='b'
    overlay_thickness='2'
    overlay_scale='1'
    other_color='0.8'
    other_thickness='0.5'
    line_color='k'
    line_thickness='2'
    
    def index_config(self):
        return T.div[
            T.input(type='hidden',name='index',value=self.index),
            T.div[
                T.label['X-axis scale:'],T.input(type='text',name='dt',value=self.dt),
                ],
            T.div[
                T.label['Plot Color:'],T.input(type='text',name='line_color',value=self.line_color),
                T.label['Thickness:'],T.input(type='text',name='line_thickness',value=self.line_thickness),
                ],
            T.div[
                T.label['Other Run Color:'],T.input(type='text',name='other_color',value=self.other_color),
                T.label['Thickness:'],T.input(type='text',name='other_thickness',value=self.other_thickness),
                ],
            T.div[
                T.label['Overlay:'],T.input(type='text',name='overlay',value=self.overlay),
                T.label['Scale:'],T.input(type='text',name='overlay_scale',value=self.overlay_scale),
                T.label['Color:'],T.input(type='text',name='overlay_color',value=self.overlay_color),
                T.label['Thickness:'],T.input(type='text',name='overlay_thickness',value=self.overlay_thickness),
                ],
            ]
        


#contour_defaults=dict(contour_n=100,contour_min='',contour_max='',contour_lines=10,contour_fmt='')


#stats_graph_defaults=dict(bcount=100,conf=0.95,x=None,y=None,m=None,compare='',sortby='',
#                  xvals='',yvals=''):



class ViewerUI(swi.SimpleWebInterface):
    def swi(self):
        dirs=T.ul()
        for d in find_directories():
            dirs[T.li[T.a(href='sim/%s'%d)[d]]]
        return html('Simulations',dirs)
    
    def swi_sim(self,dir):
        fn='%s/code.py'%dir
        lines=file(fn).readlines()
        
        params,settings,options,defaults=make_settings_table(dir)
        
        header=T.tr()
        for p in params: header[T.th[p]]
        table=T.table[header]
        for row,name in settings:
            r=T.tr()
            for x in row: 
                r[T.td[x]]
            r[T.td[T.a(href='/stats/%s/%s'%(dir,name))['data']]]    
            r[T.td[T.a(href='/graph/%s/%s'%(dir,name))['graph']]]    
            table[r]
        
        
        body=T.div[T.a(href='/code/%s.py'%dir)['source code'],T.br,
                    table]
        
        return html('Simulation: %s'%dir,body)
        
    def swi_code(self,dir):
        if dir.endswith('.py'): dir=dir[:-3]
        fn='%s/code.py'%dir
        return 'text/html',T.pre[file(fn).read()]
        
    def swi_stats(self,dir,name,bcount=100,conf=0.95):
    
        form=T.form(action="/stats/%s/%s"%(dir,name),method="get")[
            T.label['Confidence Interval:'],T.input(type='text',name='conf',value=conf),
            T.label['Bootstrap Samples:'],T.input(type='text',name='bcount',value=bcount),
            T.input(type='submit',value='Recalculate')
            ]
            
        s=ccm.stats.Stats('%s/%s'%(dir,name))
        
        statistics=['mean','median','sd']
        
        table=T.table()
        row=T.tr[T.th['']]
        for stat in statistics:
            row[T.th(colspan='3')[stat]]
        row[T.th]    
        table[row]    
        row=T.tr[T.th['measure']]
        for stat in statistics:
            row[T.th['low'],T.th['sample'],T.th['high']]
        row[T.th]    
        table[row]    
        for m in sorted(s.measures()):
            sm=s.measure(m)
            row=T.tr[T.td[m]]
            for stat in statistics:
                data=sm.get_stat(stat,int(bcount),float(conf))
                
                if data is None:
                    row[T.td(),T.td(),T.td()]
                else:
                    if data[1][0] is None: row[T.td()]
                    else: row[T.td(bgcolor='#EEEEEE')['%f'%data[1][0]]]
                    if data[0] is None: row[T.td()]
                    else: row[T.td(bgcolor='#CCCCCC')['%f'%data[0]]]
                    if data[1][1] is None: row[T.td()]
                    else:row[T.td(bgcolor='#AAAAAA')['%f'%data[1][1]]]                    
            row[T.td[T.a(href='/rawdata/%s/%s/%s'%(dir,name,m))['raw data']]]        
            table[row]    
        
        return html('%s <small>%s</small>'%(T.a(href='/sim/%s'%dir)[dir],name),T.div[T.a(href='/graph/%s/%s'%(dir,name))['graph'],T.br,form,'N=%d'%s.N,table])#,iframe])
        
    def swi_rawdata(self,dir,name,measure,**keys):
        s=ccm.stats.Stats('%s/%s'%(dir,name))
        data=s.get_raw(measure)
        
        c=ArrayPlotConfig(keys)

        page=T.div()
        config=T.form(action="/rawdata/%s/%s/%s"%(dir,name,measure),method="get")[
            c.index_bar("/rawdata/%s/%s/%s"%(dir,name,measure),'index',len(data)),
            c.index_config(),
            T.br,
            c.plot_axis_config(),
            T.input(type='submit',value='Update'),          
            ]            
            
        params,settings,options,defaults=make_settings_table(dir)
        setting=parse_setting_name(name)
        params=T.table(border=1)    
        row1=T.tr()
        row2=T.tr()
        for k,vv in sorted(options.items()):
            if len(vv)>1:
                row1[T.th[k]]
                values=T.td()
                vvlist=list(sorted(vv,key=lambda x: convert_string_to_value(x)))
                for i in range(len(vvlist)):
                    vvv=vvlist[i]
                    sval=setting.get(k,defaults[k])
                    if vvv==sval:
                        values[T.b[vvv],T.br]                    
                    else:
                        setting2=dict(setting)
                        setting2[k]=vvv
                        name2=make_setting_name(dir,setting2)
                        values[T.a(href="/rawdata/%s/%s/%s?%s"%(dir,name2,measure,c.url_args()))[vvv],T.br]
                row2[values]
        params[row1,row2]
            
                
        if type(data[0]) is float or type(data[0]) is int:
            table=T.table()
            for d in data:
                table[T.tr[T.td[d]]]
            
            page[table,T.img(src='/histogram/%s/%s/%s'%(dir,name,measure))]
            
            return str(page)
        elif type(data[0]) is list and type(data[0][0]) is float:                        
            page[T.a(href='/arrayplot/%s/%s/%s?%s'%(dir,name,measure,c.url_args(dpi=300)))[T.img(style='float:right',src='/arrayplot/%s/%s/%s?%s'%(dir,name,measure,c.url_args()))],params,config]
                
                
        return str(page)
        
        
    def swi_arrayplot(self,dir,name,measure,**keys):    
        s=ccm.stats.Stats('%s/%s'%(dir,name))
        data=s.get_raw(measure) 

        c=ArrayPlotConfig(keys)
    
        index=int(c.index)
        
        pylab.figure(figsize=(float(c.width),float(c.height)))
        pylab.axes((float(c.b_left),float(c.b_bot),1.0-float(c.b_left)-float(c.b_right),1.0-float(c.b_top)-float(c.b_bot)))

        max_index=len(data[0])
        
        
        t=pylab.arange(len(data[0]))*float(c.dt)

        if c.other_color!='':
            for i in range(len(data)):
                d=data[i]
                if i!=index:
                    pylab.plot(t,d,color=c.other_color,linewidth=c.other_thickness)


        if c.overlay!='':
            data2=s.get_raw(c.overlay)
            if data2 is not None:
                d=data2[index]
                scale=float(c.overlay_scale)
                d=[scale*x for x in d]
                pylab.plot(t[:len(d)],d,color=c.overlay_color,linewidth=c.overlay_thickness)
        
        if c.line_color!='':
            d=data[index]
            pylab.plot(t,d,color=c.line_color,linewidth=c.line_thickness)
        
        if ',' in c.xlim:
            mn,mx=c.xlim.split(',',1)
            pylab.xlim((float(mn),float(mx)))
        if ',' in c.ylim:
            mn,mx=c.ylim.split(',',1)
            pylab.ylim((float(mn),float(mx)))
        
        
        if c.xlabel!='':
            pylab.xlabel(c.xlabel)
        if c.ylabel!='':
            pylab.ylabel(c.ylabel)
        else:
            pylab.ylabel(measure)    
        
                
            
        
        img=StringIO.StringIO()
        dpi=c.dpi
        if type(dpi) is list: dpi=dpi[-1]
        pylab.savefig(img,dpi=int(dpi),format='png')
        return 'image/png',img.getvalue()
    
    
        
    def swi_histogram(self,dir,name,measure,dpi=80,width=8,height=6,b_left='0.1',b_bot='0.1',b_top='0.1',b_right='0.1',bins='20'):
        s=ccm.stats.Stats('%s/%s'%(dir,name))
        data=s.get_raw(measure) 
        
        bins=int(bins)
        
           

        pylab.figure(figsize=(float(width),float(height)))
        try: b_left=float(b_left)
        except: b_left=0.1
        try: b_right=float(b_right)
        except: b_right=0.1
        try: b_top=float(b_top)
        except: b_top=0.1
        try: b_bot=float(b_bot)
        except: b_bot=0.1
        pylab.axes((b_left,b_bot,1.0-b_left-b_right,1.0-b_top-b_bot))
        
        
        pylab.hist(data,bins=bins)

            
        
        img=StringIO.StringIO()
        if type(dpi) is list: dpi=dpi[-1]
        pylab.savefig(img,dpi=int(dpi),format='png')
        return 'image/png',img.getvalue()
        
   
    def swi_graph(self,dir,name,bcount=100,conf=0.95,x=None,y=None,multi=None,m=None,compare='',sortby='',width=8,height=6,dpi=80,
                  xvals='',yvals='',multivals='',contour_n=100,contour_min='',contour_max='',contour_lines=10,contour_fmt='',xlabel='',ylabel='',
                  xtickrotation='0',b_left='0.1',b_bot='0.1',b_top='0.1',b_right='0.1'):
        measures=m
        params,settings,options,defaults=make_settings_table(dir)
        setting=parse_setting_name(name)

        s=ccm.stats.Stats('%s/%s'%(dir,name))
        
        if x not in options or len(options[x])<=1: x=None
        if y not in options or len(options[y])<=1: y=None
        if multi not in options or len(options[multi])<=1: multi=None
        if xvals is '' and x is not None:
            xvals=';'.join(['%s'%xx for xx in sorted(options[x])])
        if yvals is '' and y is not None:
            yvals=';'.join(['%s'%yy for yy in sorted(options[y])])
        if multivals is '' and multi is not None:
            multivals=';'.join(['%s'%yy for yy in sorted(options[multi])])
        if x is None: xvals=''
        if y is None: yvals=''    
        if multi is None: multivals=''
        
        if measures is None: 
            measures=list(sorted(s.measures()))
            if len(measures)>10: measures=measures[:10]
        if type(measures) is str: measures=[measures]

        imgargs=combine_args(dict(bcount=bcount,conf=conf,x=x,y=y,multi=multi,m=measures,compare=compare,width=width,height=height,dpi=dpi,
                              sortby=sortby,xvals=xvals,yvals=yvals,multivals=multivals,contour_n=contour_n,contour_max=contour_max,contour_min=contour_min,contour_lines=contour_lines,contour_fmt=contour_fmt,
                              xlabel=xlabel,ylabel=ylabel,xtickrotation=xtickrotation,b_top=b_top,b_bot=b_bot,b_left=b_left,b_right=b_right))
        
        f_sort=T.div[
            T.label['Sort by:'],T.input(type='text',name='sortby',value=sortby),
            ]
            
        
        f_ci=T.div[
            T.label['Confidence Interval:'],T.input(type='text',name='conf',value=conf),
            T.label['Bootstrap Samples:'],T.input(type='text',name='bcount',value=bcount),
            ]
        f_compare=T.div[
            T.label['Compare to:'],T.input(type='text',name='compare',value=compare)[''],
            ]
        f_size=T.div[
            T.label['Width:'],T.input(type='text',name='width',value=width),
            T.label['Height:'],T.input(type='text',name='height',value=height),
            T.label['DPI:'],T.input(type='text',name='dpi',value=dpi),
            ]
            
        f_axes=T.div[
            T.label['X-Axis:'],T.select(name='x',onchange='this.form.submit();')[[T.option(**[{},dict(selected='y')][x==None])['---']]+[T.option(**[{},dict(selected='y')][x==k])[k] for k,v in sorted(options.items()) if len(v)>1]],
            T.label['values:'],T.input(type='text',name='xvals',value=[xvals,''][xvals==None]),
            T.br,
            T.label['Y-Axis:'],T.select(name='y',onchange='this.form.submit();')[[T.option(**[{},dict(selected='y')][y==None])['---']]+[T.option(**[{},dict(selected='y')][y==k])[k] for k,v in sorted(options.items()) if len(v)>1]],
            T.label['values:'],T.input(type='text',name='yvals',value=[yvals,''][yvals==None]),
            T.br,
            T.label['Multiline:'],T.select(name='multi',onchange='this.form.submit();')[[T.option(**[{},dict(selected='y')][multi==None])['---']]+[T.option(**[{},dict(selected='y')][multi==k])[k] for k,v in sorted(options.items()) if len(v)>1]],
            T.label['values:'],T.input(type='text',name='multivals',value=[multivals,''][multivals==None]),
            ]    
            
        f_labels=T.div[
            T.label['Label X:'],T.input(type='text',name='xlabel',value=xlabel),
            T.label['Label Y:'],T.input(type='text',name='ylabel',value=ylabel),
            T.label['X-tick rotation:'],T.input(type='text',name='xtickrotation',value=xtickrotation),
            ]
        f_border=T.div[
            T.label['Left:'],T.input(type='text',name='b_left',value=b_left),
            T.label['Right:'],T.input(type='text',name='b_right',value=b_right),
            T.label['Top:'],T.input(type='text',name='b_top',value=b_top),
            T.label['Bottom:'],T.input(type='text',name='b_bot',value=b_bot),
            ]
            
            
        f_contour=T.div()
        if x is not None and y is not None:
            f_contour[T.label['Contour Shading:'],T.input(type='text',name='contour_n',size=5,value=contour_n)]
            f_contour[T.label['Lines:'],T.input(type='text',name='contour_lines',size=5,value=contour_lines)]
            f_contour[T.br]
            f_contour[T.label['Contour Min:'],T.input(type='text',name='contour_min',size=5,value=contour_min)]
            f_contour[T.label['Max:'],T.input(type='text',name='contour_max',size=5,value=contour_max)]
            f_contour[T.label['Format:'],T.input(type='text',name='contour_fmt',size=6,value=contour_fmt)]
                
            
        params=T.table(border=1)    
        row1=T.tr()
        row2=T.tr()
        for k,vv in sorted(options.items()):
            if len(vv)>1:
                row1[T.th[k]]
                values=T.td()
                vvlist=list(sorted([convert_string_to_value(vvv) for vvv in vv]))
                #vvlist=list(sorted(vv))
                for i in range(len(vvlist)):
                    vvv=vvlist[i]
                    sval=setting.get(k,defaults[k])
                    if vvv==convert_string_to_value(sval) or vvv==sval:
                        values[T.b[vvv],T.br]                    
                    else:
                        setting2=dict(setting)
                        setting2[k]=vvv
                        name2=make_setting_name(dir,setting2)
                        values[T.a(href="/graph/%s/%s?%s"%(dir,name2,imgargs))[vvv],T.br]
                row2[values]
        params[row1,row2]
        
        
        
        
        f_measures=T.select(multiple='y',size=20,name='m')
        for m in sorted(s.measures()):
            if m in measures:
                opt=T.option(value=m,selected='y')[m]
            else:
                opt=T.option(value=m)[m]
            f_measures[opt]
        
        src='/graphpng/%s/%s?%s'%(dir,name,imgargs)
        img=T.a(href=src+'&dpi=300')[T.img(src=src,style='float:right')]
        
    
        form=T.form(action="/graph/%s/%s"%(dir,name),method="get")[
            img,
            T.a(href='/stats/%s/%s'%(dir,name))['data'],
            params,
            f_axes,
            f_contour,
            f_measures,T.input(type='submit',value='Recalculate'),
            f_sort,T.br,
            f_ci,T.br,#'N=%d'%s.N,T.br,
            f_compare,T.br,
            f_size,T.br,
            f_labels,T.br,
            f_border,T.br,
            T.input(type='submit',value='Recalculate')            
            ]
    

        return html('%s <small>%s</small>'%(T.a(href='/sim/%s'%dir)[dir],name),form)
    
    def swi_graphpng(self,dir,name,bcount=100,conf=0.95,x=None,y=None,m=None,multi=None,dpi=80,width=8,height=6,
                          compare='',sortby='',xvals='',yvals='',multivals='',contour_n=20,contour_min='',contour_max='',contour_lines=10,contour_fmt='',
                          xlabel='',ylabel='',xtickrotation='',b_left='',b_bot='',b_top='',b_right=''):
        pylab.figure(figsize=(float(width),float(height)))
        try: b_left=float(b_left)
        except: b_left=0.1
        try: b_right=float(b_right)
        except: b_right=0.1
        try: b_top=float(b_top)
        except: b_top=0.1
        try: b_bot=float(b_bot)
        except: b_bot=0.1
        pylab.axes((b_left,b_bot,1.0-b_left-b_right,1.0-b_top-b_bot))
        try: xtickrotation=float(xtickrotation)
        except: xtickrotation=0
        
        if len(compare)>0:
            if '/' not in compare:
                c_dir,c_name=compare,'default'
            else:
                c_dir,c_name=compare.split('/',1)
            c_names,c_sample,c_ci=extract_individual_data(c_dir,c_name,int(bcount),float(conf),m)
        else:
            c_names=[]    
        xvals=xvals.split(';')
        yvals=yvals.split(';')
        multivals=multivals.split(';')
        if type(m) is str: m=[m]
        



        if x is None and y is None:
            names,sample,ci=extract_individual_data(dir,name,int(bcount),float(conf),m)            
            
            if len(c_names)>0 and sortby!='':
                reversed=False
                if sortby.endswith('_r'):
                    reversed=True
                    sortby=sortby[:-2]
                data=compare_stats(sortby,names,sample,ci,c_names,c_sample,c_ci)
                data.sort()
                if reversed: data.reverse()
                index=[names.index(x[1]) for x in data]
                names=[names[i] for i in index]
                
                sample=pylab.array([sample[i] for i in index])
                ci=pylab.array([ci[i] for i in index])
                c_sample=pylab.array([c_sample[i] for i in index])
                c_ci=pylab.array([c_ci[i] for i in index])
            
            
            xvalpts=pylab.array(range(len(names)))
            

            if len(c_names)>0:
                capsize=4                
                c_yerr=pylab.array([c_sample-c_ci[:,1],c_ci[:,0]-c_sample])
                compare=True
                barwidth=0.4
                pylab.bar(xvalpts+0.2,c_sample,align='center',color='#CCCCCC',width=barwidth)
                pylab.errorbar(xvalpts+0.2,c_sample,yerr=c_yerr,ecolor='k',capsize=capsize,linewidth=0,elinewidth=1)
                xvalpts=xvalpts-0.2
            else:
                capsize=5
                compare=False    
                barwidth=0.8
        
            
            pylab.bar(xvalpts,sample,align='center',color='#EEEEEE',width=barwidth)
            yerr=pylab.array([sample-ci[:,1],ci[:,0]-sample])
            pylab.errorbar(xvalpts,sample,yerr=yerr,ecolor='k',capsize=capsize,linewidth=0,elinewidth=1)
                                    
            pylab.xticks(range(len(names)),names,rotation=xtickrotation)
            pylab.xlim(-1,len(names))
        elif x is not None and y is None:        
            setting=parse_setting_name(name)
            xvalpts=pylab.array(range(len(xvals)))


            gfile=open('most_recent_graph.py','w')

            
            if False and len(compare)>0:
                pass                        
            elif multi is not None:
                for mv in multivals:
                  for measure in m:
                    v=[]
                    vlow=[]
                    vhigh=[]
                    for xval in xvals:
                        setting2=dict(setting)
                        setting2[x]=xval
                        setting2[multi]=mv
                        name2=make_setting_name(dir,setting2)                    
                        names,sample,ci=extract_individual_data(dir,name2,int(bcount),float(conf),measure)            
                        v.append(sample[0])
                        vlow.append(sample[0]-ci[0][1])
                        vhigh.append(ci[0][0]-sample[0])
                    if len(multivals)==1:
                        label=measure
                    elif len(m)==1:
                        label=mv
                    else:
                        label='%s:%s'%(mv,measure)
                    pylab.plot(xvalpts,v,label=label)
                    pylab.errorbar(xvalpts,v,yerr=[vlow,vhigh],ecolor='k',capsize=3,linewidth=0,elinewidth=1)
                    
                    gfile.write('pylab.plot(%s,%s)\n'%(list(xvalpts),v))
                    gfile.write('pylab.errorbar(%s,%s,yerr=[%s,%s])\n'%(list(xvalpts),v,vlow,vhigh))
                    
                pylab.legend(loc='best') 
            
            else:
                for measure in m:
                    v=[]
                    vlow=[]
                    vhigh=[]
                    for xval in xvals:
                        setting2=dict(setting)
                        setting2[x]=xval
                        name2=make_setting_name(dir,setting2)                    
                        names,sample,ci=extract_individual_data(dir,name2,int(bcount),float(conf),measure)            
                        v.append(sample[0])
                        vlow.append(sample[0]-ci[0][1])
                        vhigh.append(ci[0][0]-sample[0])
                    pylab.plot(xvalpts,v,label=measure)
                    pylab.errorbar(xvalpts,v,yerr=[vlow,vhigh],ecolor='k',capsize=3,linewidth=0,elinewidth=1)
                pylab.legend(loc='best')    
                
            
            
            pylab.xticks(xvalpts,xvals)
            pylab.xlim(-0.2,xvalpts[-1]+0.2)   
            if xlabel=='':
                pylab.xlabel(x)
            else:
                pylab.xlabel(xlabel)    
            if ylabel!='':
                pylab.ylabel(ylabel)
        elif x is not None and y is not None:
            setting=parse_setting_name(name)
            xvalpts=pylab.array(range(len(xvals)))
            yvalpts=pylab.array(range(len(yvals)))
            contour_n=int(contour_n)
            contour_lines=int(contour_lines)
            if len(contour_max)==0: contour_max=None
            else: contour_max=float(contour_max)
            if len(contour_min)==0: contour_min=None
            else: contour_min=float(contour_min)
            if contour_fmt=='': contour_fmt='%1.3f'
            
            data=[]
            for yval in yvals:
                setting2=dict(setting)
                setting2[y]=yval
                row=[]
                for xval in xvals:
                    setting2[x]=xval
                    name2=make_setting_name(dir,setting2)                    
                    names,sample,ci=extract_individual_data(dir,name2,int(bcount),float(conf),m)            
                    
                    if len(compare)>0:
                        d=compare_combine(sortby,names,sample,ci,c_names,c_sample,c_ci)
                    else:
                        d=sample[0]
                    
                    row.append(d)
                data.append(row)
            
            if contour_min is None or contour_max is None:    
                pylab.contourf(xvalpts,yvalpts,data,contour_n,antialiased=True,extend='both')
                cs=pylab.contour(xvalpts,yvalpts,data,contour_lines,colors='k',linewidths=1)
            else:
                clevels=pylab.array(range(contour_n))*(contour_max-contour_min)/(contour_n-1)+contour_min
                pylab.contourf(xvalpts,yvalpts,data,list(clevels),antialiased=True,extend='both')
                clevels=pylab.array(range(contour_lines))*(contour_max-contour_min)/(contour_lines-1)+contour_min
                cs=pylab.contour(xvalpts,yvalpts,data,list(clevels),colors='k',linewidths=1)
            pylab.clabel(cs,fmt=contour_fmt)
            
        
        
            pylab.xticks(xvalpts,xvals,rotation=xtickrotation)
            if xlabel=='':
                pylab.xlabel(x)
            else:
                pylab.xlabel(xlabel)    
            pylab.yticks(yvalpts,yvals)
            if ylabel=='':
                pylab.ylabel(y)
            else:
                pylab.ylabel(ylabel)
            
                


        
        img=StringIO.StringIO()
        if type(dpi) is list: dpi=dpi[-1]
        pylab.savefig(img,dpi=int(dpi),format='png')
        pylab.close()
        return 'image/png',img.getvalue()


def compare_two(method,v1,ci1,v2,ci2):
    if method=='diff': return v2-v1
    if method in ['diff2','rmse','mse']: return (v2-v1)*(v2-v1)
    
    equiv=max(ci2[1]-ci1[0],ci1[1]-ci2[0])
    if method=='equiv': return equiv
    if method=='relequiv': return equiv/(ci2[1]-ci2[0])
    if method=='within': return float(equiv<(ci2[1]-ci2[0]))
    
    return 0

def compare_stats(method,names1,s1,ci1,names2,s2,ci2):
    data=[]
    for i,n in enumerate(names1):
        if n in names2:
            j=names2.index(n)
            x=compare_two(method,s1[i],ci1[i],s2[j],ci2[j])
            data.append((x,n))
    return data        
    
def compare_combine(method,names1,s1,ci1,names2,s2,ci2):
    data=compare_stats(method,names1,s1,ci1,names2,s2,ci2)
    data=[d[0] for d in data]
    if method in ['diff','diff2','mse','rmse','within']:
        data=sum(data)/len(data)
        if method=='rmse': data=math.sqrt(data)
    else:
        data=max(data)
    return data            
            
    
    
        

def extract_individual_data(dir,name,bcount,conf,measures):
    if type(measures) is str: measures=[measures]
    s=ccm.stats.Stats('%s/%s'%(dir,name))
    names=[]
    sample=[]
    ci=[]
    for m in measures:
        names.append(m)
        sm=s.measure(m)
        ss,c=sm.get_stat('mean',bcount,conf)
        sample.append(ss)
        ci.append(c)
    return names,pylab.array(sample),pylab.array(ci)
    


port=8080    
#webbrowser.open('localhost:%d'%port)

#webbrowser.open('http://localhost:8081/graph/seqblend/threshold(-1)%20noise(0.3)?m=est01&m=est02&m=est03&m=est04&m=est05&m=est06&m=est07&m=est08&m=est09&m=est10&conf=0.95&bcount=100&compare=human%2Fdefault&sortby=diff')
#webbrowser.open('http://localhost:8081/graph/seqblend/threshold(-1)%20noise(0.3)?x=noise&xvals=0.001%3B0.01%3B0.1%3B0.2%3B0.3%3B0.4%3B0.5%3B0.6%3B0.7%3B0.8&y=threshold&yvals=-4.0%3B-3.5%3B-3%3B-2.5%3B-2%3B-1.5%3B-1%3B-0.5%3B0%3B0.5&contour_n=100&contour_lines=10&contour_min=&contour_max=&contour_fmt=&m=est01&m=est02&m=est03&m=est04&m=est05&m=est06&m=est08&m=est09&m=est10&m=est11&m=est12&m=est14&m=est15&m=est16&m=est17&m=est18&m=est19&m=est22&m=est23&m=est25&m=est26&m=est27&m=est28&m=est29&m=est31&m=est32&m=est33&m=est34&m=est35&m=est37&m=est38&m=est39&m=est40&m=est41&m=est42&m=est43&m=est44&m=est46&m=est47&m=est48&m=est50&m=est51&m=est52&m=est53&m=est54&m=est55&m=est56&m=est57&m=est58&m=est59&m=est60&sortby=relequiv&conf=0.95&bcount=100&compare=human%2Fdefault&width=8&height=6&dpi=80')
swi.start(ViewerUI,port)
    
    
    

