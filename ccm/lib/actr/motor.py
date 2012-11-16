import ccm

class Motor(ccm.Model):
  def __init__(self):
    ccm.Model.__init__(self)
    self.busy=False

  def press(self,key):
    if self.busy: return
    self.busy=True
    self.log._='Pressing key preparation'
    yield 0.25
    self.log._='Pressing key preparation complete'
    yield 0.05
    self.log._='Pressing key initiation complete'
    yield 0.1
    self.log._='Actually pressing the key'
    self.parent.parent.key_pressed(key)
    self.log._='Finishing movement'
    yield 0.15
    self.log._='Finished movement'
    self.busy=False

