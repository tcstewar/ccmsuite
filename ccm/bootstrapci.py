import random


def sample(data):
  for x in data:
    yield random.choice(data)

def safe(f,d):
  try:
    return f(d)
  except:
    return None  



def bootstrapci(data,funcList,n=3000,p=0.95):  
  if not isinstance(funcList,(tuple,list)):
    funcList=[funcList]
  if type(data[0]) is list:
    return [(None,(None,None))]*len(funcList)
  func=lambda d: [safe(ff,d) for ff in funcList]

  index=int(n*(1-p)/2)

  s=func(data)
  r=[func(list(sample(data))) for i in range(n)]
  
  res=[]
  for i,raw in enumerate(s):
    d=sorted(x[i] for x in r)
    res.append((raw,(d[index],d[-index])))
  return res  


def bootstrapci2(data,func,n,p):
  index=int(n*(1-p)/2)
  r=[func(list(sample(data))) for i in range(n)]
  r.sort()
  return r[index],r[-index]
  
