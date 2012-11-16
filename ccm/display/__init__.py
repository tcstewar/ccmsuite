engines=dict(tk='ccm.display.tk.core.TkinterDisplay',
             cairo='ccm.display.cairo.core.CairoDisplay',
             pygame='ccm.display.pygame.core.PygameDisplay',
             )

default_order=['tk','pygame']


def display(root,engine=None,**args):
    d=None
    error=""

    order=default_order[:]
    if engine is not None and engine in order:
        order=[engine]
    
    for e in order:
        module,obj=engines[e].rsplit('.',1)
        try:
            m=__import__(module,globals(),locals(),[obj])
            d=getattr(m,obj)(root,**args)
            return d
        except ImportError,e:
            error+='\n'+str(engines[e])
        
    print 'Error: could not create display: %s'%error
