import Tkinter
import math

class CellularRenderer:
    def __init__(self,world,canvas):
        self.world=world
        self.squares={}
        self.agents={}
        
        w=int(canvas['width'])
        h=int(canvas['height'])
        dx=w/world.width
        dy=h/world.height
        size=min((dx,dy))
        if size<1: size=1
        self.size=size
        cx=(w-size*world.width)/2
        cy=(h-size*world.height)/2
        if world.directions==6:
            cx-=size/4
        self.cx=cx
        self.cy=cy
        
        for i in range(world.width):
            for j in range(world.height):
                x,y=cx+i*size,cy+j*size
                if world.directions==6 and j%2==1: x+=size/2
                color=world.grid[j][i].color
                if callable(color): color=color()
                sq=canvas.create_rectangle((x,y,x+size,y+size),fill=color,width=0)
                self.squares[(i,j)]=(sq,color)
        self.render(canvas)

    def render(self,canvas):
        world=self.world
        for (i,j),(sq,c) in self.squares.items():
                color=world.grid[j][i].color
                if callable(color): color=color()
                if c!=color:
                    canvas.itemconfig(sq,fill=color)
                    self.squares[(i,j)]=(sq,color)
        
        for a in world.agents:
            try:
                color=a.color
                if callable(color): color=color()
            except AttributeError:
                a.color='magenta'
                color=a.color
            dir=getattr(a,'dir',None)

            if a.cell is None:
                continue

            #x=a.cell.x
            #y=a.cell.y
            x=a.x
            y=a.y
            
            if world.directions==6:
                offset=y%2
                if offset>1: offset=2-offset
                offset=offset/2
                x+=offset/2

            changed=False
            if a in self.agents:
                item,olddir,oldx,oldy,oldcolor=self.agents[a]
                if (olddir,oldx,oldy)!=(dir,x,y):
                    canvas.coords(item,self.make_triangle_pts(dir,x,y))
                    changed=True
                if oldcolor!=color:
                    canvas.itemconfig(item,fill=color)
                    changed=True
            else:
                item=canvas.create_polygon(self.make_triangle_pts(dir,x,y),fill=color,width=0)
                changed=True
            if changed:
                self.agents[a]=item,dir,x,y,color
        for a in self.agents:
            if a not in world.agents:
                item,olddir,oldx,oldy,oldcolor=self.agents[a]
                canvas.delete(item)
                
            
            
                    
        
    def make_triangle_pts(self,dir,x,y):
        if dir is not None:        
            xpts=[0,0.5,-0.5]
            ypts=[-0.8,0.8,0.8]
            angle=2*math.pi*dir/self.world.directions
            if self.world.directions==6: angle+=math.pi/2
            cos=math.cos(angle)
            sin=math.sin(angle)
            for i in range(3):
                xx=xpts[i]*cos-ypts[i]*sin
                ypts[i]=xpts[i]*sin+ypts[i]*cos
                xpts[i]=xx
        else:
            count=10
            xpts=[math.sin(2*math.pi*i/count) for i in range(count)]
            ypts=[math.cos(2*math.pi*i/count) for i in range(count)]
        
        size=self.size
        xpts=tuple(self.cx+x*size+int((xx+1)*size/2) for xx in xpts)
        ypts=tuple(self.cy+y*size+int((yy+1)*size/2) for yy in ypts)
        if self.world.directions==6 and y%2==1:
            xpts=tuple(xx+size/4 for xx in xpts)

        pts=zip(xpts,ypts)
        pts=reduce(lambda a,b:a+b,pts)
        return pts
            
        
        
