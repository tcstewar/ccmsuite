import pygame
import time
from ccm.display.pygame import render

class PygameDisplay:
    def __init__(self,obj,width=640,height=480,full=False,title='CCMSuite',background='#CCCCCC'):
        self.obj=obj
        self.title=title
        self.paused=False
        self.skipped_frame=False
        self.rate=1.0
        
        pygame.init()
        self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE|pygame.DOUBLEBUF,32)
        self.background=pygame.Color(background)

        obj._get_scheduler().add(self.render_loop)

    def update_title(self):
        rateinfo=''
        if self.rate!=1.0: rateinfo='[%1.3fx]'%self.rate
        pygame.display.set_caption('%s: time=%1.3f%s'%(self.title,self.obj.now(),rateinfo))

    def on_escape(self):
        self.obj.stop()
    def on_pause(self):
        self.paused=not self.paused
    def on_pgup(self):
        self.rate*=1.1
    def on_pgdown(self):
        self.rate/=1.1

    def on_key(self,key):
        if hasattr(self.obj,'key_pressed'):
            self.obj.key_pressed(key)
        
        
    def render_loop(self):
        obj=self.obj

        dt=0.01

        while True:
            next_time=time.clock()+dt
            yield dt*self.rate
            self.screen.fill(self.background)
            render(obj,self.screen)
            self.handle_events()
            pygame.display.flip()
            if time.clock()>next_time and obj.now()>dt:
                #print 'frame skipped at t=%1.3fs'%obj.now()
                self.skipped_frame=True
                if dt<0.3: 
                    dt+=0.01
            while self.paused or time.clock()<next_time:
                self.handle_events()
            self.update_title()
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                     self.obj.stop()
                elif event.key==pygame.K_PAGEDOWN:
                     self.on_pgdown()
                elif event.key==pygame.K_PAGEUP:
                     self.on_pgup()
                elif event.key==pygame.K_PAUSE:
                     self.on_pause()

                elif event.key<128:
                     self.on_key(chr(event.key))
            elif event.type==pygame.QUIT:
                self.obj.stop()

                    

        
    


