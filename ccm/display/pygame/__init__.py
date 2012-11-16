from ccm.lib import grid
#from ccm.disp.tk.cellular import CellularRenderer
from ccm.display.pygame.default import DefaultRenderer

def render(obj,screen):
    try:
        obj._display.render(screen)
    except AttributeError:
        if isinstance(obj,grid.World):
            obj._display=DefaultRenderer(obj,screen)
            #obj._display=CellularRenderer(obj,screen)
        else:
            obj._display=DefaultRenderer(obj,screen)
    for c in obj.get_children():
        render(c,screen)
        
