import ccm
log=ccm.log(html=True)

class Environment(ccm.Model):    
    def start(self):
        self.message=None
        yield 1
        for item in ['blue','cat','red','dog','blue','cat','red','dog']:
            self.message=item
            x=self.now()
            yield self.say     # wait until something is said
            log.rt=self.now()-x
            yield 0.1
            self.message=None
            yield 0.25

    def say(self,word):
        self.said_word=word        


from ccm.lib.actr import *
class AssociativeModel(ACTR):
    goal=Buffer()
    imaginal=Buffer()

    retrieval=Buffer()
    memory=Memory(retrieval,threshold=0)
    DMBaseLevel(memory)
    DMAssociate(memory,imaginal,weight=0.1)

    def init():
        memory.add('child cat kitten',baselevel=1)
        memory.add('child dog puppy',baselevel=1)
        goal.set('read')

        
    def read_word(goal='read',top='message:?word!None'):
        goal.set('respond ?word')

    def get_response(goal='respond ?word',memory='busy:False'):
        memory.request('child ?word ?')
        goal.set('say ?word')

    def say_response(goal='say ?word',retrieval='child ?word ?word2'):
        self.parent.say(word2)
        goal.set('imagine')

    def say_response_fail(goal='say',memory='error:True'):
        self.parent.say('unknown')
        goal.set('imagine')

    def imagine(goal='imagine',top='message:?word!None'):
        imaginal.set(word)
        goal.set('wait')

    def wait(goal='wait',top='message:None'):
        goal.set('read')



e=Environment()
e.model=AssociativeModel()
ccm.log_everything(e)

e.run()
ccm.finished()
        
        
        
        
    
