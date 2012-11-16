import Tkinter
import time
from ccm.display.tk import render

class TkinterDisplay:
    root=None

    def get_root(self):
        if TkinterDisplay.root is None:
            TkinterDisplay.root=Tkinter.Tk()
        return TkinterDisplay.root
            
    def __init__(self,obj,width=640,height=480,full=False,title='CCMSuite',background='#CCCCCC'):
        self.obj=obj
        self.title=title
        self.paused=False
        self.skipped_frame=False
        self.rate=1.0
        
        root=self.get_root()

        if full:
            width, height = root.winfo_screenwidth(), root.winfo_screenheight()
            root.overrideredirect(1)
            root.geometry("%dx%d+0+0" % (width, height))        
        
        self.canvas=Tkinter.Canvas(root)
        self.canvas.configure(width=width,height=height,background=background)
        self.canvas.pack()

        obj._get_scheduler().add(self.render_loop)

        root.bind('<Escape>',self.on_escape)
        root.bind('<Pause>',self.on_pause)
        root.bind('<Prior>',self.on_pgup)
        root.bind('<Next>',self.on_pgdown)
        root.bind('<Key>',self.on_key)
        root.protocol('WM_DELETE_WINDOW',self.obj.stop)

    def update_title(self):
        rateinfo=''
        if self.rate!=1.0: rateinfo='[%1.3fx]'%self.rate
        self.get_root().title('%s: time=%1.3f%s'%(self.title,self.obj.now(),rateinfo))

    def on_escape(self,event):
        self.obj.stop()
    def on_pause(self,event):
        self.paused=not self.paused
    def on_pgup(self,event):
        self.rate*=1.1
    def on_pgdown(self,event):
        self.rate/=1.1

    def on_key(self,event):
        if hasattr(self.obj,'key_pressed'):
            self.obj.key_pressed(event.char)
        
        
    def render_loop(self):
        root=self.get_root()
        obj=self.obj
        root.update()

        dt=0.01

        while True:
            next_time=time.clock()+dt
            yield dt*self.rate
            render(obj,self.canvas)
            root.update()
            if time.clock()>next_time and obj.now()>dt:
                #print 'frame skipped at t=%1.3fs'%obj.now()
                self.skipped_frame=True
            while self.paused or time.clock()<next_time:
                root.update()
            self.update_title()
            
            

        
    


