import pygame

def get_value(obj,attr,default=None):
    x=getattr(obj,attr,default)
    if callable(x): x=x()
    return x

class DefaultRenderer:
    def __init__(self,obj,screen):
        self.obj=obj
        self.image=None
        
        self.text=''
        self.text_color=None
        self.text_color_tuple=(0,0,0)
        self.font_name=None
        
        self.render(screen)


    def get_font(self,name,screen):
        bold=False
        italics=False
        size=30
        font=[]
        for n in name.split():
            if n.lower()=='bold': bold=True
            elif n.lower()=='italics': italics=True
            elif len(n)==0: continue
            elif n[0] in '0123456789.': 
              if '.' in n: size=int(screen.get_height()*float(n))
              else: size=int(n)
            else: font.append(n)
        f=pygame.font.SysFont(' '.join(font),size,bold,italics)
        return f
        

    def render(self,screen):
        visible=get_value(self.obj,'visible',True)
        x=get_value(self.obj,'x')
        y=get_value(self.obj,'y')

        if not visible or x is None or y is None:
            return

        font=get_value(self.obj,'font')
        if font is None: font='Arial 30'

        text=get_value(self.obj,'text')
        if text is None: return
        if not type(text)==str: text=str(text)

        text_color=get_value(self.obj,'color')

        if self.image is None or text!=self.text or text_color!=self.text_color or font!=self.font_name:

            if font!=self.font_name:
                self.font=self.get_font(font,screen)
                self.font_name=font

            if text_color!=self.text_color:
                self.text_color=text_color
                if text_color is None: text_color='black'
                self.text_color_tuple=pygame.color.Color(text_color)
                
            self.image=self.font.render(text,True,self.text_color_tuple)


        if type(x) is float:
            x=int(x*int(screen.get_width()))
        if type(y) is float:
            y=int(y*int(screen.get_height()))
        rect=self.image.get_rect()
        rect.left=x-rect.width/2
        rect.top=y-rect.height/2

        screen.blit(self.image,rect)
        
