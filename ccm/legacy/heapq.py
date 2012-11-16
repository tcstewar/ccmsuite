def heapify(x):
  x.sort()

def heappush(x,item):
  x.append(item)
  x.sort()

def heappop(x):
  return x.pop(0)
