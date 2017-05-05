from ccm.ui.pytag import *

def splitKey(key):
  r=[]
  a=''
  depth=0
  for c in key:
    if c=='.' and depth==0: 
      if a:
        r.append(a)
        a=''
    elif c in '[(':
      if a:
        r.append(a)
        a=''
      depth+=1
    elif c in '])':
      if a:
        r.append(a)
        a=''
      depth-=1
    else:
      a+=c  
  if a:
    r.append(a)
    a=''
  return r    
      
      
    

  return key.split('.')

def makeHeader(table,keys):
  keys=[splitKey(k) for k in keys]
  size=max(len(x) for x in keys)
  for k in keys:
    while len(k)<size: k.append('')
    
  noMerge=[False]*len(keys)
  for i in range(size):
    row=[keys[j][i] for j in range(len(keys))]
    merged=[]
    values=[row[0]]
    count=1
    for j in range(1,len(keys)):
      if noMerge[j] or row[j]!=values[-1]:
        merged.append(count)
        count=1
        values.append(row[j])
        noMerge[j]=True
      else:
        count+=1
    merged.append(count)
    
    row=tr()
    for j in range(len(merged)):
      row[th(colspan=repr(merged[j]))[values[j]]]
    table[row]  
          
      
colors="""AliceBlue
AntiqueWhite
Aqua  
Aquamarine
Azure  
Beige  
Bisque 
BlanchedAlmond 
BurlyWood 
Chartreuse 
Cornsilk 
Cyan 
DarkGrey 
DarkKhaki 
Darkorange 
DarkSalmon  	
DarkSeaGreen 
DarkTurquoise 
DeepSkyBlue 
DodgerBlue 
Gainsboro 
GhostWhite
Gold  
GoldenRod 
GreenYellow
HoneyDew 
Ivory  	
Khaki  	
Lavender 
LavenderBlush
LawnGreen
LemonChiffon
LightBlue 
LightCyan  	
LightGoldenRodYellow
LightGray  
LightGrey  
LightGreen 
LightPink  
LightSeaGreen 
LightSkyBlue 
LightSteelBlue 
LightYellow  
Lime
LimeGreen
Linen 
MediumAquaMarine 
MediumSeaGreen 
MediumSpringGreen
MediumTurquoise 
MintCream  	
MistyRose  
Moccasin  	
NavajoWhite 
OldLace 
Orange 
PaleGoldenRod 
PaleGreen  
PaleTurquoise 
PapayaWhip
PeachPuff 
Pink  
Plum  
PowderBlue 
Salmon  
SandyBrown 
Silver  
SkyBlue 
SpringGreen 
Tan 
Thistle 
Turquoise 
Wheat 
WhiteSmoke  
Yellow  
YellowGreen""".split()
    
    
    
    
    
  


class HTMLTrace:
  def __init__(self,trace):
    self.trace=trace
    
    
  def getColor(self,value):
    if value=='': return 'white','white'
    if value=='True' or value is True: return 'lightgreen','green'
    if value=='False' or value is False: return 'pink','red'
    if isinstance(value,(int,float)): return 'black','white'
    num=hash(value)
    return 'black',colors[num%len(colors)]

  def fixValue(self,val): 
    if val is None or val=='None': val=''
    try:    val=val.replace('<','&lt;').replace('>','&gt;')  
    except: pass  
    if type(val) not in [int,float,bool] and ':' in val:
      slots=val.split()
      for i,slot in enumerate(slots):
        if ':' in slot:
          a,b=slot.split(':',1)
          slots[i]='<i>%s:</i>%s'%(a,b)
      val=' '.join(slots)    
    
    return val  


  def makeFixedTable(self,fixed):
    t=table()
    for k in fixed:
      t[tr[td[k],td[self.trace.get_final(k)]]]
    return t
      
    
  def makeBody(self,table,keys,pts):
   
    grouped={}
    for k in keys:
      grouped[k]=list(self.trace.group_pts(pts,k))
    
    for pt in pts:
      row=tr()
      for k in keys:
        if pt not in grouped[k][0]:
          del grouped[k][0]
          
        if pt==grouped[k][0][0]:
          val=self.trace.get_at(k,pt)
          val=self.fixValue(val)
          if k=='time':
              val='%1.3f'%val
              c,bg='white','#333333'
          else:
              c,bg=self.getColor(val)

          style='background:%s; color:%s;'%(bg,c)
          row[td(rowspan=repr(len(grouped[k][0])),style=style)[val]]
      table[row]  
        
    
  def generate(self,filename):
    keys=self.trace.keys()
    fixed_keys=self.trace.fixed_keys()
    fixed_keys.sort()
    keys=[k for k in keys if k not in fixed_keys]
    keys.sort()
    
    has_time=False
    if 'time' in keys:
      keys.remove('time')
      has_time=True
    pts=self.trace.get_pts(keys)
    if has_time:
      keys.insert(0,'time')
      timePts=self.trace.get_pts(['time'])
    
    if 'time' in keys:
      self.trace.merge_pts(pts,'time')
      

         
    
    tbl=table()
    makeHeader(tbl,keys)
    self.makeBody(tbl,keys,pts)


    fixed=self.makeFixedTable(fixed_keys)    

    if not filename.endswith('.html'): filename+='.html'    
    f=file(filename,'w')
    
    page=html[
           head[
             title[filename],
             style["""
                     table {border-collapse: collapse; empty-cells:show;}
                     td {border: solid black 1px; vertical-align:top;}
                     th {border: solid #cccccc 1px; background:black; color:white;}
                   """],
             ],
           body[
             tbl,
             fixed,
             ]
           ]  
    
    print>>f,page
    
    
