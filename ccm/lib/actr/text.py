import ccm

class TextOutput(ccm.Model):
    def write(self,text):
        print(text)
        self.log._=text
