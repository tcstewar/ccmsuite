import backprop
import random


nn = backprop.NN(1, 10, 1)

def make_data():
    p = random.random()
    data = [[[-1], [1 if 0<=p<0.2 else 0]],
            [[-.33], [1 if 0.2<=p<0.6 else 0]],
            [[.33], [1 if 0.6<=p<0.7 else 0]],
            [[1], [1 if 0.7<=p else 0]],
            ]
    return data

for i in range(10000):
    #print make_data()
    print(i, nn.trainAll(make_data(), learningRate=0.005))

for x in [[-1], [-.33], [.33], [1]]:
    print(nn.testOne(x, [0])[1])
