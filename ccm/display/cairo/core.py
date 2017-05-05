import pygtk,gtk
import cairo

import time

from math import pi,sqrt


def render_line(obj,cr,width,height):
    x1=obj.x1*width
    y1=obj.y1*height
    x2=obj.x2*width
    y2=obj.y2*height

    thickness=getattr(obj,'thickness',2)
    spacing1=getattr(obj,'spacing1',0)
    spacing2=getattr(obj,'spacing2',0)

    xx1=x1+(x2-x1)*spacing1
    xx2=x2+(x1-x2)*spacing2
    yy1=y1+(y2-y1)*spacing1
    yy2=y2+(y1-y2)*spacing2

    cr.set_source_rgb(*obj.color)
    cr.move_to(xx1,yy1)
    cr.line_to(xx2,yy2)

    head2=getattr(obj,'head2',0)
    if head2>0:
        scale=0.6
        xx4=xx2-(xx2-xx1)*head2
        yy4=yy2-(yy2-yy1)*head2
        dx=xx4-xx2
        dy=yy4-yy2

        cr.move_to(xx2,yy2)
        cr.line_to(xx4-dy*scale,yy4+dx*scale)
        cr.move_to(xx2,yy2)
        cr.line_to(xx4+dy*scale,yy4-dx*scale)


    cr.stroke()




def render_area(obj,cr,width,height):
    color=(1,1,1)
    if hasattr(obj,'color'): color=obj.color
    if color is not None:
        cr.set_source_rgb(*color)
        cr.rectangle(0, 0, width, height)
        cr.fill()
    for c in obj.get_children():
        if hasattr(c,'x') and hasattr(c,'y'):
            if getattr(c,'visible',True):
                if hasattr(c,'nef'):
                    render_nef(c,cr,width,height)
                elif hasattr(c,'color'):
                    if hasattr(c,'text'):
                        render_text(c,cr,width,height)
                    elif hasattr(c,'width') and hasattr(c,'height'):
                        render_box(c,cr,width,height)
        elif hasattr(c,'x1') and hasattr(c,'y1') and hasattr(c,'x2') and hasattr(c,'y2') and hasattr(c,'color'):
            render_line(c,cr,width,height)

def render_box(obj,cr,width,height):
    x=obj.x*width
    y=obj.y*height
    w=obj.width
    h=obj.height
    cr.set_source_rgb(*obj.color)
    cr.rectangle(x-w/2,y-h/2,w,h)
    cr.fill()

def render_text(obj,cr,width,height):
    x=obj.x*width
    y=obj.y*height

    cr.set_font_size(40)

    fa,fd,fh,fxa,fya=cr.font_extents()

    xb,yb,w,h,xa,ya=cr.text_extents(obj.text)

    cr.set_source_rgb(*obj.color)
    cr.move_to(x+0.5-xb-w/2,y+0.5-fd+fh/2)
    cr.show_text(obj.text)

def render_nef(obj,cr,width,height):
    mode=getattr(obj,'display',obj.nef.mode)
    if mode=='spike':
        render_nef_spikes(obj,cr,width,height)
    elif mode=='rate':
        render_nef_rate(obj,cr,width,height)
    elif mode=='direct':
        render_nef_direct(obj,cr,width,height)


def render_nef_spikes(obj,cr,width,height):
    size=getattr(obj,'size',10)
    scale=getattr(obj,'scale',1)
    cx=obj.x*width
    cy=obj.y*height

    neurons=obj.nef.neurons
    row_count=getattr(obj,'row_count',int(sqrt(neurons)))
    col_count=getattr(obj,'col_count',None)
    if col_count is None:
        col_count=neurons/row_count
        if col_count*row_count<neurons: col_count+=1

    x=cx-col_count*size/2
    y=cy-row_count*size/2

    v=obj.nef.value()     ## make sure the value has been updated

    for j in range(row_count):
        for i in range(col_count):
            index=j*col_count+i
            if index<neurons:

                z=obj.nef.voltage[index]
                color=(z*scale,z*scale,z*scale)
                if obj.nef.spikes[index]>0:
                    color=(1,1,1)

                cr.set_source_rgb(*color)
                cr.arc(x+i*size,y+j*size,(size-0.5)/2,0,2*pi)
                cr.fill()

def render_nef_rate(obj,cr,width,height):
    size=getattr(obj,'size',10)
    scale=getattr(obj,'scale',1)
    cx=obj.x*width
    cy=obj.y*height

    neurons=obj.nef.neurons
    row_count=getattr(obj,'row_count',int(sqrt(neurons)))
    col_count=getattr(obj,'col_count',None)
    if col_count is None:
        col_count=neurons/row_count
        if col_count*row_count<neurons: col_count+=1

    x=cx-col_count*size/2
    y=cy-row_count*size/2

    v=obj.nef.value()     ## make sure the value has been updated
    for j in range(row_count):
        for i in range(col_count):
            index=j*col_count+i
            if index<neurons:

                z=obj.nef._output[index]*scale/obj.nef.saturation_range[1]
                color=(z*1.0,z*1.0,z*1.0)

                cr.set_source_rgb(*color)
                cr.arc(x+i*size,y+j*size,(size-0.5)/2,0,2*pi)
                cr.fill()

def render_nef_direct(obj,cr,width,height):
    size=getattr(obj,'size',20)
    cx=obj.x*width
    cy=obj.y*height

    dims=obj.nef.dimensions
    row_count=getattr(obj,'row_count',int(sqrt(dims)))
    col_count=getattr(obj,'col_count',None)
    if col_count is None:
        col_count=dims/row_count
        if col_count*row_count<dims: col_count+=1

    x=cx-col_count*size/2
    y=cy-row_count*size/2

    v=obj.nef.value()

    outline=getattr(obj,'outline',(0,0,0))
    if outline is not None:
        cr.set_source_rgb(*outline)
        cr.rectangle(x,y,size*col_count,size*row_count)
        cr.stroke()

    for j in range(row_count):
        for i in range(col_count):
            index=j*col_count+i
            if index<dims:

                z=v[index]*0.5+0.5
                color=(z*1.0,z*1.0,z*1.0)

                cr.set_source_rgb(*color)

                cr.rectangle(x+i*size,y+j*size,size,size)
                cr.fill()

                if getattr(obj,'show_values',False):
                    text='%1.1f'%v[index]
                    cr.set_font_size(14)

                    fa,fd,fh,fxa,fya=cr.font_extents()

                    xb,yb,w,h,xa,ya=cr.text_extents(text)

                    if v[index]<0.1: color=(1.0,1.0,1.0)
                    else: color=(0,0,0)

                    cr.set_source_rgb(*color)
                    cr.move_to(x+i*size+size/2+0.5-xb-w/2,y+j*size+size/2+0.5-fd+fh/2)
                    cr.show_text(text)




class CairoDisplay(gtk.DrawingArea):
    def __init__(self,obj,width=640,height=480,title=None):
        gtk.DrawingArea.__init__(self)
        if title is None: title=obj.__class__.__name__
        self.obj=obj
        self.title=title
        self.paused=False
        self.skipped_frame=False
        self.rate=1.0

        self.app_window = gtk.Window()
        self.show()
        self.app_window.add(self)
        self.app_window.present()
        self.app_window.resize(width,height)
        self.app_window.connect('key_press_event',self.on_key_press)
        self.app_window.connect("delete-event", lambda widget,event,self=self: self.obj.stop())

        obj._get_scheduler().add(self.render_loop)


    def update_title(self):
        rateinfo=''
        if self.rate!=1.0: rateinfo='[%1.3fx]'%self.rate
        self.app_window.set_title('%s t:%1.3f%s'%(self.title,self.obj.now(),rateinfo))



    __gsignals__ = { "expose-event": "override" }
    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y,event.area.width, event.area.height)
        cr.clip()
        self.draw(cr, *self.window.get_size())

    def draw(self, cr, width, height):
        render_area(self.obj,cr,width,height)



    def on_key_press(self,widget,event):
        key=gtk.gdk.keyval_name(event.keyval)
        if key=='Page_Up':
            self.rate*=1.1
        elif key=='Page_Down':
            self.rate/=1.1
        elif key=='Pause':
            self.paused=not self.paused
        elif key=='Print':
            self.save_frame()
        elif key=='Escape':
            self.obj.stop()
        else:
            if hasattr(self.obj,'key_pressed'):
                self.obj.key_pressed(key)
            return False
        return True

    def render_loop(self):
        obj=self.obj
        dt=0.01
        while True:
            next_time=time.time()+dt
            yield dt*self.rate
            self.queue_draw()
            while gtk.events_pending(): gtk.main_iteration(False)

            if time.time()>next_time and obj.now()>dt:
                self.skipped_frame=True
            while self.paused or time.time()<next_time:
                while gtk.events_pending(): gtk.main_iteration(False)
            self.update_title()


    saved_frame_counter=0
    def save_frame(self,name=None,num=None,size=None):
        if name is None: name=self.title
        if size is None: size=self.window.get_size()
        if num is None:
            num=self.saved_frame_counter
            self.saved_frame_counter+=1

        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,*size)
        cr=cairo.Context(surface)
        self.draw(cr,*size)
        surface.write_to_png("%s%04d.png"%(name,num))

    def save_frame_eps(self,name=None,num=None,size=None):
        if name is None: name=self.title
        if size is None: size=self.window.get_size()
        if num is None:
            num=self.saved_frame_counter
            self.saved_frame_counter+=1

        surface=cairo.PSSurface("%s%04d.eps"%(name,num),size[0],size[1])
        surface.set_eps(True)
        cr=cairo.Context(surface)
        self.draw(cr,*size)
        surface.write_to_png("%s%04d.png"%(name,num))






