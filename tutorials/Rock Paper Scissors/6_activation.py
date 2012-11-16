import ccm
log=ccm.log()

class RPSChoice(ccm.Model):
    choice=None
    font='Arial 20'
    waiting=True

    def start(self):
        self.visible=True
        self.text=self.instructions
    
    def choose(self,option):
        if not self.waiting: return
        if option not in ['rock','paper','scissors']: return
        self.choice=option
        self.visible=False
        self.waiting=False

        # check to see if both players have made a choice
        if self.parent.choice1.choice is not None and self.parent.choice2.choice is not None:
            self.parent.determine_winner()            

    def reset(self):
        self.text=self.instructions
        self.waiting=True
        self.visible=True
        self.choice=None


class RockPaperScissors(ccm.Model):
    choice1=RPSChoice(x=0.5,y=0.2,instructions='Choose: Rock(1) Paper(2) Scissors(3)')
    choice2=RPSChoice(x=0.5,y=0.8,instructions='Choose: Rock(Z) Paper(X) Scissors(C)')

    result=ccm.Model(x=0.5,y=0.5,visible=False)

    score1=ccm.Model(text=0,x=0.9,y=0.1)
    score2=ccm.Model(text=0,x=0.9,y=0.9)

    trials=0

    def key_pressed(self,key):
        if key=='1': self.choice1.choose('rock')
        if key=='2': self.choice1.choose('paper')
        if key=='3': self.choice1.choose('scissors')
        
        if key=='z': self.choice2.choose('rock')
        if key=='x': self.choice2.choose('paper')
        if key=='c': self.choice2.choose('scissors')

    def determine_winner(self):
        self.choice1.text=self.choice1.choice
        self.choice2.text=self.choice2.choice
        self.choice1.visible=True
        self.choice2.visible=True

        c1=self.choice1.choice
        c2=self.choice2.choice
        self.choice1.opponent=c2
        self.choice2.opponent=c1
        if c1==c2:
            self.result.text="Tie!"
            self.choice1.state='tie'
            self.choice2.state='tie'
        elif (c1=='rock' and c2=='scissors') or (c1=='paper' and c2=='rock') or (c1=='scissors' and c2=='paper'):
            self.result.text="Player 1 wins!"
            self.score1.text+=1
            self.choice1.state='win'
            self.choice2.state='loss'
        else:
            self.result.text="Player 2 wins!"
            self.score2.text+=1
            self.choice2.state='win'
            self.choice1.state='loss'
            
        self.result.visible=True
            

        yield 1
        self.choice1.state=None
        self.choice2.state=None        

        self.result.visible=False
        
        self.choice1.reset()
        self.choice2.reset()

        self.trials+=1
        if self.trials>=100:
            log.score1=self.score1.text
            log.score2=self.score2.text
            self.stop()
        

from ccm.lib.actr import *
class MemoryPlayer(ACTR):
    goal=Buffer()
    goal.set('play rps')

    retrieval=Buffer()
    memory=Memory(retrieval)
    baselevel=DMBaseLevel(memory)

    def start_recall(goal='play rps',choice='waiting:True'):
        goal.set('recall')
        memory.request('history ?')
    def recall_fail_p(goal='recall',memory='error:True'):
        goal.set('choose paper')
    def recall_fail_r(goal='recall',memory='error:True'):
        goal.set('choose rock')
    def recall_fail_s(goal='recall',memory='error:True'):
        goal.set('choose scissors')

    def recall_success_r(goal='recall',retrieval='history rock'):
        goal.set('choose paper')
    def recall_success_p(goal='recall',retrieval='history paper'):
        goal.set('choose scissors')
    def recall_success_s(goal='recall',retrieval='history scissors'):
        goal.set('choose rock')

    def choose(goal='choose ?option'):
        choice.choose(option)
        goal.set('check response')

    def check_response(goal='check response',choice='opponent:?choice visible:True'):
        memory.add('history ?choice')
        retrieval.clear()
        goal.set('play rps')


env=RockPaperScissors()
env.model1=MemoryPlayer()
env.model1.choice=env.choice1

ccm.display(env)
env.run()

    
