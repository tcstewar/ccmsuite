import Tkinter

def get_value(obj,attr,default=None):
    x=getattr(obj,attr,default)
    if callable(x): x=x()
    return x

class DefaultRenderer:
    def __init__(self,obj,canvas):
        self.obj=obj
        self.text_widget=canvas.create_text((100,100),fill='black',font='Arial 30',justify='center')
        
        self.visible=True
        self.position=100,100
        self.text=''
        self.text_color='black'
        self.font='Arial 30'
        self.image=None
        self.image_widget=None
        
        self.render(canvas)

    def parse_font(self,font,total_height):
        f=[]
        for n in font.split():
            if len(n)==0: continue
            elif n[0] in '0123456789.':
              if '.' in n:
                  n=str(int(total_height*float(n)))
            f.append(n)
        return ' '.join(f)

    def render(self,canvas):
        visible=get_value(self.obj,'visible',True)
        x=get_value(self.obj,'x')
        y=get_value(self.obj,'y')

        if not visible or x is None or y is None:
            if self.visible:
                canvas.itemconfig(self.text_widget,state='hidden')
                if self.image_widget is not None:
                    canvas.itemconfig(self.image_widget,state='hidden')
                
                self.visible=False
        else:
            if not self.visible:
                canvas.itemconfig(self.text_widget,state='normal')
                if self.image_widget is not None:
                    canvas.itemconfig(self.image_widget,state='normal')
                self.visible=True

            if type(x) is float:
                x=int(x*int(canvas['width']))
            if type(y) is float:
                y=int(y*int(canvas['height']))
            if self.position!=(x,y):                
                canvas.move(self.text_widget,x-self.position[0],y-self.position[1])
                if self.image_widget is not None:
                    canvas.move(self.image_widget,x-self.position[0],y-self.position[1])
                self.position=x,y

            changes={}                
            color=get_value(self.obj,'color')
            if color is not None and color!=self.text_color:
                changes['fill']=color
                self.text_color=color
            text=get_value(self.obj,'text')
            if text!=self.text:
                changes['text']=text
                self.text=text
            font=get_value(self.obj,'font')
            if font is not None and font!=self.font:
                changes['font']=self.parse_font(font,int(canvas['height']))
                self.font=font

            canvas.itemconfig(self.text_widget,changes)
            
            image=get_value(self.obj,'image')
            if image!=self.image:
                if self.image_widget is not None:
                    canvas.delete(self.image_widget)
                if image is not None:
                    if not image.endswith('.gif'):
                        from PIL import Image, ImageTk
                        self.img=ImageTk.PhotoImage(Image.open(image))
                    else:    
                        self.img=Tkinter.PhotoImage(file=image)
                    self.image_widget=canvas.create_image(x,y,image=self.img,anchor=Tkinter.CENTER)    
                    canvas.tag_lower(self.image_widget)
                self.image=image    
        
        
        
