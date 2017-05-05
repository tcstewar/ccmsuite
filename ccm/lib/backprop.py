# Back-Propagation Neural Networks
#
# Based on Neil Schemenauer's bpnn.py

import math
import random

# calculate a random number where:  a <= rand < b
def rand(a, b):
    return (b-a)*random.random() + a

# Make a matrix (we could use NumPy to speed this up)
def makeMatrix(I, J, fill=0.0):
    m = []
    for i in range(I):
        m.append([fill]*J)
    return m

# our sigmoid function, tanh is a little nicer than the standard 1/(1+e^-x)
def sigmoid(x):
    return math.tanh(x)

# derivative of our sigmoid function (note that this uses y, not x)
def dsigmoid(y):
    return 1.0-y*y

class NN:
    def __init__(self, ni, nh, no):
        # number of input, hidden, and output nodes
        self.ni = ni + 1 # +1 for bias node
        self.nh = nh
        self.no = no

        # activations for nodes
        self.ai = [1.0]*self.ni
        self.ah = [1.0]*self.nh
        self.ao = [1.0]*self.no

        # create weights
        self.wi = makeMatrix(self.ni, self.nh)
        self.wo = makeMatrix(self.nh, self.no)
        # set them to random vaules
        for i in range(self.ni):
            for j in range(self.nh):
                self.wi[i][j] = rand(-2.0, 2.0)
        for j in range(self.nh):
            for k in range(self.no):
                self.wo[j][k] = rand(-2.0, 2.0)

        # last change in weights for momentum
        self.ci = makeMatrix(self.ni, self.nh)
        self.co = makeMatrix(self.nh, self.no)

        self.epochs=0

    def update(self, inputs):
        if len(inputs) != self.ni-1:
            raise ValueError('wrong number of inputs')

        # input activations
        for i in range(self.ni-1):
            #self.ai[i] = sigmoid(inputs[i])
            self.ai[i] = inputs[i]

        # hidden activations
        for j in range(self.nh):
            sum = 0.0
            for i in range(self.ni):
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = sigmoid(sum)

        # output activations
        for k in range(self.no):
            sum = 0.0
            for j in range(self.nh):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = sigmoid(sum)

    def backPropagate(self, targets, N, M):
        if len(targets) != self.no:
            raise ValueError('wrong number of target values')

        # calculate error terms for output
        output_deltas = [0.0] * self.no
        for k in range(self.no):
            error = targets[k]-self.ao[k]
            output_deltas[k] = dsigmoid(self.ao[k]) * error

        # calculate error terms for hidden
        hidden_deltas = [0.0] * self.nh
        for j in range(self.nh):
            error = 0.0
            for k in range(self.no):
                error = error + output_deltas[k]*self.wo[j][k]
            hidden_deltas[j] = dsigmoid(self.ah[j]) * error

        # update output weights
        for j in range(self.nh):
            for k in range(self.no):
                change = output_deltas[k]*self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N*change + M*self.co[j][k]
                self.co[j][k] = change
                #print N*change, M*self.co[j][k]

        # update input weights
        for i in range(self.ni):
            for j in range(self.nh):
                change = hidden_deltas[j]*self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N*change + M*self.ci[i][j]
                self.ci[i][j] = change

    def calcError(self,targets):
        error = 0.0
        for k in range(len(targets)):
            error = error + (targets[k]-self.ao[k])**2
        return math.sqrt(error/len(targets))


    def testOne(self,input,target):
      self.update(input)
      error=self.calcError(target)
      return error,self.ao[:]

    def testAll(self,patterns):
      error=0.0
      outputs=[]
      for input,target in patterns:
        e,o=self.testOne(input,target)
        error+=e*e
        outputs.append(o)
      return math.sqrt(error/len(patterns)),outputs


    def trainOne(self,input,target,learningRate=0.2,momentum=0):
      self.update(input)
      self.backPropagate(target,learningRate,momentum)
      error=self.calcError(target)
      return error

    def trainAll(self,patterns,learningRate=0.2,momentum=0):
      error = 0.0
      pat2=list(patterns)
      random.shuffle(pat2)
      for input,target in pat2:
        error+=self.trainOne(input,target,learningRate,momentum)
      self.epochs+=1
      return error/len(patterns)



    def confusionMatrix(self,patterns):
      categories=len(patterns[0][1])
      m=[[0 for i in range(categories)] for j in range(categories)]
      for input,target in patterns:
        error,output=self.testOne(input,target)
        correct=target.index(max(target))
        predict=output.index(max(output))
        m[correct][predict]+=1
      return m


